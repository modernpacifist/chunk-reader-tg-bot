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

    def get_book_progress(self, book: dict):
        # this is unsafe
        book_title = book.get('title')
        if book_title is None:
            return None
        
        if self.read_progress[book_title] == 0:
            return None

        return float( self.read_progress[book_title] / book.get('content_length')) * 100

    def get_current_reading_book(self, target_id):
        """
        in case user decides to read another book
        """
        self.current_read_target = target_id

    def from_dict(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
