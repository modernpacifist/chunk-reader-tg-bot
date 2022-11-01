class ChatClient:
    def __init__(self, client_id, books):
        self.client_id = client_id
        self.books = books
    
    def get_books(self):
        return self.books
