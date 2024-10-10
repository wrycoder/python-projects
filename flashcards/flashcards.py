#
# flashcards.py
#
# A configurable learning tool.
#

import json

class ConfigurationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Card:
    """A single flash card"""
    def __init__(self, title: str, **kwargs):
        self.details = {}
        self.title = title
        for k, v in kwargs.items():
            self.details[k] = v

    def __getitem__(self, key):
        return self.details[key]

class CardEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Card):
            output = {"title": obj.title}
            output.update(obj.details)
            return output
        return json.JSONEncoder.default(self, obj)

class Deck:
    """A collection of flash cards"""
    def __init__(self, deck_name: str, display_template: str, data: str):
        try:
            self.deck_name = deck_name
            self.display_template = display_template
            self.data = json.loads(data)
        except(json.decoder.JSONDecodeError):
            raise ConfigurationError(f"Invalid configuration data: {data}")

    def __len__(self):
        """The number of cards in this deck"""
        return len(self.data)

    def __getitem__(self, key):
        """Get a specific card"""
        return self.data[key]

    def display_all(self):
        # eventually, some variant of this:
        # marie = {'title': 'Marie Curie', 'birthplace': 'Warsaw', 'born_in': 1867, 'died_in': 1934}
        # display_template = "{marie['title']} was born in {marie['birthplace']} in the year {marie['born_in']}"
        # eval('f"' + display_template + '"')
        result = ""
        for card in self.data:
            result += eval('f"' + self.display_template + '"')
        return result


