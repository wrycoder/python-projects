"""
a configurable learning tool for help with memorization

Displays a series of flashcards--screens with information about a
given subject. Users can view the cards one at a time, either
randomly or by entering the number of a specific card. Cards
can also be viewed in groups, based on selected topics.

If you choose to view a single card, you'll initially see
just a hint about its contents. This hint is like the "front"
of the card, designed to spur your memory. Press the forward
slash key (/) to flip the card over and see all the details
about its subject.

All `flashcards` information is defined in a JSON-formatted text file,
which must be specified on the command line:

   `$ python flashcards.py [source-file.json]`

CONFIGURATION
-------------

The JSON file that defines your deck of flashcards needs to
contain one parent dictionary with at least three child entries.
The first required entry is a simple string...

  "name" : (a string value)

...which serves as the overall name for your flashcard collection.

The second required entry is an array of child dictionaries...

  "data" : [ (an array of dictionaries) ]

...where you define various properties for each one of your cards.
You can define as many properties as you want, for as many cards as you
need, as long as each key in each dictionary is a string and each value
in each dictionary is a JSON data primitive. There's only one required
key in all of these child dictionaries--`title`. It's the string that
the system will use to identify the card.

The third and final required entry in your parent dictionary is an
array of strings...

  "display_template" : [ (an array of strings) ]

...in which each string is a line of text that will be displayed
when your card is viewed. The strings can have replacement tokens, of
the form `{card['property']}`. When the system calls the card's `display()`
method, these tokens will be replaced with the properties you defined in the
dictionary for the card.

There's also one optional entry you can make in your parent dictionary,
which you can use to make the system automatically assign a number to
each card:

  "numbered" : ( true|false )

If the "numbered" key is present, and set to `true`, the deck will have
a numerical key that can be used to access specific cards. The first
key is `1`. By default, the deck is unnumbered.

For a basic example of a flashcards configuration file, see `planets.json`.

ADVANCED CONFIGURATION
----------------------

The same properties can sometimes be shared by multiple flashcards in a
given deck. A collection of United States presidents, for example, will
have several presidents who were Republicans and several other presidents
who were Democrats. You might want to view all of these cards at the same time.
But how? The answer is in yet another (optional) configuration element in
the JSON dictionary...

  "topics" : [ (an array of dictionaries) ]

...where you define each topic that multiple cards have in common.

Now here's where things get a little more complicated. The key in each dictionary
is a simple string to identify the topic. But the value in each dictionary is
yet another dictionary, with four required entries:

  "character" : (a single character, identifying a menu option for this topic)
  "prompt" :    (a string containing the text for the description in the menu)
  "detail" :    [ (an array of strings containing text to be appended to
                   the output when the card is displayed. Replacement tokens
                   can be used here.) ]
  "members" :   [ (an array of strings, containing the `title` properties of the
                 cards that have this topic in common.) ]

For an example of an advanced flashcards configuration file, see `colonies.json`.
"""
import json, re, sys, random, curses
from .screen_utils import *

DEFAULT_RANDOM_MENU_CHAR    = 'r'
DEFAULT_NUMBERED_MENU_CHAR  = 'n'
DEFAULT_MAIN_MENU_CHAR      = 'm'
DEFAULT_TOGGLE_CHAR         = '/'
MAIN_MENU_LEVEL             = 0
CARD_FRONT_DISPLAY_LEVEL    = 1
CARD_BACK_DISPLAY_LEVEL     = 2
TOPIC_DISPLAY_LEVEL         = 3
NUMBER_INPUT_LEVEL          = 4
TOPIC_INPUT_LEVEL           = 5
DEFAULT_PROMPT              = 'press the [ESC] key to quit'

class ConfigurationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class CardNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Card:
    """
    A single flashcard

    Attributes
    ----------
    details : dict
        The properties to be displayed on this flashcard. There is
        only one required key, `title`, which serves as the subject of
        the card.
    title : str
        Name of the subject covered by this card.

    Methods
    -------
    display(template: list, topics: dict={}, number: int=None,
            front: bool=False)
        Get an ordered list of strings, each one of which is a line
        of text with details about the specific card. The `topics`
        dictionary contains information about various topics this
        card has in common with other cards in the deck. The `number` is
        a 1-indexed integer identifying this card's position in
        the deck. `front` identifies which side of the card you
        want to view.
    """
    def __init__(self, title: str, **kwargs):
        """Initialize the Card object

        Parameters:
            title:          the name of the subject of this card
            kwargs:         dictionary containing details about the subject
        """
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

    def display(self, template, topics={}, number=None, front=False) -> list:
        """
        Show this card, using fixed text with markup to be replaced by
        properties of the current subject. The markup syntax for the
        replaced values takes the form ``{card['property']}``, where
        each *property* is a detail about the subject.

        Parameters:
            template:   the boilerplate text with embedded symbols
                        (must be contained in a list of at least one
                        element)
            topics:     dictionary of related topics, which may or
                        may not contain the subject of the current card
            number:     the ordinal position of this card in the deck
            front:      boolean value to indicate front or back of card

        Returns:        a list containing lines of text
        """
        result = []
        if front == False:
            for line in template:
                new_line = re.sub(r'\{card\[', '{self[', line)
                if len(result) == 0 and number != None:
                    new_line = f"{number}. " + new_line
                result.append(eval('f"' + new_line + '"'))
            if len(topics) > 0:
                for (topic, table) in topics.items():
                    members = table['members']
                    if self.title in members:
                        topic_template = table['detail']
                        for topic_line in topic_template:
                            new_topic_line = re.sub(r'\{card\[', '{self[', topic_line)
                            result.append(eval('f"' + new_topic_line + '"'))
        else:
            line = random.choice(template).replace(
                           "{card['title']}", "???")
            new_line = re.sub(r'\{card\[', '{self[', line)
            if len(result) == 0 and number != None:
                new_line = f"{number}. " + new_line
            result.append(eval('f"' + new_line + '"'))
        return result

class CardEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Card):
            output = {"title": obj.title}
            output.update(obj.details)
            return output
        return json.JSONEncoder.default(self, obj)

class Deck:
    """
    A collection of flashcards

    Attributes
    ----------
    deck_name : str
        The name of this deck
    display_template : list
        A container of strings consisting of text with replacement tokens
    numbered : bool
        Indicates whether the cards in this deck are accessible by number
    data : list
        An ordered container of Card objects
    topics : dict
        An optional dictionary of topics that multiple cards have in common.
        The keys in this dictionary are the names of the topics. Each value
        is a child dictionary, which specifies the four standard properties of
        the given topic: `character`, `prompt`, `detail`, and `members`.
    current_menu_level : int
        An integer specifying the level of the main control loop. Possible
        values include MAIN_MENU_LEVEL, CARD_DISPLAY_LEVEL, TOPIC_DISPLAY_LEVEL,
        NUMBER_INPUT_LEVEL, and TOPIC_INPUT_LEVEL.

    Methods
    -------
    choose_card(number: int)
        Pick a card using a 1-indexed value

    find_topic(prompt_char: chr)
        Find the topic for a given prompt character

    list(for_topic: str=None)
        Get a list of all cards, or only those matching the specified topic

    main_menu()
        Get an ordered container of menu options. Each menu option is
        a dictionary with two keys: ``character`` (for the character a user
        must enter) and ``prompt`` (for the label the user will see on
        the menu). Every menu will have at least one option (``r``, to view
        a random card). Other menu options will be added based upon the contents
        of the ``self.topics`` dictionary.

    random_card()
        Pick a card at random.

    prompt_text()
        Get context-sensitive wording for the prompt at the bottom of the screen
    """
    def __init__(self, data: str):
        """
        Parameters:
            data:           data in JSON format
        """
        try:
            js_data = json.loads(data)
        except(json.decoder.JSONDecodeError) as json_ex:
            raise ConfigurationError(f"Configuration data could not be parsed: {data}")
        try:
            self.deck_name = js_data['name']
            self.display_template = js_data['display_template']
            raw_data = js_data['data']
            try:
                self.numbered = js_data['numbered']
            except:
                self.numbered = False
            self.data = []
            self.topics = {}
            for item in raw_data:
                next_title = item['title']
                for existing_card in self.data:
                    existing_title = existing_card['title']
                    if existing_title == next_title:
                        raise ConfigurationError(f"Duplicate card: {next_title}")
                self.data.append(Card(item.pop('title'), **item))
            if 'topics' in js_data:
                topic_list = js_data['topics']
                for item in topic_list:
                    for table in item.values():
                        menu_char = table['character']
                        if menu_char == DEFAULT_RANDOM_MENU_CHAR:
                            raise ConfigurationError(
                                f"The character \'{DEFAULT_RANDOM_MENU_CHAR}\' " \
                                "is reserved for the system menu."
                            )
                        if self.numbered is True and menu_char == DEFAULT_NUMBERED_MENU_CHAR:
                            raise ConfigurationError(
                                f"The character \'{DEFAULT_NUMBERED_MENU_CHAR}\' " \
                                "is reserved for the system menu."
                            )
                    self.topics.update(item)
        except(KeyError) as key_ex:
            raise ConfigurationError(f"System misconfigured: {str(key_ex)}")
        self.current_menu_level = MAIN_MENU_LEVEL

    def choose_card(self, number: int):
        """
        Choose a card by a 1-indexed ordinal number.

        Parameters:
            number:             the 1-indexed position of the card
        """
        self.current_menu_level = CARD_FRONT_DISPLAY_LEVEL
        return self.data[number - 1]

    def __len__(self):
        """The number of cards in this deck"""
        return len(self.data)

    def __getitem__(self, key):
        """Get a specific card"""
        count = 0
        for card in self.data:
            if card['title'] == key:
                return self.data[count]
            else:
                count += 1
        raise CardNotFoundError(f"Card not found for key '{key}'")

    def list(self, for_topic: str=None):
        """
        Show all cards, or cards on a certain topic

        Parameters:
            for_topic:      the topic all of these cards have in common
        """
        result = []
        for i in range(len(self.data)):
            card = self.data[i]
            if for_topic is None:
                result.append(card)
            elif for_topic in self.topics:
                members = self.topics[for_topic]['members']
                if card.title in members:
                    result.append(card)
        self.current_menu_level = TOPIC_DISPLAY_LEVEL
        return result

    def random_card(self):
        """
        Pick a card at random
        """
        n = random.randint(0, len(self.data)-1)
        return self.choose_card(n)

    def main_menu(self):
        """
        Build a menu for this deck

        A menu should have at least one option: to view a random
        card. Other menu options must be added based upon the contents
        of the ``self.topics`` dictionary.

        Returns:    an ordered container of dictionaries.
        """
        result = []
        if self.numbered == True:
            result.append({
                'character' : DEFAULT_NUMBERED_MENU_CHAR,
                'prompt' : "To view a card by ordinal number, press \'" +\
                           f"{DEFAULT_NUMBERED_MENU_CHAR}\'"
            })
        result.append({
            'character' : DEFAULT_RANDOM_MENU_CHAR,
            'prompt' : "To view a random card, press \'" +\
                       f"{DEFAULT_RANDOM_MENU_CHAR}\'"
        })
        if len(self.topics) > 0:
            for name, hashtable in self.topics.items():
                topic_prompt = f"To view a list of {hashtable['prompt']}, " +\
                               f"press \'{hashtable['character']}\'"
                result.append({
                    'character' : hashtable['character'],
                    'prompt' : topic_prompt
                })
        return result

    def find_topic(self, prompt_char: str):
        """
        Find the topic for a given prompt character

        Parameters:

            prompt_char:        one-character symbol representing the topic
        """
        for name, hashtable in self.topics.items():
            if hashtable['character'] == prompt_char:
                return name
        return None

    def prompt_text(self):
        """Get context-sensitive prompt"""
        if self.current_menu_level == MAIN_MENU_LEVEL:
            return DEFAULT_PROMPT
        elif (self.current_menu_level == CARD_FRONT_DISPLAY_LEVEL):
            return '\'' + DEFAULT_MAIN_MENU_CHAR + \
                          '\': main menu;  ' + \
                          '\'' + DEFAULT_TOGGLE_CHAR + \
                          '\': view back of card; ' + \
                          DEFAULT_PROMPT
        elif (self.current_menu_level == CARD_BACK_DISPLAY_LEVEL):
            return '\'' + DEFAULT_MAIN_MENU_CHAR + \
                          '\': main menu;  ' + \
                          '\'' + DEFAULT_TOGGLE_CHAR + \
                          '\': view front of card; ' + \
                          DEFAULT_PROMPT
        else:
            return DEFAULT_PROMPT

def block_padding(text: list, x_width: int):
    """
    When several lines of text are displayed as a block, left-aligned,
    calculate a general padding value for the whole block. Ignore separators.

    Parameters:
        text:           ordered container of text that is about to be
                        displayed
        x_width:        total width of the display window
    """
    text_only = [x for x in text if(type(x) == str)]
    longest_line = sorted(text_only, key=lambda x: len(x), reverse=True)[0]
    return (x_width // 2) - (len(longest_line) // 2)

def do_loop(stdscr, deck):
    """
    The main loop is broken into three parts: 1) displaying the right screen;
    2) getting input; and 3) deciding what to do with the input.

    Parameters:
        stdscr:         handle to curses viewport
        deck:           ``Deck`` object containing the cards to be displayed
    """
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(TITLE_STYLE, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(MENU_STYLE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(TEXT_STYLE, curses.COLOR_WHITE, curses.COLOR_BLACK)
    screen_height, screen_width = stdscr.getmaxyx()
    main_window = curses.newwin(screen_height - 2, screen_width - 1, 0, 0)
    prompt_bar = curses.newwin(1, screen_width - 1, screen_height - 2, 0)
    chosen_card = None
    while(True):
        stdscr.clear()
        main_window.clear()
        prompt_bar.clear()
        y_index = 0
        # 1) DISPLAY...
        if deck.current_menu_level == MAIN_MENU_LEVEL:
            menu_contents = deck.main_menu()
            menu_height = len(menu_contents)
            y_index = (screen_height // 2) - (menu_height // 2)
            for menu_item in menu_contents:
                show_text(menu_item["prompt"], y_index,
                                    screen_width, main_window,
                                    alignment=CENTERED,
                                    color=TITLE_STYLE,
                                    mode=curses.A_BOLD)
                y_index += 1
            show_text(deck.prompt_text(), 0, screen_width, prompt_bar,
                                color=MENU_STYLE, mode=curses.A_BOLD)
        elif (deck.current_menu_level == CARD_FRONT_DISPLAY_LEVEL) or \
             (deck.current_menu_level == CARD_BACK_DISPLAY_LEVEL):
            if deck.numbered:
                num = deck.data.index(chosen_card) + 1
            else:
                num = None
            if deck.current_menu_level == CARD_FRONT_DISPLAY_LEVEL:
                card_contents = chosen_card.display(deck.display_template,
                                                    deck.topics, num,
                                                    front=True)
            else:
                card_contents = chosen_card.display(deck.display_template,
                                                    deck.topics, num,
                                                    front=False)
            y_index = (screen_height // 2) - (len(card_contents) // 2)
            for line in card_contents:
                show_text( line, y_index, screen_width, main_window,
                                        alignment=LEFT_ALIGNED,
                                        left_padding=block_padding(card_contents,
                                            screen_width)
                                        )
                y_index += 1
            show_text(deck.prompt_text(), 0, screen_width, prompt_bar,
                                color=MENU_STYLE, mode=curses.A_BOLD)
        elif deck.current_menu_level == TOPIC_DISPLAY_LEVEL:
            lines = []
            p = Paginator(  centered = False,
                            quit_prompt = f"{DEFAULT_MAIN_MENU_CHAR}: main menu",
                            quit_char = 'm', prompt_color=MENU_STYLE,
                            prompt_mode=curses.A_BOLD)
            for card in chosen_cards:
                for line in card.display(deck.display_template, deck.topics):
                    lines.append(line)
                    y_index += 1
                if len(chosen_cards) > 1 and \
                    chosen_cards.index(card) < (len(chosen_cards) - 1):
                    lines.append(SeparatorMarker(color=MENU_STYLE,
                                                 mode=curses.A_BOLD))
                    y_index += 1
            p.left_padding = block_padding(lines, screen_width)
            try:
                stdscr.refresh()
                p.paginate(stdscr, lines)
            except(PaginatorException):
                deck.current_menu_level = MAIN_MENU_LEVEL
                continue
        elif deck.current_menu_level == NUMBER_INPUT_LEVEL:
            pass
        else:
            center("UNDER CONSTRUCTION", 0, screen_width, main_window)
            center(deck.prompt_text(), 0, screen_width, prompt_bar)
            deck.current_menu_level = MAIN_MENU_LEVEL
        main_window.border()
        main_window.addstr(0,
                          (screen_width // 2) - (len(deck.deck_name) // 2),
                          deck.deck_name,
                          curses.A_BOLD)
        main_window.refresh()
        prompt_bar.refresh()
        # 2) GET INPUT
        if deck.current_menu_level == NUMBER_INPUT_LEVEL:
            number_prompt = "Enter the number: "
            stdscr.clear()
            stdscr.addstr(
                (screen_height // 2),
                (screen_width // 2) - (len(number_prompt) // 2),
                number_prompt, curses.color_pair(MENU_STYLE))
            curses.curs_set(2)
            curses.echo()
            stdscr.refresh()
            key = stdscr.getstr(
                (screen_height // 2),
                (screen_width // 2) + (len(number_prompt) // 2)
            ).decode("utf-8")
            curses.curs_set(0)
            try:
                if (int(key) > deck.data.__len__()) or (int(key) < 1):
                    error_prompt = "You can only enter a number between 1 and " +\
                                   f"{deck.data.__len__()}"
                    stdscr.addstr(
                        (screen_height // 2),
                        (screen_width // 2) - (len(error_prompt) // 2),
                        error_prompt, curses.color_pair(MENU_STYLE))
                    show_text("Press any key to continue...",
                            (screen_height - 2), screen_width, stdscr)
                    stdscr.getch()
                    continue
                else:
                    chosen_card = deck.choose_card(int(key))
                    continue
            except(ValueError):
                continue
        else:
            char1 = prompt_bar.getch()
        # 3) DECIDE WHAT TO DO WITH INPUT
        if char1 == 27: # ESC key...
            break
        elif deck.current_menu_level == MAIN_MENU_LEVEL:
            if char1 == ord(DEFAULT_RANDOM_MENU_CHAR):
                chosen_card = deck.random_card()
                continue
            elif char1 == ord(DEFAULT_NUMBERED_MENU_CHAR):
                if deck.numbered:
                    deck.current_menu_level = NUMBER_INPUT_LEVEL
                else:
                    continue
            else:
                chosen_topic = deck.find_topic(chr(char1))
                if chosen_topic == None:
                    continue
                chosen_cards = deck.list(for_topic=chosen_topic)
                deck.current_menu_level = TOPIC_DISPLAY_LEVEL
        elif char1 == ord(DEFAULT_TOGGLE_CHAR):
            if deck.current_menu_level == CARD_FRONT_DISPLAY_LEVEL:
                deck.current_menu_level = CARD_BACK_DISPLAY_LEVEL
            else:
                deck.current_menu_level = CARD_FRONT_DISPLAY_LEVEL
            continue
        elif (deck.current_menu_level == CARD_FRONT_DISPLAY_LEVEL) or \
             (deck.current_menu_level == CARD_BACK_DISPLAY_LEVEL):
            if char1 == ord(DEFAULT_MAIN_MENU_CHAR):
                deck.current_menu_level = MAIN_MENU_LEVEL
        else:
            deck.current_menu_level = 99

if __name__ == "__main__":
    try:
        with open(sys.argv[1]) as sourcefile:
            cards = Deck(sourcefile.read())
    except(IndexError):
        print("ERROR: please specify a source file for the data")
        quit()
    except(Exception) as cfg_ex:
        print(f"Error in source file: {str(cfg_ex)}")
        quit()

    curses.wrapper(do_loop, cards)
