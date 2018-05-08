class Conversation:
    """
    Represents a conversation object with its initiation and responses.
    """
    def is_valid(self):
        return self.initiation and len(self.responses) > 0

    def new_initiation(self, text):
        self.initiation = text

    def add_to_conversation(self, text):
        if not self.initiation:
            self.initiation = text
        else:
            self.responses.append(text)

    def append_to_last(self, text):
        if len(self.responses) < 1:
            self.initiation += " " + text
        else:
            self.responses[-1] += " " + text

    def __init__(self):
        self.initiation = ""
        self.responses = []

    def __str__(self):
        return "- - {}".format(self.initiation) \
               + "\n  - " \
               + "\n  - ".join(r for r in self.responses)
