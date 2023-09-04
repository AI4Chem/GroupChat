from base import Base

class Message(Base):
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content

    def serialize(self):
        data = {
            "sender": self.sender,
            "content": self.content    
        }
        return super().serialize(data)