#
# flashcards.py
#
# A configurable learning tool.
#

import json, re, sys, random, curses, screen_utils

DEFAULT_RANDOM_MENU_CHAR    = 'r'
DEFAULT_NUMBERED_MENU_CHAR  = 'n'
DEFAULT_MAIN_MENU_CHAR      = 'm'
MAIN_MENU_LEVEL             = 0
CARD_DISPLAY_LEVEL          = 1
TOPIC_DISPLAY_LEVEL         = 2
NUMBER_INPUT_LEVEL          = 3
TOPIC_INPUT_LEVEL           = 4

class ConfigurationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class CardNotFoundError(Exception):
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

    def display(self, template, topics={}, number=None):
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
            number:     the ordinal position of this card in the deck
        """
        result = []
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
    def __init__(self, data: str):
        """
        Initialize the deck

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

    def choose_card(self, number):
        self.current_menu_level = CARD_DISPLAY_LEVEL
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
        of the ``self.topics`` dictionary. The result will be an ordered
        container of dictionaries.
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

def do_loop(stdscr, deck):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(screen_utils.TITLE_STYLE, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(screen_utils.MENU_STYLE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(screen_utils.TEXT_STYLE, curses.COLOR_WHITE, curses.COLOR_BLACK)
    screen_height, screen_width = stdscr.getmaxyx()
    main_window = curses.newwin(screen_height - 2, screen_width - 1, 0, 0)
    prompt_bar = curses.newwin(1, screen_width - 1, screen_height - 2, 0)
    default_prompt = 'press the [ESC] key to quit'
    card_display_prompt = '\'' + DEFAULT_MAIN_MENU_CHAR + \
                          '\': main menu;  ' + default_prompt
    chosen_card = None
    while(True):
        # The main loop is broken into three parts:
        # 1) display the right screen;
        # 2) get input; and
        # 3) decide what to do with the input
        stdscr.clear()
        main_window.clear()
        prompt_bar.clear()
        y_index = 0
        # 1) DISPLAY...
        if deck.current_menu_level == MAIN_MENU_LEVEL:
            for menu_item in deck.main_menu():
                main_window.addstr(y_index, 0, menu_item["prompt"])
                screen_utils.center(menu_item["prompt"], y_index,
                                    screen_width, main_window)
                y_index += 1
            screen_utils.center(default_prompt, 0, screen_width, prompt_bar)
        elif deck.current_menu_level == CARD_DISPLAY_LEVEL:
            if deck.numbered:
                num = deck.data.index(chosen_card) + 1
            else:
                num = None
            for line in chosen_card.display(deck.display_template, deck.topics, num):
                screen_utils.center(line, y_index, screen_width, main_window)
                y_index += 1
            screen_utils.center(card_display_prompt, 0, screen_width, prompt_bar)
        elif deck.current_menu_level == TOPIC_DISPLAY_LEVEL:
            screen_utils.center("You have chosen a topic. Congratulations.", 0,
                                 screen_width, main_window)
            screen_utils.center(card_display_prompt, 0, screen_width, prompt_bar)
            deck.current_menu_level = MAIN_MENU_LEVEL
        elif deck.current_menu_level == NUMBER_INPUT_LEVEL:
            screen_utils.center("You are about to choose a number. Congratulations.", 0,
                                 screen_width, main_window)
            screen_utils.center(card_display_prompt, 0, screen_width, prompt_bar)
        else:
            screen_utils.center("UNDER CONSTRUCTION", 0, screen_width, main_window)
            screen_utils.center(card_display_prompt, 0, screen_width, prompt_bar)
            deck.current_menu_level = MAIN_MENU_LEVEL
        main_window.refresh()
        prompt_bar.refresh()
        # 2) GET INPUT
        if deck.current_menu_level == NUMBER_INPUT_LEVEL:
            number_prompt = "Enter the number: "
            stdscr.clear()
            stdscr.addstr(
                (screen_height // 2),
                (screen_width // 2) - (len(number_prompt) // 2),
                number_prompt, curses.color_pair(screen_utils.MENU_STYLE))
            curses.curs_set(2)
            curses.echo()
            stdscr.refresh()
            key = stdscr.getstr(
                (screen_height // 2),
                (screen_width // 2) + (len(number_prompt) // 2)
            ).decode("utf-8")
            curses.curs_set(0)
            if (int(key) > deck.data.__len__()) or (int(key) < 1):
                error_prompt = "You can only enter a number between 1 and " +\
                               f"{deck.data.__len__()}"
                stdscr.addstr(
                    (screen_height // 2),
                    (screen_width // 2) - (len(error_prompt) // 2),
                    error_prompt, curses.color_pair(screen_utils.MENU_STYLE))
                screen_utils.center("Press any key to continue...",
                        (screen_height - 2), screen_width, stdscr)
                stdscr.getch()
                continue
            else:
                chosen_card = deck.choose_card(int(key))
                deck.current_menu_level = CARD_DISPLAY_LEVEL
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
        elif deck.current_menu_level == CARD_DISPLAY_LEVEL:
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
