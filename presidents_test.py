import unittest
import presidents

class TestInitialization(unittest.TestCase):

    def test_load_data(self):
        import subprocess
        cp = subprocess.run(
            ["wc", "-l", "presidents.tsv"],
            capture_output=True
        )
        output = cp.stdout.decode("utf-8").split(' ')
        total_presidents = int(output[0])
        presidents.load_data()
        self.assertEqual(len(presidents.presidents), total_presidents)

if __name__ == '__main__':
    unittest.main()
