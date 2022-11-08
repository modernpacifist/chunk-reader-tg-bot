class Book:
    def __init__(self, owner_id, title, content):
        self.owner_id = owner_id
        self.title = title
        self.content = content
        self.read_progress = 0

    # def get_read_chunk(self, text_length):
    #     """
    #     get chunk from the given content by interval: [read_progress, text_length]
    #     get chunk to the closest sentence end
    #     increase read_progress by the resultant length
    #     """
    #     # read_progress is same as start position
    #     self.read_progress += text_length
    #     end_index = self.content.find('.') + 1
    #     return self.content[:self.read_progress:end_index]
    # get particular chunk size from the user
    def get_chunk_to_read(self, text_length):
        """
        get chunk from the given content by interval: [read_progress, text_length]
        get chunk to the closest sentence end
        increase read_progress by the resultant length
        """
        # read_progress is same as start position
        self.read_progress += text_length
        end_index = self.content.find('.') + 1
        return self.content[:self.read_progress:end_index]

    def get_book_info(self):
        return f"Title: {self.title},\n ReadProgress: {self.read_progress}\n"