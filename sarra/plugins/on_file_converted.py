
"""

   With this plugin, in sr_sarra, a converted product has
   is message fixed for its posting because the conversion
   changed its attributes.

   Conversion plugin rename the product and might add extension
   to the product. If this plugin is used in a sender, the 
   on_message function with strip the possible extensions the
   product may have. This was used because of the way sundew
   was working. A converted product would have the same name
   and the extension would have ex. GIF instead of PNG to 
   show how it was converted. Should such a product be delivered
   with WHATFN, its name would never show its type.

   Here in sarra, products converted to png would end with .png
   And this on_message would strip it out to mimic the sundew delivery.

"""

class On_File_Converted(object):

      def __init__(self,parent) :
          pass

      # if file was converted, get rid of extensions it had

      def on_message(self, parent ):
          import os,stat

          if parent.program_name != 'sr_sender' : return True

          self.parent = parent
          self.logger = parent.logger

          nf = self.parent.new_file

          # format

          if   '.imv6' in nf : nf = nf.replace('.imv6','')
          elif '.png'  in nf : nf = nf.replace('.png','')

          # compression

          if   '.gz'   in nf : nf = nf.replace('.gz','')
          elif '.Z'    in nf : nf = nf.replace('.Z','')

          self.parent.new_file = nf

          return True

      # once the file converted, adjust message 

      def on_file(self, parent ):
          import os,stat

          if parent.program_name != 'sr_sarra' : return True

          logger  = parent.logger
          msg     = parent.msg
          path    = msg.new_dir + '/' + msg.new_file

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

          return True

self.plugin='On_File_Converted'

