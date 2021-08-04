from Structs.profile import Profile
from utils import send_profile
from SDK.cmd import set_after
from SDK.keyboard import Keyboard

def send_continue_action(self, user_id = None):
    user_id = user_id or self.user.id
    keyboard = Keyboard({"1": "green", "2": "blue", "3": "white", "4": "red"})
    message = "Что ты хочешь сделать?\n 1 - Посмотреть анкету\n2 - Изменить анкету\n3 - Оценить кого-то\n4 - Отключить анкету"
    has_pending = len(self.db.select("select * from pending where peer_id = ?", [user_id])) > 0
    vip = Profile(self.db, user_id = user_id).vip
    if has_pending and not vip:
        message += "\n5 - Посмотреть людей, которым понравилась анкета"
        keyboard += {"5": "green"}
    elif has_pending and vip:
        message += "\n5 - Посмотреть людей, которым понравилась анкета\n\n6 - Посмотреть историю"
        keyboard += {"5": "green", "6": "blue"}
    elif not has_pending and vip:
        message += "\n5 - Посмотреть историю"
        keyboard += {"5": "blue"}
    self.write(user_id, message, keyboard)
    set_after("continue_action",user_id)

def confirm_message(self):
    send_profile(self, self.user.id, self.user.id,
                 "Твоя анкета выглядит так:\n\n")
    self.reply("Все верно? \n\n1. Да, все верно.\n2. Изменить анкету",
               keyboard={"1": "green", "2": "red"})
    self.set_after("confirm_profile")

def update_options(self):
    self.reply("Что именно ты хочешь сделать?\n 1. Изменить фото анкеты.\n2. Заполнить анкету заново.\n3. Добавить еще фото к моей анкете.\n4. Добавить к моей анкете голосовое сообщение.\n5. Изменить текст анкеты.\n6. Удалить фото из анкеты.", keyboard={"1":"green","2":"red","3":"blue","4":"white","5":"blue","6":"red"})
    self.set_after("choose_update_profile_option")