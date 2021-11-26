#!/usr/bin/python3
"""
  For Production deployments, see: part_check instead of this file (file_check)  

  As file_check re-reads the entire file, re-calculates from scratch, which is very inefficient 
  compared to part_check which takes care of checksum calc done as the files are downloaded.
  NOTE: it also deletes the downloaded file after checking!

STATUS:
  This is more for debugging, internal testing, and reference.
  20171212: not sure if it has been fixed after the local->new transition.

"""
import os, stat, time
from hashlib import md5
import logging
from sarracenia.flowcb import FlowCB

logger = logging.getLogger(__name__)

class Check(FlowCB):
    def __init__(self, options):
        self.o = options

    def after_work(self, worklist):
        for message in worklist.ok:
            logger.info("check_file local file %s " % message['new_file'])
            logger.info("check_file partflg    %s " % message['partflg'])
            logger.info("check_file sumflg     %s " % message['sumflg'])
            logger.info("check_file filesize   %s " % message['filesize'])
            logger.info("check_file offset     %d " % message['offset'])
            logger.info("check_file length     %d " % message['length'])
    
            if message['partflg'] != '1' or message['sumflg'] != 'd':
                logger.warning("ignore parts or not md5sum on data")
                os.unlink(message['new_file'])
                worklist.rejected.append(message)
    
            lstat = os.stat(message['new_file'])
            fsiz = lstat[stat.ST_SIZE]
    
            if fsiz != message['filesize']:
                logger.error("check_file filesize differ (corrupted ?)  lf %d  msg %d" % fsiz, message['filesize'])
                os.unlink(message['new_file'])
                worklist.rejected.append(message)
    
            f = open(message['new_file'], 'rb')
            if message['offset'] != 0: f.seek(message['offset'], 0)
            if message['length'] != 0: data = f.read(message['length'])
            else: data = f.read()
            f.close()
            fsum = md5(data).hexdigest()
    
            if fsum != message['checksum']:
                logger.error("check_file checksum differ (corrupted ?)  lf %s  msg %s" % fsum, message['checksum'])
            os.unlink(message['new_file'])
            worklist.rejected.append(message)
