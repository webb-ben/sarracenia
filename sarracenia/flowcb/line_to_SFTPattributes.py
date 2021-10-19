#!/usr/bin/env python3
"""


"""
import logging
import paramiko
from sarracenia.flowcb import FlowCB
import os
from paramiko.sftp_attr import SFTPAttributes
import stat
from datetime import datetime, timezone
from datetime import datetime, timedelta, timezone
from pathlib import Path
import datetime
import pytz

class Line_To_SFTPattributes(FlowCB):
    def __init__(self, options):
        self.o = options

    def on_line(self, line):
        if type(line) is paramiko.SFTPAttributes:
            return line
        elif type(line) is str:
            parts = line.split()
            filename = parts[-1]
            path = self.o.directory + "/" + filename
            status = os.stat(path)
            sftp_obj = SFTPAttributes.from_stat(status)
            sftp_obj.longname = line
            sftp_obj.filename = filename
            return sftp_obj
        else:
            return None


