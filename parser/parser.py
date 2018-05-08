# -*- coding: utf-8 -*-
import errno
import logging.config
import os
import xml.etree.ElementTree as ElementTree

from conversation import Conversation
from helpers import *
from parser_settings import ParserSettings
from state_machine import ParserStates
from subtitles_timer import SubtitlesTimer

logging.config.fileConfig("development.ini")
log = logging.getLogger(__name__)


class Parser:
    state = ParserStates.ADD_TO_CONVERSATION
    conversation = Conversation()
    timers = []
    is_first_start = False
    output_stream = ""

    @classmethod
    def parse(cls, file):
        """
        Parses the conversations form OPUS's XML file and outputs it.
        """
        # XML tree
        tree = ElementTree.parse(file, ElementTree.XMLParser(encoding="utf-8"))
        root = tree.getroot()

        sentence_text = ""

        for sentence_node in root.findall("s"):
            cls.is_first_start = True
            if len(cls.timers) > 0:
                if cls.timers[-1].is_end:
                    sentence_text = ""
            iterator = sentence_node.iter()
            for node in iterator:
                if node.tag == "time":
                    cls.handle_timer(node.attrib)
                elif node.tag == "w":
                    sentence_text = cls.concat_word(node.text, sentence_text)
            if len(cls.timers) > 0:
                if cls.timers[-1].is_end:
                    cls.handle_sentence(sentence_text.strip())
        cls.save_conversation(cls.output_stream)

    @classmethod
    def handle_sentence(cls, sentence_text):
        """
        Handles the complete sentence by building a conversation.
        """
        sentence_text = sentence_text.replace(":", "...")
        if contains_profanity(sentence_text):
            cls.save_conversation(cls.output_stream)
        elif len(cls.timers) > 2 and cls.timers[-2].delta_seconds(cls.timers[-1]) > ParserSettings.response_timeout:
            cls.save_conversation(cls.output_stream)
        elif sentence_text[0] == "-":
            cls.split_dash_separated_dialog(sentence_text)
        else:
            cls.conversation.add_to_conversation(sentence_text.strip("-").strip())

    @classmethod
    def split_dash_separated_dialog(cls, text):
        lines = text.split("-")
        for line in lines:
            line = line.strip().strip("-").strip()
            if line:
                cls.conversation.add_to_conversation(line)

    @classmethod
    def save_conversation(cls, output_stream):
        """
        Outputs conversation.
        """
        if cls.conversation.is_valid():
            with open(ParserSettings.output_dir + output_stream, "a", encoding="utf-8") as f:
                f.write(str(cls.conversation) + "\n")
        cls.conversation = Conversation()

    @classmethod
    def concat_word(cls, word, sentence_text):
        """
        Returns sentence text with contents of word handled appropriately.
        """
        word = word.strip()
        if re.match(ParserSettings.punctuation_regex, word) \
                or re.match(ParserSettings.punctuation_mid_regex, word) \
                or not sentence_text:  # if word is punctuation or first word
            sentence_text += word  # no space in front
        else:
            sentence_text += " " + word
        return sentence_text.strip()

    @classmethod
    def handle_timer(cls, attrib):
        """
        Updates the timer with newest values.
        """
        match = re.match(r"^T([0-9]+)([SE])$", attrib["id"])
        is_end = bool(match[2] == "E")
        value = SubtitlesTimer.fromstring(attrib["value"], is_end)
        if match:
            if is_end and cls.timers[-1].is_end:
                cls.timers[-1] = value
            elif is_end:
                cls.timers.append(value)
            elif cls.is_first_start:
                cls.timers.append(value)
                cls.is_first_start = False
        else:
            log.error(f"Inconsistent timers in file {file}. Value: {value}")


def find_xml_files(directory):
    """
    Returns all xml files in the given directory found recursively.
    """

    files = []
    for file in os.listdir(directory):
        if os.path.isdir(directory + file):
            files = files + find_xml_files(directory + file + "/")
        else:
            if file[-4:] == ".xml":
                files.append(directory + file)
                log.debug(f"Found XML file \"{directory + file}\" staged for parsing.")
    return files


def main():
    """
    The entry point of the OPUS dialog parser.
    """

    ParserSettings.set()

    log.info("OPUS Dialog Parser started.")

    files = find_xml_files(ParserSettings.opus_data_dir)
    files_found = len(files)
    progress = 0
    log.info(f"Found {files_found} files.")

    mkdir_p(ParserSettings.output_dir)
    for file in files:
        progress += 1
        try:
            log.info(f"Trying to parse conversations from \"{file}\"... ({progress}/{files_found})")
            sub_id = file.split("/")[-1].split(".")[0]
            mkfile(ParserSettings.output_dir + sub_id + ".yml")
            Parser.output_stream = sub_id + ".yml"
            with open(ParserSettings.output_dir + Parser.output_stream, "a", encoding="utf-8") as f:
                f.write(f"categories:\n- {sub_id}\nconversations:\n")
            Parser.parse(file)
        except KeyboardInterrupt:
            log.info("Process stopped by user.")
            return 0
        except Exception:
            log.exception(f"Error in {file}")
            pass


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def mkfile(path):
    try:
        with open(path, 'w+'):
            return 1
    except IOError:
        print("Data file open, ensure it is closed, and re-run!")
        return 0