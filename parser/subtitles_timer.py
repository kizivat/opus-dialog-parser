# -*- coding: utf-8 -*-


class SubtitlesTimer:
    """
    Represents a timer of subtitles. In OPUS timer data
    are stored in tag <time> having attributes 'id' and 'vlaue'.

    In 'id' is stored the ID of the timer in format T{id}[ES]
    (E for end of a time frame, S for start of a time frame).

    For example
        <time id="T939E" value="01:39:19,415" />
    represents the end of a time frame with id 939
    at time 1 hour, 39 minutes and 19.415 seconds.
    """

    def __init__(self, hours, minutes, seconds, is_end):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.is_end = is_end

    @staticmethod
    def timer_zero():
        """
        Returns a timer at 0 hours, 0 minutes and 0.0 seconds.
        """
        return SubtitlesTimer(0, 0, 0.0)

    @classmethod
    def fromstring(cls, string_time, is_end):
        """
        Returns an instance of class SubtitlesTimer
        constructed from a string in the following format:
            hh:mm:ss,sss
        or
            hh:mm:ss.sss
        Both are accepted. The reason for this is OPUS using
        decimal comma instead of decimal point.
        """
        parts = string_time.replace(' ', '').split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2].replace(',', '.'))
        return cls(hours, minutes, seconds, is_end)

    def delta_seconds(self, other):
        """
        Returns the number of seconds between the self timer object
        and the other timer object. Other is subtracted from self.
        """
        return SubtitlesTimer.in_seconds(self) - SubtitlesTimer.in_seconds(other)

    def in_seconds(self):
        """
        Returns the timer converted to seconds.
        """
        return 3600.0 * float(self.hours) + 60.0 * float(self.minutes) + self.seconds

    def __str__(self):
        return '{:>02}:{:02}:{:06.3f}'.format(self.hours, self.minutes, self.seconds).replace('.', ',')

    def __eq__(self, other):
        return self.hours == other.hours \
               and self.minutes == other.minutes \
               and self.seconds == other.seconds
