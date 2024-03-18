import unittest


class MathTest(unittest.TestCase):
    def test_1_plus_1(self):
        self.assertEqual(1 + 1, 2)


if __name__ == "__main__":
    unittest.main()
