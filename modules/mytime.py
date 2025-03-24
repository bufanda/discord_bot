"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 28.11.2024
    @CLicense: MIT
    @Description: Module to convert timestamps for better handling
                  or readability.
"""

from datetime import datetime, timedelta

class MyTime:
    """my very own time class"""

    # pylint: disable=no-self-argument

    def convert_time(in_sec: int) -> str:
        """convert time in seconds to a human readable format"""
        days = 0
        hours = 0
        minutes = 0
        seconds = in_sec

        days = int(in_sec / 86400)
        seconds = in_sec % 86400

        hours = int(seconds / 3600)
        seconds = seconds % 3600

        minutes = int(seconds / 60)
        seconds = int(seconds % 60)

        return f"{days:02d}d {hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_date_for_age(in_sec: int) -> datetime:
        """get a date for an age in seconds"""
        return datetime.today() - timedelta(days=in_sec)

    def get_timestamp(_string) -> int:
        """get the unix timestamp for a time in server format"""
        return datetime.strptime(_string, "%Y.%m.%d-%H.%M.%S").timestamp()

    def get_time_delta(_string: str) -> int:
        """ get time delta from a string """
        s = str.split(_string, sep=":")
        retval = int(s[0])*3600 + int(s[1])*60 + int(s[2])
        return retval

    # pylint: enable=no-self-argument
