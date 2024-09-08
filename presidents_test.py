import unittest
from presidents import presidents, load_data, President

class TestInitialization(unittest.TestCase):

    def test_load_data(self):
        import subprocess
        cp = subprocess.run(
            ["wc", "-l", "presidents.tsv"],
            capture_output=True
        )
        output = cp.stdout.decode("utf-8").split(' ')
        total_presidents = int(output[0])
        load_data()
        self.assertEqual(len(presidents), total_presidents)

    def test_president_class(self):
        pres = President('1', "Hans Schmidt", '2071', 'ND',
                                    'he/him/his', 'Republican')
        self.assertEqual(pres.key, 1)
        self.assertEqual(pres.state, 'North Dakota')
        self.assertEqual(pres.name, 'Hans Schmidt')
        self.assertEqual(pres.party, 'Republican')
        self.assertEqual(pres.sworn_in, 2071)
        self.assertEqual(pres.pronouns, 'he/him/his')

    def test_pronoun_method(self):
        hilda = President('1', 'Hilda Hansen', '2044', 'NE',
                        'she/her/her', 'Democratic')
        sven = President('2', 'Sven Borgmansson', '2075', 'NY',
                        'they/them/their', 'Revolutionary')
        bob = President('3', 'Bob White', '2040', 'OK',
                        'he/him/his', 'Republican')
        self.assertEqual(sven.pronoun('possessive'), 'their')
        self.assertEqual(bob.pronoun('subject'), 'he')
        self.assertEqual(hilda.pronoun('object'), 'her')

if __name__ == '__main__':
    unittest.main()
