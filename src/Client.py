class ChatClient:
    def __init__(self, client_id, client_name=None):
        self._id = client_id
        self.client_name = client_name
        # books probably need to be an instance
        self.read_chunk_size = 500 # 500 chars per chunk default message length
        self.qty_of_owned_books = 0
        # rename this field
        self.read_progress = dict()
        # self.currently_reading = book_id
        self.current_read_target = None
        # self.books = None
        self.using_bot_flag = True
        # 10 hours interval
        self.chunk_feed_interval = 10
        self.admin = False
        self.owned_book_indices = []

    def get_book_progress(self, book: dict):
        # this is unsafe
        book_title = book.get('title')
        if book_title is None:
            return None

        if self.read_progress.get(book_title) is None:
            return None

        # If the book is shared and no progress has been made, square brackets crash
        user_read_progress = self.read_progress.get(book_title)
        if user_read_progress is None:
            return None

        book_content_length = book.get('content_length')
        if book_content_length is None:
            book_content_length = len(book.get('content'))

        return round(float(user_read_progress / book_content_length) * 100, 2)

    def from_dict(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
