#"""
#@file
#@author John C. Linford (jlinford@paratools.com)
#@version 1.0
#
#@brief
#
# This file is part of TAU Commander
#
#@section COPYRIGHT
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
#"""

from tau.error import InternalError
from tau.arguments import ParsePackagePathAction
from tau.controller import Controller, ByName
from tau.cf.target import Architecture, OperatingSystem
from tau.cf.target import host
from tau.cf.compiler import CC_ROLE, CXX_ROLE, FC_ROLE, UPC_ROLE, CompilerRole
from tau.cf.compiler.mpi import MPI_CC_ROLE, MPI_CXX_ROLE, MPI_FC_ROLE
from tau.cf.compiler.installed import InstalledCompilerSet 


class Target(Controller, ByName):

    """
    Target data model controller
    """

    attributes = {
        'projects': {
            'collection': 'Project',
            'via': 'targets',
            'description': 'projects using this target'
        },
        'name': {
            'type': 'string',
            'unique': True,
            'description': 'target configuration name',
            'argparse': {'metavar': '<target_name>'}
        },
        'host_os': {
            'type': 'string',
            'required': True,
            'description': 'host operating system',
            'default': host.operating_system().name,
            'argparse': {'flags': ('--host-os',),
                         'group': 'target system',
                         'metavar': '<os>',
                         'choices': OperatingSystem.keys()}
        }, 
        'host_arch': {
            'type': 'string',
            'required': True,
            'description': 'host architecture',
            'default': host.architecture().name,
            'argparse': {'flags': ('--host-arch',),
                         'group': 'target system',
                         'metavar': '<arch>',
                         'choices': Architecture.keys()}
        },
        # TODO: Get TAU to support a proper host/device model for offloading, etc.
#         'device_arch': {
#             'type': 'string',
#             'description': 'coprocessor architecture',
#             'default': None,
#             'argparse': {'flags': ('--device-arch',),
#                          'group': 'target system',
#                          'metavar': 'arch'}
#         },
        CC_ROLE.keyword: {
            'model': 'Compiler',
            'required': CC_ROLE.required,
            'description': '%s compiler command' % CC_ROLE.language,
            'argparse': {'flags': ('--cc',),
                         'group': 'compiler',
                         'metavar': '<command>'}
        },
        CXX_ROLE.keyword: {
            'model': 'Compiler',
            'required': CXX_ROLE.required,
            'description': '%s compiler command' % CXX_ROLE.language,
            'argparse': {'flags': ('--cxx',),
                         'group': 'compiler',
                         'metavar': '<command>'}
        },
        FC_ROLE.keyword: {
            'model': 'Compiler',
            'required': FC_ROLE.required,
            'description': '%s compiler command' % FC_ROLE.language,
            'argparse': {'flags': ('--fc',),
                         'group': 'compiler',
                         'metavar': '<command>'}
        },
        UPC_ROLE.keyword: {
            'model': 'Compiler',
            'required': UPC_ROLE.required,
            'description': '%s compiler command' % UPC_ROLE.language,
            'argparse': {'flags': ('--upc',),
                         'group': 'Universal Parallel C',
                         'metavar': '<command>'}
        },
        MPI_CC_ROLE.keyword: {
            'model': 'Compiler',
            'required': MPI_CC_ROLE.required,
            'description': '%s compiler command' % MPI_CC_ROLE.language,
            'argparse': {'flags': ('--mpi-cc',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<command>'}
        },
        MPI_CXX_ROLE.keyword: {
            'model': 'Compiler',
            'required': MPI_CXX_ROLE.required,
            'description': '%s compiler command' % MPI_CXX_ROLE.language,
            'argparse': {'flags': ('--mpi-cxx',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<command>'}
        },
        MPI_FC_ROLE.keyword: {
            'model': 'Compiler',
            'required': MPI_FC_ROLE.required,
            'description': '%s compiler command' % MPI_FC_ROLE.language,
            'argparse': {'flags': ('--mpi-fc',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<command>'}
        },
        'mpi_include_paths': {
            'type': 'array',
            'description': 'paths to search for MPI header files when building MPI applications',
            'argparse': {'flags': ('--mpi-include-paths',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<path>',
                         'nargs': '+',
                         'action': ParsePackagePathAction},
        },
        'mpi_library_paths': {
            'type': 'array',
            'description': 'paths to search for MPI library files when building MPI applications',
            'argparse': {'flags': ('--mpi-library-paths',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<path>',
                         'nargs': '+',
                         'action': ParsePackagePathAction},
        },
        'mpi_linker_flags': {
            'type': 'array',
            'description': 'additional linker flags required to build MPI applications',
            'argparse': {'flags': ('--mpi-linker-flags',),
                         'group': 'Message Passing Interface (MPI)',
                         'metavar': '<flag>',
                         'nargs': '+'},
        },
        'cuda': {
            'type': 'string',
            'description': 'path to NVIDIA CUDA installation',
            'argparse': {'flags': ('--cuda',),
                         'group': 'software package',
                         'metavar': '<path>',
                         'action': ParsePackagePathAction},
        },
        'tau_source': {
            'type': 'string',
            'description': 'path or URL to a TAU installation or archive file',
            'default': 'download',
            'argparse': {'flags': ('--tau',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download)',
                         'action': ParsePackagePathAction}
        },
        'pdt_source': {
            'type': 'string',
            'description': 'path or URL to a PDT installation or archive file',
            'default': 'download',
            'argparse': {'flags': ('--pdt',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|None)',
                         'action': ParsePackagePathAction},
        },
        'binutils_source': {
            'type': 'string',
            'description': 'path or URL to a GNU binutils installation or archive file',
            'default': 'download',
            'argparse': {'flags': ('--binutils',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|None)',
                         'action': ParsePackagePathAction}
        },
        'libunwind_source': {
            'type': 'string',
            'description': 'path or URL to a libunwind installation or archive file',
            'default': 'download',
            'argparse': {'flags': ('--libunwind',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|None)',
                         'action': ParsePackagePathAction}
        },
        'papi_source': {
            'type': 'string',
            'description': 'path or URL to a PAPI installation or archive file',
            'argparse': {'flags': ('--papi',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|None)',
                         'action': ParsePackagePathAction}
        },
        'score-p_source': {
            'type': 'string',
            'description': 'path or URL to a Score-P installation or archive file',
            'argparse': {'flags': ('--score-p',),
                         'group': 'software package',
                         'metavar': '(<path>|<url>|download|None)',
                         'action': ParsePackagePathAction}
        }
    }

    def compilers(self):
        """Get Compiler objects for all compilers in this Target.
         
        Returns:
            A CompilerSet with all required compilers set.
        """
        eids = []
        compilers = {}
        for role in CompilerRole.all():
            try:
                compiler_command = self.populate(role.keyword)
            except KeyError:
                continue
            compilers[role.keyword] = compiler_command.info()
            eids.append(compiler_command.eid)
        missing = [role.keyword for role in CompilerRole.required() if role.keyword not in compilers]
        if missing:
            raise InternalError("Target '%s' is missing required compilers: %s" % (self['name'], missing))
        return InstalledCompilerSet('_'.join(map(str, eids)), **compilers)
