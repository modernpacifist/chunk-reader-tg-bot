class ChatClient:
    def __init__(self, client_id, books, read_chunk_size=100):
        self.client_id = client_id
        # books probably need to be an instance
        self.books = books
        self.current_read_target = 0 # book_id
        self.read_chunk_size = read_chunk_size # 100 chars per chunk

    def get_books(self):
        return self.books

    def get_current_reading_book(self, target_id):
        """
        in case user decides to read another book
        """
        self.current_read_target = target_id

    def get_current_reading_book(self):
        return self.current_read_target