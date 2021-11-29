"""
   http size was 4.1M an approximation
   get the right size set in post message
"""
import logging
import os, stat
from sarracenia.flowcb import FlowCB

logger = logging.getLogger(__name__)

class RepairSize(FlowCB):
    def __init__(self, options):
        self.o = options

    def after_work(self, worklist):
        for message in worklist.ok:
            path = message['new_dir'] + '/' + message['new_file']
            fsiz = os.stat(path)[stat.ST_SIZE]
            partstr = '1,%d,1,0,0' % fsiz

            if partstr == message['partstr']:
                continue

            message['partstr'] = partstr
            message['headers']['parts'] = message['partstr']
            logger.debug("file size repaired in message %s" % partstr)

