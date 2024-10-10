import unittest, re
from flashcards import Card, Deck, ConfigurationError, CardEncoder
import json

COLONIES = '''
[
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
]
'''

class CardTest(unittest.TestCase):
    def test_load_deck(self):
        with self.assertRaises(ConfigurationError):
            colonies = Deck('foo', 'bar', 'baz')
        colonies = Deck('colony', 'All About the {card["title"]} Colony', COLONIES)
        self.assertEqual(len(colonies), 13, "Incorrect number of cards")
        self.assertEqual(
            colonies[4]['title'],
            "Massachusetts",
            "Incorrect title for card"
        )

    def test_display_card(self):
        curie = Card(
            "Marie Curie",
            birthplace="Warsaw",
            born_in=1867,
            died_in=1934
        )
        self.assertEqual(
            curie['born_in'],
            1867,
            "Incorrect value for specified key"
        )
        test_list = [curie]
        scientists = Deck('scientist', 'All About {card["title"]}', json.dumps(test_list, cls=CardEncoder))
        self.assertEqual(len(scientists), 1, "Incorrect number of cards")
        self.assertTrue(
            re.match(r'All About Marie Curie', scientists.display_all()) != None,
            "Title of test card not found"
        )

if __name__ == "__main__":
    unittest.main()

