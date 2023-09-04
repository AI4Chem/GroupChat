from base import Base

class Topic(Base):
    def __init__(self, name):
        self.name = name
        self.members = []

    def add_member(self, member):
        self.members.append(member)

    def serialize(self):
        data = {
            "name": self.name,
            "members": self.members
        }
        return super().serialize(data)