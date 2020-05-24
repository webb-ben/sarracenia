#!/usr/bin/env python3

#
# This file is part of sarracenia.
# The sarracenia suite is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Shared Services Canada, 2020
#


import copy
import importlib
import logging


from abc import ABCMeta, abstractmethod



logger = logging.getLogger( __name__ )

"""
1st draft of a v03 plugin method.

__init__ accepts options as an argument.

options is a dictionary of settings, used to override default behaviour

a setting is declared:

set sarra.plugin.msg.log.Log.level debug

the plugin should get the setting:

    options.level = 'debug'


worklist given to on_plugins...

    worklist.incoming --> new messages to continue processing
    worklist.ok       --> successfully processed
    worklist.rejected --> messages to not be further processed.
    worklist.retry    --> messages for which processing failed.


Initially all messages are placed in incoming.
if a plugin decides:

- a message is not relevant, it is moved to rejected.
- all processing has been done, it moves it to ok.
- an operation failed and it should be retried later, move to retry

if a
Do not remove from all lists, only move messages between them.
   it is necessary to put rejected messages in the appropriate worklist
   so they can be acknowledged as received.

"""

entry_points = [ 'do_download', 'do_get', 'do_poll', 'do_put', 'do_send',
   'on_messages', 'on_data', 'on_files', 'on_housekeeping', 'on_html_page', 
   'on_line', 'on_part', 'on_post', 'on_report', 'on_start', 'on_stop', 
   'on_watch' ]


class Plugin:
    """
    FIXME: document the API signatures for all the entry points. 
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, options):
        self.o = options

        logging.basicConfig( format=self.o.logFormat, level=getattr(logging, self.o.logLevel.upper()) )

        logger.info( 'intializing %s' % self.name )
        pass

#    @abstractmethod
#    def name(self):
#        return __name__
#
#    @abstractmethod
#    def on_files(self,messages):
#        pass
#
#    @abstractmethod
#    def on_messages(self,messages):
#        pass
#
#    @abstractmethod
#    def do_download(self,messages): 
#        pass
#
#    @abstractmethod
#    def do_get(self,messages): 
#        pass
#
#    @abstractmethod
#    def do_poll(self): 
#        pass
#
#    @abstractmethod
#    def do_put(self): 
#        pass
#
#    @abstractmethod
#    def do_send(self):
#        pass
#
#    @abstractmethod
#    def on_data(self): 
#        pass
#
#    @abstractmethod
#    def on_files(self,worklist): 
#        pass
#
#    @abstractmethod
#    def on_housekeeping(self):
#        pass
#
#    @abstractmethod
#    def on_html_page(self): 
#        pass
#
#    @abstractmethod
#    def on_line(self): 
#        pass
#
#    @abstractmethod
#    def on_part(self): 
#        pass
#
#    @abstractmethod
#    def on_post(self): 
#        pass
#
#    @abstractmethod
#    def on_report(self): 
#        pass
#
#    @abstractmethod
#    def on_start(self): 
#        pass
#
#    @abstractmethod
#    def on_stop(self):
#        pass
#
#    @abstractmethod
#    def on_watch(self):
#        pass
#



def load_library(factory_path,options):

    logger.info( 'load_plugin: %s' % factory_path )
    packagename, classname = factory_path.rsplit('.', 1)
    module = importlib.import_module(packagename)
    class_ = getattr(module, classname)

    if hasattr(options,'settings'):
        opt = copy.deepcopy(options)
        # strip off the class prefix.
        if factory_path in options.settings:
            for s in options.settings[factory_path]:
                setattr(opt,s,options.settings[factory_path][s])
    else:
        opt=options

    plugin = class_(opt)
    return plugin

