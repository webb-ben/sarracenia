#!/usr/bin/python3
"""
   print the age of files written (compare current time to mtime of message.)
   usage:


   on_file file_age


"""

import os, stat, time
from sarracenia import nowflt, timestr2flt
import logging
from sarracenia.flowcb import FlowCB

logger = logging.getLogger(__name__)

class FileAge(FlowCB):
    def __init__(self, options):
        self.o = options
        logger.debug("file_age initialized")

    def after_work(self, worklist):
        for message in worklist.ok:
            if not 'mtime' in message['headers'].keys():
                continue
            now = nowflt()
            mtime = timestr2flt(message['headers']['mtime'])
            age = now - mtime
            logger.info("file_age %g seconds for %s" % (age, message['new_file']))

