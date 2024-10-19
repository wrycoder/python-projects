import unittest, re
from flashcards import *
import json

COLONIES = '''
{
  "name" : "Colony",
  "data" : [
      { "title" : "Connecticut",
        "capital" : "New Haven & Hartford"
      },
      { "title" : "Delaware",
        "capital" : "New Castle"
      },
      { "title" : "Georgia",
        "capital" : "Savannah"
      },
      { "title" : "Maryland",
        "capital" : "Annapolis"
      },
      { "title" : "Massachusetts",
        "capital" : "Boston"
      },
      { "title" : "New Hampshire",
        "capital" : "Portsmouth"
      },
      { "title" : "New Jersey",
        "capital" : "Elizabeth"
      },
      { "title" : "New York",
        "capital" : "New York"
      },
      { "title" : "North Carolina",
        "capital" : "New Bern"
      },
      { "title" : "Pennsylvania",
        "capital" : "Philadelphia"
      },
      { "title" : "Rhode Island",
        "capital" : "Newport & Providence"
      },
      { "title" : "South Carolina",
        "capital" : "Charleston"
      },
      { "title" : "Virginia",
        "capital" : "Williamsburg"
      }
  ],
  "display_template" : [
    "All about the {card['title']} Colony",
    "The capital of {card['title']} was {card['capital']}"
  ],
  "topics" : [{
    "tobacco" : {
      "character" : "t",
      "prompt" : "Colonies that farmed tobacco",
      "detail" : ["{card['title']} was a tobacco-farming colony"],
      "members" : ["North Carolina", "Virginia", "Maryland"]
    },
    "royals" : {
      "character" : "k",
      "prompt" : "Colonies that were subject to the King of England",
      "detail" : ["{card['title']} was one of the Royal Colonies, subject to the King of England"],
      "members" : ["Virginia", "New Hampshire", "New York", "New Jersey", "North Carolina", "South Carolina", "Georgia"]
    }
  }]
}
'''

SCIENTISTS = '''
{
  "name" : "Scientist",
  "data" : [
    {
      "title" : "Marie Curie",
      "birthplace" : "Warsaw",
      "born_in" : 1867,
      "died_in" : 1934
    }
  ],
  "display_template" : [
    "All About {card['title']}: ",
    "{card['title']} was born in {card['birthplace']} ",
    "in the year {card['born_in']}, and lived until {card['died_in']}."
  ]
}
'''
class ConfigTest(unittest.TestCase):
    duplicate_card_config = '''
    {
      "name" : "Comedian",
      "data" : [
        {
          "title" : "Shecky Greene"
        },
        {
          "title" : "Eddie Murphy"
        },
        {
          "title" : "Don Rickles"
        },
        {
          "title" : "Shecky Greene"
        }
      ],
      "display_template" : [],
      "numbered" : true
    }
    '''
    unpermitted_char_config = '''
    {
      "name" : "Restaurant",
      "data" : [
        {
          "title" : "Garden on the Green"
        }
      ],
      "display_template" : [],
      "topics" : [{
        "reservations" : {
          "character" : "r",
          "prompt" : "Restaurants that Require Reservations",
          "detail" : ["You need a reservation to eat at {card['title']}"],
          "members" : ["Garden on the Green"]
        }
      }]
    }
    '''
    def test_reserved_chars(self):
        with self.assertRaises(ConfigurationError):
            restaurants = Deck(self.unpermitted_char_config)

    def test_duplicate_cards(self):
        with self.assertRaises(ConfigurationError):
            comedians = Deck(self.duplicate_card_config)

class DeckTest(unittest.TestCase):
    def test_load_deck(self):
        with self.assertRaises(ConfigurationError):
            colonies = Deck('baz')
        colonies = Deck(COLONIES)
        self.assertEqual(len(colonies), 13, "Incorrect number of cards")
        self.assertEqual(
            colonies['Massachusetts']['title'],
            "Massachusetts",
            "Incorrect name for colony")
        self.assertEqual(
            colonies['Massachusetts']['capital'],
            "Boston",
            "Incorrect capital for colony"
        )

    def test_list(self):
        scientists = Deck(SCIENTISTS)
        self.assertEqual(len(scientists), 1, "Incorrect number of cards")
        curie_cards = scientists.list()[0]
        sample_text = '\n'.join(curie_cards.display(scientists.display_template))
        self.assertTrue(
            re.match(r'^All About Marie Curie.*', sample_text) != None,
            "Title of test card not found"
        )
        birth_year = re.findall(r'.+1867.+', sample_text, re.MULTILINE)
        self.assertEqual(len(birth_year), 1,
                        "Birth year not found in deck display")
        death_year = re.findall(r'.+1934\.', sample_text, re.MULTILINE)
        self.assertEqual(len(death_year), 1,
                        "Death year not found in deck display")
        birthplace = re.findall(r'.+Warsaw.+', sample_text, re.MULTILINE)
        self.assertEqual(len(birthplace), 1,
                        "Birthplace not found in deck display")
        self.assertEqual(
            scientists.current_menu_level,
            TOPIC_DISPLAY_LEVEL,
            "list() should set current_menu_level to TOPIC_DISPLAY_LEVEL")

    def test_list_filtered(self):
        total_tobacconists = 3
        colonies = Deck(COLONIES)
        self.assertEqual(len(colonies), 13, "Incorrect number of cards")
        tobacconists = colonies.list(for_topic='tobacco')
        self.assertEqual(len(tobacconists), 3, "Incorrect number of cards")
        js_data = json.loads(COLONIES)
        detail_string = js_data['topics'][0]['tobacco']['detail'][0]
        sample_member_name = js_data['topics'][0]['tobacco']['members'][0]
        formatted_string = re.sub(r'\{card\[\'title\'\]\}', sample_member_name, detail_string)
        sample_member = colonies[sample_member_name]
        output = sample_member.display(colonies.display_template, colonies.topics)
        self.assertTrue(formatted_string in output)

    def test_random_card(self):
        colonies = Deck(COLONIES)
        card = colonies.random_card()
        self.assertEqual(type(card), type(colonies['Massachusetts']))
        self.assertEqual(colonies.current_menu_level, CARD_FRONT_DISPLAY_LEVEL,
                        "current_menu_level for random card should be FRONT_DISPLAY")

    def test_numbered_card(self):
        numbered_json_string = '''
        {
          "name" : "TV Hosts",
          "data" : [
            {
              "title" : "Dick Clark"
            },
            {
              "title" : "Ryan Seacrest"
            }
          ],
          "display_template" : [],
          "numbered" : true
        }
        '''
        numbered_false_json_string = '''
        {
          "name" : "TV Witches",
          "data" : [
            {
              "title" : "Elizabeth Montgomery"
            },
            {
              "title" : "Alyssa Milano"
            }
          ],
          "display_template" : [],
          "numbered" : false
        }
        '''
        hosts = Deck(numbered_json_string)
        card = hosts.choose_card(2)
        self.assertEqual(card.title, 'Ryan Seacrest', "Incorrect card for given number")
        self.assertTrue(hosts.numbered, "List should be numbered")
        witches = Deck(numbered_false_json_string)
        self.assertFalse(witches.numbered, "List should not be numbered")

    def test_main_menu(self):
        scientists = Deck(SCIENTISTS)
        menu = scientists.main_menu()
        self.assertEqual(len(menu), 1, "Scientists main menu should have one option")
        numbered_deck_json_string = '''
        {
          "name" : "Sesame Street Characters",
          "data" : [
            {
              "title" : "Oscar the Grouch"
            },
            {
              "title" : "Grover"
            }
          ],
          "display_template" : [],
          "numbered" : true
        }
        '''
        muppets = Deck(numbered_deck_json_string)
        menu = muppets.main_menu()
        self.assertEqual(len(menu), 2, "Menu should have two options")
        colonies = Deck(COLONIES)
        menu = colonies.main_menu()
        self.assertEqual(len(menu), 3, "Menu should have three options")

    def test_choose_card(self):
        colonies = Deck(COLONIES)
        card = colonies.choose_card(2)
        self.assertEqual(card['title'], "Delaware", "method should return correct card")
        self.assertEqual(
            colonies.current_menu_level,
            CARD_FRONT_DISPLAY_LEVEL,
            "Incorrect menu level for chosen card"
        )

    def test_find_topic(self):
        colonies = Deck(COLONIES)
        self.assertEqual(colonies.find_topic('t'), 'tobacco',
            "Should be able to find topic by prompt character")
        self.assertTrue(colonies.find_topic('z') == None,
            "Search on undefined character should return None"
        )

    def test_prompt(self):
        colonies = Deck(COLONIES)
        colonies.current_menu_level = MAIN_MENU_LEVEL
        prompt = colonies.prompt_text()
        self.assertEqual(prompt.index(DEFAULT_PROMPT), 0,
                        "Main menu prompt should match DEFAULT_PROMPT")
        colonies.current_menu_level = CARD_FRONT_DISPLAY_LEVEL
        prompt = colonies.prompt_text()
        back_char_pos = prompt.index('back of card')
        self.assertTrue(back_char_pos < len(prompt),
                        "incorrect card-level display prompt for card front")
        colonies.current_menu_level = CARD_BACK_DISPLAY_LEVEL
        prompt = colonies.prompt_text()
        front_char_pos = prompt.index('front of card')
        self.assertTrue(front_char_pos < len(prompt),
                       "incorrect card-level display prompt for card back")

class CardTest(unittest.TestCase):
    def test_display_card(self):
        js_data = json.loads(SCIENTISTS)
#        print(json.dumps(js_data, indent=4))
        curie = Card(
            js_data['data'][0]['title'],
            birthplace=js_data['data'][0]['birthplace'],
            born_in=js_data['data'][0]['born_in'],
            died_in=js_data['data'][0]['died_in']
        )
        self.assertEqual(
            curie['born_in'],
            1867,
            "Incorrect value for specified key"
        )
        sample_text = '\n'.join(curie.display(js_data['display_template']))
        birth_year = re.findall(
            r'.+1867.+',
            sample_text,
            re.MULTILINE
        )
        self.assertEqual(len(birth_year), 1, "Birth year not found in card display")

    def test_display_card_front_or_back(self):
        js_data = json.loads(COLONIES)
        delaware = Card(
            js_data['data'][1]['title'],
            capital=js_data['data'][1]['capital']
        )
        self.assertEqual(
            delaware['capital'],
            js_data['data'][1]['capital'],
            "Incorrect value for specified key"
        )
        sample_text = '\n'.join(delaware.display(
                            js_data['display_template'],
                            front=True))
        with self.assertRaises(ValueError):
            colony_name = sample_text.index(delaware['title'])
        sample_text = '\n'.join(delaware.display(
                            js_data['display_template'],
                            front=False))
        colony_name_position = sample_text.index(delaware['title'])
        self.assertTrue(colony_name_position < len(sample_text),
                        "display with 'front=False' should include card title")

if __name__ == "__main__":
    unittest.main()

