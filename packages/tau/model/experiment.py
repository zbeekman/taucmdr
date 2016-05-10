# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, ParaTools, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# (1) Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
# (2) Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
# (3) Neither the name of ParaTools, Inc. nor the names of its contributors may
#     be used to endorse or promote products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""Experiment data model.

An Experiment uniquely groups a :any:`Target`, :any:`Application`, and :any:`Measurement`
and will have zero or more :any:`Trial`. There is one selected experiment per project.  
The selected experiment will be used for application compilation and trial visualization. 
"""

import os
import shutil
from tau import logger, util
from tau.error import ConfigurationError
from tau.mvc.model import Model
from tau.model.trial import Trial
from tau.model.project import Project
from tau.storage.levels import PROJECT_STORAGE, STORAGE_LEVELS, ORDERED_LEVELS
from tau.cf.target import OperatingSystem, DARWIN_OS
from tau.cf.software import SoftwarePackageError
from tau.cf.software.tau_installation import TauInstallation
from tau.cf.compiler.installed import InstalledCompiler


LOGGER = logger.get_logger(__name__)


def attributes():   
    from tau.model.target import Target
    from tau.model.application import Application
    from tau.model.measurement import Measurement
    return {
        'project': {
            'model': Project,
            'required': True,
            'description': "Project this experiment belongs to"
        },
        'target': {
            'model': Target,
            'required': True,
            'description': "Target this experiment runs on"
        },
        'application': {
            'model': Application,
            'required': True,
            'description': "Application this experiment uses"
        },
        'measurement': {
            'model': Measurement,
            'required': True,
            'description': "Measurement parameters for this experiment"
        },
        'trials': {
            'collection': Trial,
            'via': 'experiment',
            'description': "Trials of this experiment"
        }
    }


class Experiment(Model):
    """Experiment data model."""
    
    __attributes__ = attributes

    def __init__(self, *args, **kwargs):
        super(Experiment, self).__init__(*args, **kwargs)
        
    @classmethod
    def controller(cls, storage=PROJECT_STORAGE):
        return cls.__controller__(cls, storage)
    
    def title(self):
        populated = self.populate()
        return '(%s, %s, %s)' % (populated['target']['name'],
                                 populated['application']['name'],
                                 populated['measurement']['name'])
        
    def data_size(self):
        return sum([int(trial.get('data_size', 0)) for trial in self.populate('trials')])

    @property
    def prefix(self):
        # pylint: disable=attribute-defined-outside-init
        try:
            return self._prefix
        except AttributeError: 
            populated = self.populate()
            self._prefix = os.path.join(populated['project'].prefix,
                                        populated['target']['name'],
                                        populated['application']['name'],
                                        populated['measurement']['name'])
            return self._prefix
        
    def on_create(self):
        try:
            util.mkdirp(self.prefix)
        except:
            raise ConfigurationError('Cannot create directory %r' % self.prefix,
                                     'Check that you have `write` access')

    def on_delete(self):
        # pylint: disable=broad-except
        try:
            util.rmtree(self.prefix)
        except Exception as err:
            if os.path.exists(self.prefix):
                LOGGER.error("Could not remove experiment data at '%s': %s", self.prefix, err)

    def next_trial_number(self):
        trials = self.populate('trials')
        for i, j in enumerate(sorted([trial['number'] for trial in trials])):
            if i != j:
                return i
        return len(trials)
    
    def uses_tau(self):
        # For now, all experiments use TAU
        # This might change if we ever re-use this for something like ThreadSpotter
        return True

    def uses_pdt(self):
        measurement = self.populate('measurement')
        return measurement['source_inst'] == 'automatic'
    
    def uses_binutils(self):
        measurement = self.populate('measurement')
        return (measurement['sample'] or 
                measurement['compiler_inst'] != 'never' or 
                measurement['openmp'] in ('ompt', 'gomp'))
        
    def uses_libunwind(self):
        populated = self.populate()
        host_os = OperatingSystem.find(populated['target']['host_os'])
        return (host_os is not DARWIN_OS and
                (populated['measurement']['sample'] or 
                 populated['measurement']['compiler_inst'] != 'never' or 
                 populated['application']['openmp']))
        
    def uses_papi(self):
        measurement = self.populate('measurement')
        return bool(len([met for met in measurement['metrics'] if 'PAPI' in met]))
    
    def configure_tau(self, prefix, dependencies):
        """Configures TAU for the current experiment, if necessary.
        
        Args:
            prefix (str): Filesystem prefix where TAU will be installed, if necessary.
            dependencies (dict): Installation objects indexed by dependency name.
            
        Returns:
            TauInstallation: Object handle for the TAU installation.
        """
        populated = self.populate()
        target = populated['target']
        application = populated['application']
        measurement = populated['measurement']
        verbose = (logger.LOG_LEVEL == 'DEBUG')
        tau_args = (target.get('tau_source', None), 
                    target['host_arch'], 
                    target['host_os'], 
                    target.compilers())
        tau_kwargs = dict(verbose=verbose,
                          # TAU dependencies
                          pdt=dependencies['pdt'],
                          binutils=dependencies['binutils'],
                          libunwind=dependencies['libunwind'],
                          papi=dependencies['papi'],
                          # TAU feature suppport
                          openmp_support=application['openmp'],
                          pthreads_support=application['pthreads'],
                          mpi_support=application['mpi'],
                          mpi_include_path=target.get('mpi_include_path', []),
                          mpi_library_path=target.get('mpi_library_path', []),
                          mpi_libraries=target.get('mpi_libraries', []),
                          cuda_support=application['cuda'],
                          cuda_prefix=target.get('cuda', None),
                          opencl_support=application['opencl'],
                          opencl_prefix=target.get('opencl', None),
                          shmem_support=application['shmem'],
                          mpc_support=application['mpc'],
                          # Instrumentation methods and options            
                          source_inst=measurement['source_inst'],
                          compiler_inst=measurement['compiler_inst'],
                          link_only=measurement['link_only'],
                          io_inst=measurement['io'],
                          keep_inst_files=measurement['keep_inst_files'],
                          reuse_inst_files=measurement['reuse_inst_files'],
                          select_inst_file=measurement.get('select_inst_file', None),
                          # Measurement methods and options
                          profile=measurement['profile'],
                          trace=measurement['trace'],
                          sample=measurement['sample'],
                          metrics=measurement['metrics'],
                          measure_mpi=measurement['mpi'],
                          measure_openmp=measurement['openmp'],
                          measure_opencl=measurement['opencl'],
                          measure_pthreads=None,  # TODO
                          measure_cuda=None,  # TODO
                          measure_shmem=None,  # TODO
                          measure_mpc=None,  # TODO
                          measure_heap_usage=measurement['heap_usage'],
                          measure_memory_alloc=measurement['memory_alloc'],
                          callpath_depth=measurement['callpath'])

        for storage in reversed(ORDERED_LEVELS):
            tau = TauInstallation(storage.prefix, *tau_args, **tau_kwargs)
            try:
                tau.verify()
            except SoftwarePackageError:
                # Not installed in this storage, but that's OK
                continue
            else:
                # Found installation
                return tau
        tau = TauInstallation(prefix, *tau_args, **tau_kwargs)
        with tau:
            tau.install()
            return tau

    def configure_tau_dependency(self, name, prefix):
        """Installs dependency packages for TAU, e.g. PDT.
        
        Args:
            name (str): Name of the dependency to install.  
                        Must have a matching tau.cf.software.<name>_installation module.
            prefix (str): Installation prefix.
        
        Returns:
            Installation: A new installation instance for the installed dependency.
        """
        target = self.populate('target')
        cls_name = name.title() + 'Installation'
        pkg = __import__('tau.cf.software.%s_installation' % name.lower(), globals(), locals(), [cls_name], -1)
        cls = getattr(pkg, cls_name)
        opts = (target.get(name + '_source', None), target['host_arch'], target['host_os'], target.compilers())
        for storage in reversed(ORDERED_LEVELS):
            inst = cls(storage.prefix, *opts)
            try:
                inst.verify()
            except SoftwarePackageError:
                # Not installed in this storage, but that's OK
                continue
            else:
                # Found installation
                return inst
        inst = cls(prefix, *opts)
        with inst:
            inst.install()
            return inst       

    def configure(self):
        """Sets up the Experiment for a new trial.
        
        Installs or configures TAU and all its dependencies.  After calling this 
        function, the experiment is ready to operate on the user's application.
        
        Returns:
            TauInstallation: Object handle for the TAU installation. 
        """
        project_data = self.populate('project')
        try:
            storage = STORAGE_LEVELS[project_data['storage_level']]
        except KeyError:
            # Install at highest writable storage level
            for storage in reversed(ORDERED_LEVELS):
                if storage.is_writable():
                    prefix = storage.prefix
                    break
            else:
                raise SoftwarePackageError("%s storage is not writable" % project_data['storage_level'])
        else:
            if not storage.is_writable():
                raise SoftwarePackageError("%s storage is not writable" % project_data['storage_level'])
            else:
                prefix = storage.prefix

        if self.uses_tau():
            dependencies = {}
            for name in 'pdt', 'binutils', 'libunwind', 'papi':
                uses_dependency = getattr(self, 'uses_' + name)
                inst = self.configure_tau_dependency(name, prefix) if uses_dependency() else None
                dependencies[name] = inst
            return self.configure_tau(prefix, dependencies)

    def managed_build(self, compiler_cmd, compiler_args):
        """Uses this experiment to perform a build operation.
        
        Checks that this experiment is compatible with the desired build operation,
        prepares the experiment, and performs the operation.
        
        Args:
            compiler_cmd (str): The compiler command intercepted by TAU Commander.
            compiler_args (list): Compiler command line arguments intercepted by TAU Commander.
            
        Raises:
            ConfigurationError: The experiment is not configured to perform the desired build.
        
        Returns:
            int: Build subprocess return code.
        """
        LOGGER.debug("Managed build: %s", [compiler_cmd] + compiler_args)
        target = self.populate('target')
        given_compiler = InstalledCompiler(compiler_cmd)
        target.check_compiler(given_compiler, compiler_args)
        
        tau = self.configure()
        return tau.compile(given_compiler, compiler_args)
        
    def managed_run(self, launcher_cmd, application_cmd):
        """Uses this experiment to run an application command.
        
        Performs all relevent system preparation tasks to run the user's application
        under the specified experimental configuration.
        
        Args:
            launcher_cmd (list): Application launcher with command line arguments.
            application_cmd (list): Application executable with command line arguments.

        Raises:
            ConfigurationError: The experiment is not configured to perform the desired run.
            
        Returns:
            int: Application subprocess return code.
        """
        command = util.which(application_cmd[0])
        if not command:
            raise ConfigurationError("Cannot find executable: %s" % application_cmd[0])
        tau = self.configure()
        cmd, env = tau.get_application_command(launcher_cmd, application_cmd)
        return Trial.controller(self.storage).perform(self, cmd, os.getcwd(), env)

    def show(self, profile_tool=None, trace_tool=None, trial_numbers=None):
        """Show experiment trial data.
        
        Shows the most recent trial or all trials with given numbers.
        
        Args:
            profile_tool (str): Name of the visualization or data processing tool for profiles, e.g. `pprof`.
            trace_tool (str): Name of the visualization or data processing tool for traces, e.g. `vampir`.
            trial_numbers (list): Numbers of trials to show.
            
        Raises:
            ConfigurationError: Invalid trial numbers or no trial data for this experiment.
        """
        if trial_numbers:
            trials = []
            for num in trial_numbers:
                found = Trial.controller(self.storage).one({'experiment': self.eid, 'number': num})
                if not found:
                    raise ConfigurationError("No trial number %d in experiment %s" % (num, self.name))
                trials.append(found)
        else:
            trials = self.populate('trials')
            if trials:
                found = trials[0]
                for trial in trials[1:]:
                    if trial['begin_time'] > found['begin_time']:
                        found = trial
                trials = [found]
        if not trials:
            raise ConfigurationError("No trials in experiment %s" % self.title(), "See `tau trial create --help`")

        tau = self.configure()
        meas = self.populate('measurement')
        for trial in trials:
            prefix = trial.prefix
            if meas['profile']:
                tau.show_profile(prefix, profile_tool)
            if meas['trace']:
                tau.show_trace(prefix, trace_tool)
                
    def export(self, export_location=None, profile_format=None, trial_numbers=None):
        """Export experiment trial data.
        
        Exports the most recent trial or all trials with given numbers.
        
        Args:
            export_location (str): Name of the visualization or data processing tool for profiles, e.g. `pprof`.
            profile_format (str): Name of the visualization or data processing tool for traces, e.g. `vampir`.
            trial_numbers (list): Numbers of trials to show.
            
        Raises:
            ConfigurationError: Invalid trial numbers or no trial data for this experiment.
        """
        if trial_numbers:
            trials = []
            for num in trial_numbers:
                found = Trial.controller(self.storage).one({'experiment': self.eid, 'number': num})
                if not found:
                    raise ConfigurationError("No trial number %d in experiment %s" % (num, self.name))
                trials.append(found)
        else:
            trials = self.populate('trials')
            if trials:
                found = trials[0]
                for trial in trials[1:]:
                    if trial['begin_time'] > found['begin_time']:
                        found = trial
                trials = [found]
        if not trials:
            raise ConfigurationError("No trials in experiment %s" % self.title(), "See `tau trial create --help`")

        tau = self.configure()
        meas = self.populate('measurement')
        for trial in trials:
            prefix = trial.prefix
            if profile_format == 'ppk':
                cmd = 'paraprof', '--pack', `trial['number']`+'.ppk', prefix
                retval = tau.pack_profile(cmd)
                if retval != 0:
                    raise ConfigurationError("paraprof failed to open '%s'" % prefix)
                if export_location is not None:
                    shutil.move(`trial['number']`+'.ppk', export_location)
            else:
                if export_location is None:
                    export_location = os.getcwd()
                if(os.path.exists(export_location)):
                    shutil.copytree(prefix,export_location+'/trial'+`trial['number']`)
                else:
                    shutil.copytree(prefix,export_location)
