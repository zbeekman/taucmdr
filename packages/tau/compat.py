#"""
#@file
#@author Srinath Vadlamani (srinathv@paratools.com)
#@version 1.0
#
#@brief
#
#This file is part of TAU Commander
#
#@section COPYRIGHT
#
#Copyright (c) 2015, ParaTools, Inc.
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
# (1) Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
# (2) Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
# (3) Neither the name of ParaTools, Inc. nor the names of its contributors may
#     be used to endorse or promote products derived from this software without
#     specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#"""

# TAU modules
import logger
import error
import models.target

#structure for requisite [first pass]
#want to redo this like:
Required = 1
NotRequired = 0
Recommended = 2

#want to grab an instance a target, measurement or application class and return dictionary of

def dictGen( component ) :
  """
  A function that takes in an instance of a component class and returns a dict
  with the appropiate keys for compatability.
  """

#compat_mat = {
#'source_inst': {'pdt_source': Required, 'bfd_source': NotRequired, 'libuwind': NotRequired,},
#'compiler_inst': {'pdt_source': NotRequired, 'bfd_source': Recommended, ...  },
#'binary_inst:':{
#'dynamic_inst':{


#packages = {
#'pdt_source': cf.pdt.Pdt,
#'bfd_source': cf.pdt.Bfd
#...
#}
#
#depends = set()
#
#for pkgkey, val in measurement:
#  try:
#    compat = compat_mat[pkgkey]
#  except KeyError:
#    continue
#  for key, val in compat:
#    try:
#      supplied = target[key]
#    except KeyError:
#      raise error.ConfigurationError("No value for %s was supplied" % key)
#    if (val == Required) and (util.parseBool(supplied) == False):
#      # Error, this is required
#    elif (val == Recommended) and (util.parseBool(supplied) == False):
#      LOGGER.warning("Hey, I really think you should use %s" % key
#    elif (val == NoRequired) and (util.parseBool(supplied) == True):
#      LOGGER.info("Hey, %s is not required but you're using it anyway")
#    else:
#      # Everything looks good
#      depnds.add((packages[key], key))
#
#tau = cf.tau.Tau(prefix, cc, cxx, fc, .... depnds, kwargs)

#we want a function that can be used in other modules (experiment.py) that looks like
# def check_compat(A,B,map)
#where A and B and objects with attributes that are traversed in the same way
# map is




