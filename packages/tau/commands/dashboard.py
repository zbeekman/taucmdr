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

# TAU modules
import settings
from tau import EXIT_SUCCESS
from logger import getLogger, LINE_WIDTH
from error import InternalError
from arguments import args.getParser
from commands import commands.executeCommand
from model.experiment import Experiment

LOGGER = logger.getLogger(__name__)

_name_parts = __name__.split('.')[2:]
COMMAND = ' '.join(['tau'] + _name_parts)

SHORT_DESCRIPTION = "Show all projects and their components."

USAGE = """
  %(command)s {<command>|<file_name>}
  %(command)s -h | --help
""" % {'command': COMMAND}

HELP = """
Help page to be written.
"""

PARSER = args.getParser([],
                   prog=COMMAND, 
                   usage=USAGE, 
                   description=SHORT_DESCRIPTION)


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
  
  commands.executeCommand(['target', 'list'])
  commands.executeCommand(['application', 'list'])
  commands.executeCommand(['measurement', 'list'])
  commands.executeCommand(['project', 'list'])
  
  title = '{:=<{}}'.format('== Selected Experiment ==', LINE_WIDTH)
  experiment = Experiment.getSelected()
  LOGGER.debug("Found experiment %r" % experiment)
  if experiment:
    experiment.populate()
    target = experiment['target']
    application = experiment['application']
    measurement = experiment['measurement']
    msg = "Application '%s' on target '%s' measured by '%s'" % \
          (application['name'], target['name'], measurement['name'])
  else:
    msg = "No experiment selected. See `tau project select --help`"
  LOGGER.info('\n'.join([title, '', msg, '']))  
  
  return EXIT_SUCCESS