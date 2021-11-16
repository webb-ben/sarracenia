#!/usr/bin/python3
"""
 Discard messages if they are too old, so that rather than downloading
 obsolete data, only current data will be retrieved.

 this should be used as an on_msg script. 
 For each announcement, check how old it is, and if it exceeds the threshold in the 
 routine, discard the message by returning False, after printing a local log message saying so.
 
 The message can be used to gauge whether the number of instances or internet link are sufficient
 to transfer the data selected.  if the lag keeps increasing, then likely instances should be 
 increased.

 It is mandatory to set the threshold for discarding messages (in seconds) in the configuration 
 file. For example:

 msg_skip_threshold 10

 will result in messages which are more than 10 seconds old being skipped. 

 default is one hour (3600 seconds.) 


"""
import calendar
import logging
import os
import stat
import time
from sarracenia import timestr2flt, nowflt
from sarracenia.flowcb import FlowCB
logger = logging.getLogger(__name__)


class Transformer(FlowCB):
    def __init__(self, options):
        self.o = options
        if not hasattr(self.o, 'msg_skip_threshold'):
            self.o.msg_skip_threshold = 3600
        else:
            if type(self.o.msg_skip_threshold) is list:
                self.o.msg_skip_threshold = int(self.o.msg_skip_threshold[0])

    def after_accept(self, worklist):
        new_incoming = []

        for message in worklist.incoming:
            then = timestr2flt(message['pubtime'])
            now = nowflt()

            # Set the maximum age, in seconds, of a message to retrieve.
            lag = now - then

            if lag > int(self.o.msg_skip_threshold):
                logger.info("msg_skip_old, Excessive lag: %g sec. Skipping download of: %s, "
                    % (lag, message['new_file']))
                worklist.rejected.append(m)

            new_incoming.append(message)
        worklist.incoming = new_incoming
