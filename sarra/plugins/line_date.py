#!/usr/bin/env python3
"""comments:
    This plugin compares today's date to the file's date by creating a date time object. Nine formats are
    acceptd so far, more can be added if needed (format on https://strftime.org/ ). Files with future dates
    are processed as long as the (future date - todays date) is < time_limit.
    FIXME: french input like Fev will not work - only Feb is accepted for the month
    If year is not provided, this means that the file is < 6 months old, so depending on todays date, assign
    appropriate year (for todays year: jan-jun -> assign prev year, for jul-dec assign current year)
    Note: is it possible for a file to be more than 6 months old and have the format Mo Day TIME ? (problematic)
"""

class Line_date(object):
    def __init__(self, parent):
        pass

    def _file_date_exceed_limit(self, parent, date, time_limit):
        time_limit = int(time_limit)
        current_date = datetime.datetime.now()
        accepted_date_formats = ['%d %b %H:%M', '%d %B %H:%M', '%b %d %H:%M', '%B %d %H:%M',
                                '%b %d %Y', '%B %d %Y', '%d %B %Y', '%d %B %Y', '%x']
        # case 1: the date contains - instead of /. Must be replaced
        if "-" in date: date = date.split()[0].replace('-', '/')
        for i in accepted_date_formats:
            try:
                file_date = datetime.datetime.strptime(date, i)
                # case 2: the year was not given, it is defaulted to 1900. Must find which year (this one or last one).
                if file_date.year == 1900:
                    if file_date.month - current_date.month >= 6:
                        file_date = file_date.replace(year=(current_date.year - 1))
                    else:
                        file_date = file_date.replace(year=current_date.year)
                parent.logger.debug("File date is: " + str(file_date) + " > File is " + str(
                    abs((file_date - current_date).seconds)) + " seconds old")
                return abs((file_date - current_date).seconds) < time_limit
            except Exception as e:
                # try another date format
                pass
        parent.logger.error("Assuming ok, unrecognized date format, %s" % date)
        return True

    def perform(self,parent):
        if hasattr(parent,'date') and hasattr(parent, 'file_time_limit'):
            return self._file_date_exceed_limit(parent, parent.date, parent.file_time_limit)
        return False

line_date = Line_date(self)
self.on_line = line_date.perform


