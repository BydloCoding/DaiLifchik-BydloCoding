from message_utils import send_continue_action
from SDK.cmd import after_func
from Structs.profile import Profile

@after_func("handle_chat")
def handle_chat(self):
    profile = Profile(self.db, user_id = self.user.id)
    if self.text == "выйти":
        other_profile = Profile(self.db, user_id = profile.chatting_with)
        self.write(profile.chatting_with, "Собеседник покинул чат.")
        self.reply("Вы вышли из чата!")
        send_continue_action(self)
        send_continue_action(self, profile.chatting_with)
        profile.chatting_with = 0
        other_profile.chatting_with = 0
        return
    joined = ",".join(self.attachments)
    kwargs = {"attachment": joined}
    if self.sticker_id is not None:
        kwargs["sticker_id"] = self.sticker_id
    self.write(profile.chatting_with, self.raw_text, **kwargs)
    return True