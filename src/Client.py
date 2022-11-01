class ChatClient:
    def __init__(self, client_id, books, books_quantity, read_progress):
        self.client_id = client_id
        # books probably need to be an instance
        self.books = books
        self.books_quantity = books_quantity
        # is this needed?
        self.read_progress = read_progress

    def get_books(self):
        return self.books

    def get_books_quantity(self):
        return self.books_quantity

    # must be in client field
    def get_read_progress(self):
        return self.read_progress
