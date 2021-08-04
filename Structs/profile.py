from SDK.database import ProtectedProperty, Struct


class Profile(Struct):
    def __init__(self, *args, **kwargs):
        self.table_name = ProtectedProperty("profiles")
        self.save_by = ProtectedProperty("user_id")
        self.user_id = 0
        self.age = 0
        self.gender = 0
        self.profile_text = ""
        self.active = 0
        self.profile_photo = ""
        self.voice_message = ""
        self.photos = []
        self.searching_for = 0
        self.lat = 0
        self.display_name = ""
        self.long = 0
        self.chatting_with = ""
        self.city = ""
        self.history = []
        self.vip = True
        super().__init__(*args, **kwargs)

    def len_attachments(self, factor_voice_message=True):
        return len(self.display_name) > 0 + len(self.photos) + len(self.voice_message) > 0 and factor_voice_message + len(self.profile_photo) > 0
