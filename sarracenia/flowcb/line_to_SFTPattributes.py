#!/usr/bin/env python3
"""
    This plugin turns a line into SFTPattributes object. It sets the fields st_mtime, st_gid,
    st_uid, st_size, st_mode, filname, and longname.

"""
import logging
import paramiko
from sarracenia.flowcb import FlowCB
import dateparser
from paramiko.sftp_attr import SFTPAttributes
import datetime
import pytz
file_type_dict = {
    'l': 0o120000,  # symbolic link
    's': 0o140000,  # socket file
    '-': 0o100000,  # regular file
    'b': 0o060000,  # block device
    'd': 0o040000,  # directory
    'c': 0o020000,  # character device
    'p': 0o010000   # fifo (named pipe)
}

class Line_To_SFTPattributes(FlowCB):
    def __init__(self, options):
        self.o = options


    def modstr2num(self, m):
        mode = 0
        if (m[0] == 'r'): mode += 4
        if (m[1] == 'w'): mode += 2
        if (m[2] == 'x'): mode += 1
        return mode


    def filemode(self, modstr):
        mode = 0
        mode += file_type_dict[modstr[0]]
        mode += self.modstr2num(modstr[1:4]) << 6
        mode += self.modstr2num(modstr[4:7]) << 3
        mode += self.modstr2num(modstr[7:10])
        return mode

    def fileid(self, id):
        if type(id) is str: return 1000
        else: return id

    def filedate(self,line):
        line_split = line.split()
        file_date = line_split[5] + " " + line_split[6] + " " + line_split[7]
        current_date = datetime.datetime.now(pytz.utc)
        # case 1: the date contains '-' implies the date is in 1 string not 3 seperate ones, and H:M is also provided
        if "-" in file_date: file_date = line_split[5] + " " + line_split[6]
        standard_date_format = dateparser.parse(file_date,
                                                settings={
                                                    'RELATIVE_BASE': datetime.datetime(current_date.year, 1, 1),
                                                    'TIMEZONE': 'UTC', #turn this into an option - should be EST for mtl
                                                    'TO_TIMEZONE': 'UTC'})
        if standard_date_format is not None:
            # case 2: the year was not given, it is defaulted to 1900. Must find which year (this one or last one).
            if standard_date_format.month - current_date.month >= 6:
                standard_date_format = standard_date_format.replace(year=(current_date.year - 1))
        timestamp = datetime.datetime.timestamp(standard_date_format)
        return timestamp


    def on_line(self, line):
        if type(line) is paramiko.SFTPAttributes:
            return line
        elif type(line) is str:
            parts = line.split()
            sftp_obj = SFTPAttributes()
            sftp_obj.st_mode = self.filemode(parts[0])
            sftp_obj.st_uid = int(self.fileid(parts[2]))   # 1000 if its you
            sftp_obj.st_gid = int(self.fileid(parts[3]))   # 1000 if its you
            sftp_obj.st_size = int(parts[4])
            sftp_obj.st_mtime = self.filedate(line)
            sftp_obj.filename = parts[-1]
            sftp_obj.longname= line
            return sftp_obj
        else:
            return None
