#
# flashcards.py
#
# A configurable learning tool.
#

import json, re, sys, curses, screen_utils

class ConfigurationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Card:
    """
    A single flash card

    Parameters:
        title:          the name of the subject of this card
        kwargs:         dictionary containing details about the subject
    """
    def __init__(self, title: str, **kwargs):
        """Initialize the Card object"""
        self.details = {}
        self.title = title
        for k, v in kwargs.items():
            self.details[k] = v

    def __getitem__(self, key):
        """
        Access a given property via subscript

        Parameters:
            key:        dictionary key for the given property
        """
        if key != 'title':
            return self.details[key]
        else:
            return self.title

    def display(self, template, topics={}):
        """
        Show this card, using fixed text with markup to be replaced by
        properties of the current subject. The markup syntax for these
        replaced values takes the form ``{card['property']}``, where
        each *property* is a detail about the subject.

        Parameters:
            template:   the boilerplate text with embedded symbols
                        (must be contained in a list of at least one
                        element)
            topics:     dictionary of related topics, which may or
                        may not contain the subject of the current card
        """
        result = []
        for line in template:
            new_line = re.sub(r'\{card\[', '{self[', line)
            result.append(eval('f"' + new_line + '"'))
        if len(topics) > 0:
            for (topic, table) in topics.items():
                members = table['members']
                if self.title in members:
                    topic_template = table['detail']
                    for topic_line in topic_template:
                        new_topic_line = re.sub(r'\{card\[', '{self[', topic_line)
                        result.append(eval('f"' + new_topic_line + '"'))
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
            self.deck_name = deck_name
            self.display_template = js_data['display_template']
            raw_data = js_data['data']
            self.data = []
            self.topics = {}
            for item in raw_data:
                self.data.append(Card(item.pop('title'), **item))
            if 'topics' in js_data:
                topic_list = js_data['topics']
                for item in topic_list:
                    self.topics.update(item)
        except(json.decoder.JSONDecodeError) as ex:
            raise ConfigurationError(f"Invalid configuration data: {data}")

    def __len__(self):
        """The number of cards in this deck"""
        return len(self.data)

    def __getitem__(self, key):
        """Get a specific card"""
        return self.data[key]

    def display_all(self, for_topic: str=None):
        """
        Show all cards, or cards on a certain topic

        Parameters:
            for_topic:      the topic all of these cards have in common
        """
        result = []
        for card in self.data:
            if for_topic is None:
                result += card.display(
                    self.display_template,
                    self.topics
                )
            elif for_topic in self.topics:
                members = self.topics[for_topic]['members']
                if card.title in members:
                    result += card.display(
                        self.display_template,
                        self.topics
                    )
        return result

def do_loop(stdscr, cards):
    result = 0
    while(result != ord('q')):
        stdscr.clear()
        stdscr.refresh()
        curses.curs_set(0)
        height, width = stdscr.getmaxyx()
        paging_win = curses.newwin(height - 1, width - 1, 0, 0)
        y_index = 0
        for line in cards.display_all():
            stdscr.addstr(y_index, 0, line)
            y_index += 1
        stdscr.addstr(y_index, 0, 'Press q to quit')
        stdscr.refresh()
        result = stdscr.getch()

if __name__ == "__main__":
    try:
        with open(sys.argv[1]) as sourcefile:
            cards = Deck('flashcards', sourcefile.read())
    except:
        print("ERROR: please specify a source file for the data")
        quit()

    curses.wrapper(do_loop, cards)
