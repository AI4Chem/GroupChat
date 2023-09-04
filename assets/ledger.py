from base import Base

class AssetLedger(Base):
    def __init__(self):
        self.assets = {}
        
    def add_asset(self, name, amount, owner):
        self.assets[name] = {
            "amount": amount,
            "owner": owner
        }

    def transfer(self, name, amount, from_agent, to_agent):
        asset = self.assets[name]
        if asset["owner"] != from_agent:
            return False 
        
        asset["amount"] -= amount
        asset["owner"] = to_agent
        return True

    def serialize(self):
        return super().serialize(self.assets)