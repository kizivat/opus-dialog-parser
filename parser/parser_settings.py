# -*- coding: utf-8 -*-
import logging.config

logging.config.fileConfig("development.ini")
log = logging.getLogger(__name__)


class ParserSettings:
    punctuation_mid_regex = r"[\\,\\:]"
    punctuation_regex = r"[\\.\\?\\!]|\\.\\.\\."
    parenthesis_regex = r"[\\\"\\\']"
    response_timeout = 2.5
    profanity_filter_file_dir = "../resources/profanity_filter_sk.txt"
    profanity_filter_accept_file_dir = "../resources/profanity_filter_sk_accept.txt"
    output_dir = "output/"

    opus_data_dir = '/Users/dkizivat/dev/OpenSubtitles/xml/sk/'
    profanity_filter = []
    profanity_accept = []

    @classmethod
    def set(cls):
        cls.build_profanity_filter()
        cls.build_profanity_accept()

    @classmethod
    def build_profanity_filter(cls):
        log.info(
            'Loading profanity filter from \"%s\" ...'
            , cls.profanity_filter_file_dir)
        with open(cls.profanity_filter_file_dir, encoding='utf-8') as file:
            profanity_filter = file.readlines()
        cls.profanity_filter = [x.strip('\n') for x in profanity_filter]

    @classmethod
    def build_profanity_accept(cls):
        log.info(
            'Loading words to leave out from profanity filtering from \"%s\" ...'
            , cls.profanity_filter_accept_file_dir)
        with open(cls.profanity_filter_accept_file_dir, encoding='utf-8') as file:
            profanity_accept = file.readlines()
        cls.profanity_accept = [x.strip('\n') for x in profanity_accept]
