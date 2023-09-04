from vectors import VectorDB 

class Memory:

    def __init__(self, agent):
        self.db = VectorDB()
        self.agent = agent

    def query(self, vector):
        results = self.db.search(vector)
        return results

    def add(self, vector, experience):
        self.db.add(vector, experience) 
