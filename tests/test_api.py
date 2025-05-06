import unittest
from api.books import BookStackBooksAPI
from api.chapters import BookStackChaptersAPI
from api.pages import BookStackPagesAPI

class TestBookStackBooksAPI(unittest.TestCase):
    def test_list_books(self):
        api = BookStackBooksAPI()
        books = api.list_books()
        self.assertIsInstance(books, list)

    def test_get_book(self):
        api = BookStackBooksAPI()
        books = api.list_books()
        if books:
            book = api.get_book(books[0]['id'])
            self.assertIsInstance(book, dict)

class TestBookStackChaptersAPI(unittest.TestCase):
    def test_list_chapters(self):
        api = BookStackChaptersAPI()
        # Nécessite un book_id existant
        from api.books import BookStackBooksAPI
        books = BookStackBooksAPI().list_books()
        if books:
            chapters = api.list_chapters(books[0]['id'])
            self.assertIsInstance(chapters, list)

class TestBookStackPagesAPI(unittest.TestCase):
    def test_list_pages(self):
        api = BookStackPagesAPI()
        # Nécessite un book_id existant
        from api.books import BookStackBooksAPI
        books = BookStackBooksAPI().list_books()
        if books:
            pages = api.list_pages(book_id=books[0]['id'])
            self.assertIsInstance(pages, list)

if __name__ == "__main__":
    unittest.main()
