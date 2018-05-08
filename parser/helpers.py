import re

from parser_settings import ParserSettings


def contains_profanity(string):
    return any(substring in string.lower() for substring in ParserSettings.profanity_filter) \
           and not any(substring in string.lower() for substring in ParserSettings.profanity_accept)
