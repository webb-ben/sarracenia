##
#  one_to_one_filter template plugin
##

class One_To_One_Filter(object):

      # registering as http for localhost stuff

      def __init__(self,parent) :
          self.registered_list = [ 'http' ]

      def registered_as(self) :
          return self.registered_list

      def on_message(self,parent):

          # Mandatory different filename

          # parent.msg.new_file = "CONVERTED PRODUCT NAME"

          return True

      def do_get(self, parent ):
          import os

          logger = parent.logger

          # input file path
          ipath  = parent.base_dir    + '/' + parent.msg.relpath

          # output file path
          opath  = parent.msg.new_dir + '/' + parent.msg.new_file

          #
          logger.info("converting %s to %s" % \
                     (os.path.basename(ipath),os.path.basename(opath)))

          # HERE
          # proceed with converting ipath resulting into opath
          # return True if everything worked fine, False if not

          return True

self.plugin='One_To_One_Filter'
