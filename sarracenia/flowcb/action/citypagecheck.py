#!/usr/bin/python3
"""
  citypage_check.  debugging plugin.

  delete pages that are OK, leave the bad ones.

  we have a problem with how citypages are being posted.
  a lot of incomplete ones. they are getting posted while they are being
  re-written.

usage:

on_file file_citypage_check


"""
import os, stat, time
from hashlib import md5
import logging
from sarracenia.flowcb import FlowCB

logger = logging.getLogger(__name__)


class CityPageCheck(FlowCB):
    def __init__(self, options):
        self.o = options

    def after_work(self, worklist):
        for message in worklist.ok:
            bad = False
    
            logger.info("check_file local file %s partflg %s, sumflg %s " %
                        ( message['new_file'], message['partflg'], message['sumflg'] ) )
            logger.info("check_file file size  %s, offset %d, length %d. " %
                        ( message['filesize'], message['offset'], message['length']) )
    
            if message['partflg'] != '1' or message.sumflg != 'd':
                logger.warning("ignore parts or not md5sum on data")
                worklist.rejected.append(message)
    
            lstat = os.stat(message.new_file)
            fsiz = lstat[stat.ST_SIZE]
    
            if fsiz != message.filesize:
                logger.error("check_file filesize differ (corrupted ?)  lf %d  msg %d" %
                    (fsiz, message['filesize']))
                worklist.rejected.append(message)
    
            f = open(message['new_file'], 'rb')
            if message.offset != 0: f.seek(message['offset'], 0)
            if message['length'] != 0: data = f.read(message['length'])
            else: data = f.read()
            f.close()
            fsum = md5(data).hexdigest()
    
            if fsum != message['checksum']:
                logger.error("check_file checksum differ (corrupted ?)  lf %s  msg %s" % (fsum, message['checksum']))
                bad = True
    
            if "</siteData>" not in data.decode('iso8859-1'):
                logger.error("check_file does not have </siteData> in it, XML incomplete")
                bad = True
    
            if not bad:
                os.unlink(message['new_file'])

