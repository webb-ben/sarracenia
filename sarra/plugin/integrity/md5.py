#!/usr/bin/env python3

from hashlib import md5

from sarra.plugin.integrity import Integrity
from base64 import b64decode, b64encode

class Md5(Integrity):
      """
         use the (obsolete) Message Digest 5 (MD5) algorithm, applied on the content
         of a file, to generate an integrity signature.
      """
      @classmethod
      def assimilate(cls,obj):
         obj.__class__ = Md5

      def __init__(self):
         Md5.assimilate(self)

      def registered_as():
          """
            v2name.
          """
          return 'd'

      def get_value(self):
          return b64encode(self.filehash.digest()).decode('utf-8')

      def set_path(self,path):
          self.filehash = md5()

      def update(self,chunk):
          if type(chunk) == bytes : self.filehash.update(chunk)
          else                    : self.filehash.update(bytes(chunk,'utf-8'))
