from SDK.cmd import after_func
from message_utils import send_continue_action
from utils import send_profile
from SDK.keyboard import Keyboard
from Structs.profile import Profile

def add_to_histoy(self, add):
    user_profile = Profile(self.db, user_id = self.user.id)
    if len(user_profile.history)+1 >= self.config["history_size"]:
        del user_profile.history[0]
    user_profile.history.append(add)

def browse_history(self, idx):
    profile = Profile(self.db, user_id = self.user.id)
    history = profile.history
    if len(history) > 0:
        keyb = Keyboard({"⏪":"blue", "⏸":"green", "⏩":"blue"})
        keyb.add_line()
        keyb.add_from_dict({"💤":"white"})
        send_profile(self, history[idx], self.user.id, keyboard=keyb)
        self.set_after("react_to_browse", [idx])
    else:
        self.reply("Ваша история пуста.")
        send_continue_action(self)

@after_func("react_to_browse")
def react_to_browse(self, args):
    idx = int(args[0])
    profile = Profile(self.db, user_id = self.user.id)
    history = profile.history
    if self.text == "⏪":
        idx = idx - 1 if (idx != 0) else 0
        browse_history(self, idx)
    elif self.text == "⏩":
        idx = idx + 1 if idx+1 != self.config["history_size"]-1 and idx+1 != len(history) else 0
        browse_history(self, idx)
    elif self.text == "⏸":
        self.reply("Выберите действие для этого пользователя:", keyboard=Keyboard({"❤": "green", "💌": "blue", "👎": "red", "💬":"white", "💤": "blue"}))
        self.set_after("react_profile", [history[idx]])
    elif (self.command == "💤"):
        send_continue_action(self)