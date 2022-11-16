class ChatClient:
    def __init__(self, client_id, read_chunk_size=100):
        self._id = client_id
        # books probably need to be an instance
        self.read_chunk_size = read_chunk_size # 100 chars per chunk default message length
        self.qty_of_owned_books = 0
        # self.read_progress = {"book_id": chunk_index}
        self.read_progress = dict()
        # self.currently_reading = book_id
        self.current_read_target = None
        self.books = None
        self.using_bot_flag = True

    def get_books(self):
        return self.books

    def get_current_reading_book(self, target_id):
        """
        in case user decides to read another book
        """
        self.current_read_target = target_id

    def get_current_reading_book(self):
        return self.current_read_target
    
    def from_dict(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])