class Book:
    def __init__(self, title, owner):
        self.title = title
        # owner - owner id
        self.owner = owner
        self.content = None
    
    def modify_content(self, content):
        self.content = content