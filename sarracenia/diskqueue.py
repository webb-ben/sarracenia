#!/usr/bin/env python3
#
# This file is part of sarracenia.
# The sarracenia suite is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2008-2015
#
# more info: https://github.com/MetPX/sarracenia
#
# Code originally contributed by:
#  Michel Grenier - Shared Services Canada
#  first shot     : Wed Jan 10 16:06:16 UTC 2018
#  re-factored beyond recognition by PSilva 2021. Don't blame Michel 
#

import os, sys, time
from _codecs import decode, encode

import jsonpickle

from sarracenia import nowflt, timestr2flt

import logging

# class sarra/retry

logger = logging.getLogger(__name__)


class DiskQueue():
    """
    Process Persistent Queue...

    Persist messages to a file so that processing can be attempted again later.
    For safety reasons, want to be writing to a file ASAP.
    For performance reasons, all those writes need to be Appends.

    so continuous, but append-only io... with an occasional housekeeping cycle.
    to resolve them
   
    not clear if we need multi-task safety... just one task writes to the queue.

    retry_ttl how long 

    self.retry_cache 
          - a dictionary indexed by some sort of key to prevent duplicate messages
            being stored in it.

    retry_path = ~/.cache/sr3/<component>/<config>/diskqueue_<name>
    with various suffixes:

    .new  -- messages added to the retry list are appended to this file.
            
    whenever a message is added to the retry_cache, it is appended to a cumulative
    list of entries to add to the retry list.  

    every housekeeping interval, the two files are consolidated.

    note that the *ack_id* of messages retreived from the retry list, is removed.
    files must be acked around the time they are placed on the retry_list.
    as reception from the source has already been acknowledged.

    FIXME:  would be fun to look at performance of this thing and compare it to
        python persistent queue.  the differences:

        This class does no locking (presumed single threading.) 
             could add locks... and they would be coarser grained than stuff in persistentqueue
             this should be faster than persisten queue, but who knows what magic they did.
        This class doesn't implement in-memory queue... it is entirely on disk...
        saves memory, optimal for large queues.  
           probably good, since retries should be slow...

        not sure what will run better.
   
    """
    def __init__(self, options, name):

        logger.debug(" %s __init__" % name )

        self.o = options

        self.name = name

        if not hasattr(self.o, 'retry_ttl'):
            self.o.retry_ttl = None

        #logging.basicConfig(format=self.o.logFormat,
        #                    level=getattr(logging, self.o.logLevel.upper()))
        logger.setLevel(getattr( logging, self.o.logLevel.upper()))

        logger.debug('name=%s logLevel=%s' % (self.name, self.o.logLevel) )

        # initialize all retry path if retry_path is provided
        self.working_dir=os.path.dirname(self.o.pid_filename)
        self.queue_file= self.working_dir + os.sep + 'diskqueue_' + name
        self.now = nowflt()

        # retry messages

        self.queue_fp = None

        # newer retries

        self.new_path = self.queue_file + '.new'
        self.new_fp = None

        # working file at housekeeping
        self.housekeeping_path = self.queue_file + '.hk'
        self.housekeeping_fp = None

        # initialize ages.

        if not os.path.isfile(self.queue_file): return

        retry_age = os.stat(self.queue_file).st_mtime

        if os.path.isfile(self.new_path):
            new_age = os.stat(self.new_path).st_mtime
            if retry_age > new_age: os.unlink(self.new_path)


    def put(self,message_list):
        """
          add messages to the end of the queue.
        """

        if self.new_fp is None:
            self.new_fp = open(self.new_path, 'a')

        for message in message_list:
            logger.debug("DEBUG add to new file %s %s" %
                 (os.path.basename(self.new_path), message))
            self.new_fp.write(self.msgToJSON(message))
        self.new_fp.flush()

    def cleanup(self):

        if os.path.exists(self.queue_file):
            os.unlink(self.queue_file)

    def close(self):
        try:
            self.housekeeping_fp.close()
        except:
            pass
        try:
            os.fsync(self.new_fp)
            self.new_fp.close()
        except:
            pass
        try:
            self.queue_fp.close()
        except:
            pass
        self.housekeeping_fp = None
        self.new_fp = None
        self.queue_fp = None

    def msgFromJSON(self, line):
        try:
            msg = jsonpickle.decode(line)
        except ValueError:
            logger.error("corrupted line in retry file: %s " % line)
            logger.debug("Error information: ", exc_info=True)
            return None

        return msg

    def msgToJSON(self, message):
        return jsonpickle.encode(message) + '\n'

    def get(self, maximum_messages_to_get=1):
        """
           qty number of messages to retrieve from the queue.

        """

        ml=[]
        count=0
        while count < maximum_messages_to_get : 
            self.queue_fp, message = self.msg_get_from_file( self.queue_fp, self.queue_file)

            # FIXME MG as discussed with Peter
            # no housekeeping in get ...
            # if no message (and new or state file there)
            # we wait for housekeeping to present retry messages
            if not message:
                try:
                    os.unlink(self.queue_file)
                except:
                    pass
                self.queue_fp = None
                #logger.debug("MG DEBUG retry get return None")
                break
            
            if self.is_expired(message):
                #logger.error("MG invalid %s" % message)
                continue

            message['isRetry'] = True
            if 'ack_id' in message:
               del message['ack_id']
               message['_deleteOnPost'].remove('ack_id')

            ml.append(message)
            count +=1
        return ml

    def in_cache(self, message):
        """
          return whether the entry is message is in the cache or not.
          side effect: adds it.

        """
        urlstr = message['baseUrl'] + '/' + message['relPath']
        sumstr = jsonpickle.encode(message['integrity'])
        cache_key = urlstr + ' ' + sumstr

        if 'parts' in message:
            cache_key += ' ' + message['parts']

        if cache_key in self.retry_cache: return True
        self.retry_cache[cache_key] = True
        return False

    def is_expired(self, message):
        # no expiry
        if self.o.retry_ttl is None: return False
        if self.o.retry_ttl <= 0: return False

        # compute message age
        msg_time = timestr2flt(message['pubTime'])
        msg_age = self.now - msg_time

        # expired ?
        return  msg_age > self.o.retry_ttl

    def needs_requeuing(self, message):

        if self.in_cache(message):
            logger.info("discarding duplicate message (in %s cache) %s" % (self.name, message) )
            return False

        # log is info... it is good to log a retry message that expires
        if self.is_expired(message):
            logger.info("discarding expired message in (%s): %s" % (self.name, message) )
            return False

        return True

    def msg_get_from_file(self, fp, path):
        if fp is None:
            if not os.path.isfile(path): return None, None
            logger.debug("DEBUG %s open read" % path)
            fp = open(path, 'r')

        line = fp.readline()
        if not line:
            try:
                fp.close()
            except:
                pass
            return None, None

        msg = self.msgFromJSON(line)
        # a corrupted line : go to the next
        if msg is None: return self.msg_get_from_file(fp, path)

        return fp, msg

    def on_housekeeping(self):
        """

           read rest of queue_file (from current point of unretried ones.)
                 - check if message is duplicate or expired.
                 - write to .hk

           read .new file, 
                 - check if message is duplicate or expired.
                 - writing to .hk (housekeeping)

           remove .new
           rename housekeeping to queue for next period.
        """
        logger.info("%s on_housekeeping" % self.name)

        # finish retry before reshuffling all retries entries

        if os.path.isfile(self.queue_file) and self.queue_fp != None:
            logger.info("have not finished retry list. Resuming retries with %s" % self.queue_file )
            return

        self.now = nowflt()
        self.retry_cache = {}
        N = 0

        # put this in try/except in case ctrl-c breaks something

        try:
            self.close()
            try:
                os.unlink(self.housekeeping_path)
            except:
                pass
            fp = open(self.housekeeping_path, 'w')
            fp.close()

            i = 0
            last = None

            fp = self.queue_fp
            self.housekeeping_fp=open( self.housekeeping_path, 'a')

            logger.debug("FIXME DEBUG has queue %s" % os.path.isfile(self.queue_file))

            # remaining of retry to housekeeping
            while True:
                fp, message = self.msg_get_from_file(fp, self.queue_file)
                if not message: break
                i = i + 1
                if not self.needs_requeuing(message): continue
                self.housekeeping_fp.write(self.msgToJSON(message))
                N = N + 1

            try:
                fp.close()
            except:
                pass

            i = 0
            j = N

            fp = None
            # append new to housekeeping.
            while True:
                fp, message = self.msg_get_from_file(fp, self.new_path)
                if not message: break
                i = i + 1
                logger.debug("DEBUG message %s" % message)
                if not self.needs_requeuing(message): continue

                #logger.debug("MG DEBUG flush retry to state %s" % message)
                self.housekeeping_fp.write(self.msgToJSON(message))
                N = N + 1
            try:
                fp.close()
            except:
                pass

            logger.debug("FIXME DEBUG took %d out of the %d retry" % (N - j, i))

            self.housekeeping_fp.close()

        except Exception as Err:
            logger.error("something went wrong")
            logger.debug('Exception details: ', exc_info=True)

        # no more retry

        if N == 0:
            logger.info("No retry in list")
            try:
                os.unlink(self.housekeeping_path)
            except:
                pass

        # housekeeping file becomes new retry

        else:
            logger.info("Number of messages in retry list %d" % N)
            try:
                os.rename(self.housekeeping_path, self.queue_file)
            except:
                logger.error("Something went wrong with rename")

        # cleanup
        try:
            os.unlink(self.new_path)
        except:
            pass

        elapse = nowflt() - self.now
        logger.info("on_housekeeping elapse %f" % elapse)

