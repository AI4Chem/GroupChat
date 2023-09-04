
from base import Base

class Agent(Base):
    def __init__(self):
        self.name = ""
        self.memory = Memory(self) 

    def remember(self, experience):
        self.memory.add(experience)

    def serialize(self):
        data = {
            "name": self.name
        }
        return super().serialize(data) 