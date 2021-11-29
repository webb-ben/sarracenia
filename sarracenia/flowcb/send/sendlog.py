#!/usr/bin/python3
"""
do_send_log : an example do_send that only logs for testing purpose
"""
import logging
from sarracenia.flowcb import FlowCB

logger = logging.getLogger(__name__)

class SendLog(FlowCB):
    def __init__(self, options):
        self.o = options
        self.proto = None

    def send(self, msg):
        local_file = msg['relPath']
        new_dir = msg['new_dir']
        new_file = msg['new_file']

        try:
            logger.info("transport send")

            if self.proto == None:
                logger.info("transport send connects")
                proto = True

            logger.info("cd %s (perm 775)" % new_dir)

            if msg['sumflg'] == 'R':
                logger.info("rm %s" % new_file)
                return True

            if msg['sumflg'] == 'L':
                logger.info("symlink %s %s" % (new_file, msg['headers']['link']))
                return True

            offset = 0
            if msg['partflg'] == 'i': offset = msg['offset']

            str_range = ''
            if msg['partflg'] == 'i':
                str_range = 'bytes=%d-%d' % (offset, offset + msg['length'] - 1)

            #upload file
            if self.o.inflight == None or msg['partflg'] == 'i':
                logger.info("put %s %s (%d,%d,%d)" % (local_file, new_file, offset, offset, msg['length']))
            elif self.o.inflight == '.':
                new_lock = '.' + new_file
                logger.info("put %s %s" % (local_file, new_lock))
                logger.info("rename %s %s" % (new_lock, new_file))
            elif self.o.inflight[0] == '.':
                new_lock = new_file + self.o.inflight
                logger.info("put %s %s" % (local_file, new_lock))
                logger.info("rename %s %s" % (new_lock, new_file))
            elif self.o.inflight == 'umask':
                logger.info("umask")
                logger.info("put %s %s" % (local_file, new_file))

            logger.info('Sent: %s %s into %s/%s %d-%d' % (self.o.local_file, str_range, new_dir, new_file,
                             offset, offset + msg['length'] - 1))
        except:
            logger.error("Couldn't send log")
            logger.debug('Exception details: ', exc_info=True)
            return False

        return True


