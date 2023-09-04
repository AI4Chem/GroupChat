
from .base import Message

class TextMessage(Message):
    pass

class TransferAssetMessage(Message):
    
    def __init__(self, sender, asset, receiver, amount):
        content = f"Transfer {amount} of {asset} to {receiver}"
        super().__init__(sender, content)