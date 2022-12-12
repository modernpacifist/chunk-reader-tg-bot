class Book:
    def __init__(self, owner_id, title, content, index=1, content_length=1):
        self.owner_id = owner_id
        self.title = title
        self.content = content
        self.index = index
        self.content_length = content_length
        self.shared = False

    # TODO: implement later
    def from_dict(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
