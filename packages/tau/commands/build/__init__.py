"""
@file
@author John C. Linford (jlinford@paratools.com)
@version 1.0

@brief

This file is part of the TAU Performance System

@section COPYRIGHT

Copyright (c) 2013, ParaTools, Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:
 (1) Redistributions of source code must retain the above copyright notice, 
     this list of conditions and the following disclaimer.
 (2) Redistributions in binary form must reproduce the above copyright notice, 
     this list of conditions and the following disclaimer in the documentation 
     and/or other materials provided with the distribution.
 (3) Neither the name of ParaTools, Inc. nor the names of its contributors may 
     be used to endorse or promote products derived from this software without 
     specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# System modules
import os
import sys
import subprocess
from pkgutil import walk_packages
from textwrap import dedent

# TAU modules
from logger import getLogger
from arguments import args.getParser, REMAINDER
from commands import commands.getCommandsHelp, commands.executeCommand
from cf import tau
from cf.compiler import COMPILERS
from model.experiment import Experiment


LOGGER = logger.getLogger(__name__)

_name_parts = __name__.split('.')[1:]
COMMAND = ' '.join(['tau'] + _name_parts)


def _compilersHelp():
  parts = ['  %s  %s' % ('{:<15}'.format(comp.cmd), comp.short_descr) 
           for comp in COMPILERS.itervalues()]
  parts.sort()
  return '\n'.join(parts)

def isKnownCompiler(cmd):
  """
  Returns True if cmd is a known compiler command
  """
  known = COMPILERS.keys()
#   known.extend([n for _, n, _ in 
#                 walk_packages(sys.modules[__name__].__path__)])
  return cmd in known


SHORT_DESCRIPTION = "Instrument programs during compilation and/or linking."

USAGE = """
  %(command)s <command> [args ...]
  %(command)s -h | --help 
""" % {'command': COMMAND}

HELP = """
'%(command)s' page to be written.
""" % {'command': COMMAND}

USAGE_EPILOG = """
compiler commands:
%(simple_descr)s
%(command_descr)s
""" % {'simple_descr': _compilersHelp(), 
       'command_descr': commands.getCommandsHelp(__name__)}


_arguments = [ (('cmd',), {'help': "Compiler or linker command, e.g. 'gcc'",
                           'metavar': '<command>'}),
               (('cmd_args',), {'help': "Compiler arguments",
                                'metavar': 'args',
                                'nargs': REMAINDER})]
PARSER = args.getParser(_arguments,
                   prog=COMMAND,
                   usage=USAGE, 
                   description=SHORT_DESCRIPTION,
                   epilog=USAGE_EPILOG)

def getUsage():
  return PARSER.format_help() 


def getHelp():
  return HELP


def main(argv):
  """
  Program entry point
  """
  args = PARSER.parse_args(args=argv)
  LOGGER.debug('Arguments: %s' % args)
  
  cmd = args.cmd
  cmd_args = args.cmd_args
  
  selected = Experiment.getSelected()
  selected.populate()
  
  
  
  if cmd in COMPILERS:
   
    # Compile the project if needed
    proj.compile()
   
    # Set the environment
    env = proj.getTauCompilerEnvironment()
   
    # Get compiler flags
    flags = proj.getTauCompilerFlags()
     
    # Execute the compiler wrapper script
    if cmd_args:
        cmd = [SIMPLE_COMPILERS[compiler].tau_cmd] + flags + cmd_args
    else:
        cmd = [SIMPLE_COMPILERS[compiler].cmd]
         
    LOGGER.debug('Creating subprocess: cmd=%r, env=%r' % (cmd, env))
    LOGGER.info('\n'.join(['%s=%s' % i for i in env.iteritems() if i[0].startswith('TAU')]))
    LOGGER.info(' '.join(cmd))
    proc = subprocess.Popen(cmd, env=env, stdout=sys.stdout, stderr=sys.stderr)
    return proc.wait()

  # Execute as a tau command
  return commands.executeCommand(_name_parts + [cmd], cmd_args)