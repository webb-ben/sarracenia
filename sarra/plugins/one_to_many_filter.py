##
#  MG template for a filter that parse a file into many others
##

class One_To_Many_Filter(object):

      # registering as http for localhost stuff

      def __init__(self,parent) :
          self.registered_list = [ 'http' ]

      def registered_as(self) :
          return self.registered_list

      # here is just an example...
      # parsed_filename = original_filename + '_split_' + "rank in file"

      def on_message(self,parent):
          parent.msg.new_file += '_split_'
          return True

      # ok using do_download to parse and publish

      def do_download(self, parent ):
          self.parent = parent
          self.logger = parent.logger

          ipath  = parent.base_dir + '/' + parent.msg.relpath

          self.logger.info("splitting %s" % os.path.basename(ipath) )

          # HERE IS A FUNCTION THAT EXTRACTS/GENERATES THE FILES
          # AND RETURNS A LIST CONTAINING THE ABSOLUTE PATH FOR
          # THE FILES GENERATED

          opaths = self.FILE_PARSER(ipath)

          # if it did not work it is an error

          if not opaths or len(opaths) <= 0 : return False

          # publish all parsed files but last

          for p in opaths[:-1] :
              self.update_message(p)

              # publishing

              ok = parent.__on_post__()
              if ok and parent.reportback: msg.report_publish(201,'Published')

          # prepare message for last file
          # and let sarra post it as if it
          # was a normal downloaded product
          # from the incoming message

          self.update_message(opaths[-1])

          return True

      # update message for parsed file

      def update_message(self, path ):
          import os,stat

          parent  = self.parent
          logger  = parent.logger
          msg     = parent.msg
          lstat   = os.stat(path)

          # adjust part

          fsiz    = lstat[stat.ST_SIZE]
          partstr = '1,%d,1,0,0' % fsiz
          msg.partstr          = partstr
          msg.headers['parts'] = msg.partstr

          # adjust time

          if parent.preserve_time or 'mtime' in msg.headers :
             msg.headers['mtime'] = timeflt2str(lstat.st_mtime)
             msg.headers['atime'] = timeflt2str(lstat.st_atime)

          # adjust mode

          if parent.preserve_mode or 'mode' in msg.headers:
             msg.headers['mode']  = "%o" % ( lstat[stat.ST_MODE] & 0o7777 )

          # adjust checksum

          algo = msg.sumalgo
          algo.set_path(path)
          src  = open(path,'rb')
          while True:
                chunk = src.read(parent.bufsize)
                if not chunk : break
                algo.update(chunk)

          checksum = algo.get_value()

          msg.set_sum(msg.sumflg,checksum)
          msg.onfly_checksum = checksum

          # adjust topic, notice

          msg.new_file    = os.path.basename(path)
          msg.new_relpath = path.replace(parent.base_dir,'')

          msg.set_topic(msg.topic_prefix,msg.new_relpath)
          msg.set_notice(msg.new_baseurl,msg.new_relpath)

      # file parsing here

      def FILE_PARSER(self, ipath ):

          opaths = []

          # PARSE THE FILE HERE

          # EACH GENERATED FILE SHOULD HAVE A DIFFERENT PATH
          # THAT SHOULD LOOK LIKE

          # opath  = parent.msg.new_dir + '/' + new_extracted_filename

          # EACH SUCCESSFULL PATH IS APPENDED TO THE LIST

          # opaths.append(opath)

          # RETURN THE LIST OF ALL GENERATED FILES

          return opaths
