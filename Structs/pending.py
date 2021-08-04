from SDK.database import ProtectedProperty, Struct

class Pending(Struct):
    def __init__(self, *args, **kwargs):
        self.save_by = ProtectedProperty(["peer_id", "sender_id"])
        self.sender_id = 0
        self.peer_id = 0
        self.message = ""
        self.chat = False
        super().__init__(*args, **kwargs)