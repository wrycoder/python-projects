#
# flashcards.py
#
# A configurable learning tool.
#

import json, re

class ConfigurationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Card:
    """A single flash card"""
    def __init__(self, title: str, **kwargs):
        """Initialize the Card object"""
        self.details = {}
        self.title = title
        for k, v in kwargs.items():
            self.details[k] = v

    def __getitem__(self, key):
        """Access a given property via subscript"""
        if key != 'title':
            return self.details[key]
        else:
            return self.title

    def display(self, template):
        result = ""
        for line in template:
            new_line = re.sub(r'\{card\[', '{self[', line)
            result += eval('f"' + new_line + '"')
            result += '\n'
        return result

class CardEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Card):
            output = {"title": obj.title}
            output.update(obj.details)
            return output
        return json.JSONEncoder.default(self, obj)

class Deck:
    """A collection of flash cards"""
    def __init__(self, deck_name: str, data: str):
        """Initialize the deck"""
        try:
            js_data = json.loads(data)
#            print(json.dumps(js_data, indent=4))
            self.deck_name = deck_name
            self.display_template = js_data['display_template']
            raw_data = js_data['data']
            self.data = []
            for item in raw_data:
                self.data.append(Card(item.pop('title'), **item))
        except(json.decoder.JSONDecodeError):
            raise ConfigurationError(f"Invalid configuration data: {data}")

    def __len__(self):
        """The number of cards in this deck"""
        return len(self.data)

    def __getitem__(self, key):
        """Get a specific card"""
        return self.data[key]

    def display_all(self):
        result = ""
        for card in self.data:
            result += card.display(self.display_template)
        return result


