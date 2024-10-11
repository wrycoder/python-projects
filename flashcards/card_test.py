import unittest, re
from flashcards import Card, Deck, ConfigurationError, CardEncoder
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
        "prompt" : "Colonies that Farmed Tobacco",
        "detail" : ["{card['title']} was a tobacco-farming colony"],
        "members" : ["North Carolina", "Virginia", "Maryland"]
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

    def test_display_all(self):
        scientists = Deck(SCIENTISTS)
        self.assertEqual(len(scientists), 1, "Incorrect number of cards")
        sample_text = '\n'.join(scientists.display_all())
        self.assertTrue(
            re.match(r'^All About Marie Curie.*', sample_text) != None,
            "Title of test card not found"
        )
        birth_year = re.findall(r'.+1867.+', sample_text, re.MULTILINE)
        self.assertEqual(len(birth_year), 1, "Birth year not found in deck display")
        death_year = re.findall(r'.+1934\.', sample_text, re.MULTILINE)
        self.assertEqual(len(death_year), 1, "Death year not found in deck display")
        birthplace = re.findall(r'.+Warsaw.+', sample_text, re.MULTILINE)
        self.assertEqual(len(birthplace), 1, "Birthplace not found in deck display")

    def test_display_all_filtered(self):
        colonies = Deck(COLONIES)
        self.assertEqual(len(colonies), 13, "Incorrect number of cards")
        tobacconists = colonies.display_all(for_topic='tobacco')
        self.assertEqual( len(tobacconists), 9,
                          "There should be 3 lines of text for each "\
                          "of the 3 tobacco-producing colonies")
        js_data = json.loads(COLONIES)
        detail_string = js_data['topics'][0]['tobacco']['detail'][0]
        sample_member = js_data['topics'][0]['tobacco']['members'][0]
        formatted_string = re.sub(r'\{card\[\'title\'\]\}', sample_member, detail_string)
        self.assertTrue(formatted_string in tobacconists)

    def test_random_card(self):
        colonies = Deck(COLONIES)
        card = colonies.random_card()
        self.assertEqual(type(card), type(colonies['Massachusetts']))

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
        hosts = Deck('host', numbered_json_string)
        card = hosts.get_item(2)
        self.assertEqual(card.title, 'Ryan Seacrest', "Incorrect card for given number")
        with self.assertRaises(ConfigurationError):
          colonies = Deck('colony', COLONIES)
          card = colonies.get_item(2)
          tv_witches = Deck('witch', numbered_false_json_string)
          card = tv_witches.get_item(2)

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

if __name__ == "__main__":
    unittest.main()

