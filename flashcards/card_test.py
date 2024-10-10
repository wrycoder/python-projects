import unittest, re
from flashcards import Card, Deck, ConfigurationError, CardEncoder
import json

COLONIES = '''
{
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
    "All about the {card['title']} Colony"
  ]
}
'''

SCIENTISTS = '''
{
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

class CardTest(unittest.TestCase):
    def test_load_deck(self):
        with self.assertRaises(ConfigurationError):
            colonies = Deck('foo', 'baz')
        colonies = Deck('colony', COLONIES)
        self.assertEqual(len(colonies), 13, "Incorrect number of cards")
        self.assertEqual(
            colonies[4]['capital'],
            "Boston",
            "Incorrect capital for colony"
        )

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
        test_list = [curie]
        scientists = Deck('scientist', SCIENTISTS)
        self.assertEqual(len(scientists), 1, "Incorrect number of cards")
        self.assertTrue(
            re.match(r'^All About Marie Curie.*', scientists.display_all()) != None,
            "Title of test card not found"
        )
        birth_year = re.findall(r'.+1867.+', scientists.display_all(), re.MULTILINE)
        self.assertEqual(len(birth_year), 1, "Detail not found")
        death_year = re.findall(r'.+1934\.', scientists.display_all(), re.MULTILINE)
        self.assertEqual(len(death_year), 1, "Detail not found")
        birthplace = re.findall(r'.+Warsaw.+', scientists.display_all(), re.MULTILINE)
        self.assertEqual(len(birthplace), 1, "Detail not found")

if __name__ == "__main__":
    unittest.main()

