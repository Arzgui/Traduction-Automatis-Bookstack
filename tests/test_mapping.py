import unittest
from api.mapping import MappingManager

class TestMappingManager(unittest.TestCase):
    def setUp(self):
        # Utilise un mapping temporaire pour les tests
        self.test_path = 'db/test_mapping.json'
        self.manager = MappingManager(mapping_path=self.test_path)
        self.manager.mapping = {'books': {}, 'chapters': {}, 'pages': {}}
        self.manager.save_mapping()

    def tearDown(self):
        import os
        if os.path.exists(self.test_path):
            os.remove(self.test_path)

    def test_set_and_get_book(self):
        self.manager.set_book('1', 'en', 42)
        self.assertEqual(self.manager.get_book('1', 'en'), 42)

    def test_set_and_get_chapter(self):
        self.manager.set_chapter('10', 'de', 99)
        self.assertEqual(self.manager.get_chapter('10', 'de'), 99)

    def test_set_and_get_page(self):
        self.manager.set_page('100', 'en', 123)
        self.assertEqual(self.manager.get_page('100', 'en'), 123)

if __name__ == "__main__":
    unittest.main()
