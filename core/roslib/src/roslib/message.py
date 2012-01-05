# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Revision $Id$

"""
Support library for Python autogenerated message files. This defines
the Message base class used by genmsg_py as well as support
libraries for type checking and retrieving message classes by type
name.
"""

import os
import sys

import roslib.names

import genpy

# forward a bunch of old symbols from genmsg for backwards compat
from genmsg.message import check_type, strify_message
from genpy import Message, DeserializationError, SerializationError, \
     Time, Duration, TVal
from genpy.message import get_printable_message_args, fill_message_args

def _get_message_or_service_class(type_str, message_type, reload_on_error=False):
    """
    Utility for retrieving message/service class instances. Used by
    get_message_class and get_service_class. 
    :param type_str: 'msg' or 'srv', ``str``
    :param message_type: type name of message/service, ``str``
    :returns: Message/Service  for message/service type or None, ``class``
    :raises: :exc:`ValueError` If message_type is invalidly specified
    """
    ## parse package and local type name for import
    package, base_type = roslib.names.package_resource_name(message_type)
    if not package:
        if base_type == 'Header':
            package = 'std_msgs'
        else:
            raise ValueError("message type is missing package name: %s"%str(message_type))
    pypkg = val = None
    try: 
        # import the package and return the class
        pypkg = __import__('%s.%s'%(package, type_str))
        val = getattr(getattr(pypkg, type_str), base_type)
    except roslib.packages.InvalidROSPkgException:
        val = None
    except ImportError:
        val = None
    except AttributeError:
        val = None

    # this logic is mainly to support rosh, so that a user doesn't
    # have to exit a shell just because a message wasn't built yet
    if val is None and reload_on_error:
        try:
            if pypkg:
                reload(pypkg)
            val = getattr(getattr(pypkg, type_str), base_type)
        except:
            val = None
    return val
        
## cache for get_message_class
_message_class_cache = {}

def get_message_class(message_type, reload_on_error=False):
    """
    Get the message class. NOTE: this function maintains a
    local cache of results to improve performance.
    :param message_type: type name of message, ``str``
    :param reload_on_error: (optional). Attempt to reload the Python
      module if unable to load message the first time. Defaults to
      False. This is necessary if messages are built after the first load.
    :returns: Message class for message/service type, ``Message class``
    :raises :exc:`ValueError`: if  message_type is invalidly specified
    """
    if message_type in _message_class_cache:
        return _message_class_cache[message_type]
    cls = _get_message_or_service_class('msg', message_type, reload_on_error=reload_on_error)
    if cls:
        _message_class_cache[message_type] = cls
    return cls

## cache for get_service_class
_service_class_cache = {}

def get_service_class(service_type, reload_on_error=False):
    """
    Get the service class. NOTE: this function maintains a
    local cache of results to improve performance.
    :param service_type: type name of service, ``str``
    :param reload_on_error: (optional). Attempt to reload the Python
      module if unable to load message the first time. Defaults to
      False. This is necessary if messages are built after the first load.
    :returns: Service class for service type, ``Service class``
    :raises :exc:`Exception` If service_type is invalidly specified
    """
    if service_type in _service_class_cache:
        return _service_class_cache[service_type]
    cls = _get_message_or_service_class('srv', service_type, reload_on_error=reload_on_error)
    _service_class_cache[service_type] = cls
    return cls

