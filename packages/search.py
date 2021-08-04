from Structs.pending import Pending
import random
from packages import VIP
from SDK.keyboard import Keyboard
from Structs.profile import Profile
from message_utils import send_continue_action, update_options
from utils import parseInt, send_profile
from SDK.cmd import after_func, set_after


@after_func("react_profile")
def react_profile(self, args):
    profile_id = args[0]
    if self.text == '❤':
        self.write(profile_id, "Кому-то понравилась твоя анкета. Перейдите в режим оценивания людей, которым вы понравились для дальнейших действий.")
        Pending(self.db, peer_id = profile_id, sender_id = self.user.id)
        random_profile(self)
    elif self.text == '💌':
        self.reply("Введите сообщение для пользователя.")
        self.set_after("add_message", args)
    elif self.text == '💬':
        self.write(profile_id, "Кто-то просит вас войти в чат. Перейдите в режим оценивания людей, которым вы понравились для дальнейших действий.")
        Pending(self.db, peer_id = profile_id, sender_id = self.user.id, chat = True)
        random_profile(self)
    elif self.text == '👎':
        VIP.add_to_histoy(self, profile_id)
        random_profile(self)
    elif self.text == '💤':
        send_continue_action(self)
    else:
        self.reply("Действие не распознано. Попробуй еще раз")
        return True
        
@after_func("add_message")
def add_message(self, args):
    profile_id = args[0]
    self.write(profile_id, f"Кому-то понравилась твоя анкета. Перейдите в режим оценивания людей, которым вы понравились для дальнейших действий.\nСообщение для тебя: {self.raw_text}")
    Pending(self.db, peer_id = profile_id, sender_id = self.user.id, message = self.raw_text)
    random_profile(self)

def random_profile(self):
    user_profile = Profile(self.db, user_id = self.user.id)
    user_profile.active = 1
    random_profiles = self.db.select_all_structs("SELECT * FROM profiles where city = ? and (gender = ? or ? = 3 or gender = 3) and user_id != ? and active = 1 ORDER BY RANDOM() LIMIT 5", [user_profile.city, user_profile.searching_for, user_profile.searching_for, self.user.id])
    if len(random_profiles) == 0:
        self.reply("Мне не удалось никого для тебя найти, возвращайся позже.")
        send_continue_action(self)
        return
    choice = random.choice(random_profiles)
    send_profile(self, choice.user_id, self.user.id, "Нашел кое-кого для тебя, смотри:\n\n", {"❤": "green", "💌": "blue", "👎": "red", "💬":"white", "💤": "blue"})
    self.set_after("react_profile", [choice.user_id])

@after_func("continue_action")
def continue_action(self):
    action = parseInt(self.text)
    has_pending = len(self.db.select("select * from pending where peer_id = ?", [self.user.id])) > 0
    vip = Profile(self.db, user_id = self.user.id).vip
    if not action or action < 0 or action > 6:
        self.reply("Нет такого варианта ответа. Попробуйте еще раз.")
        return True
    if action == 1:
        send_profile(self, self.user.id, self.user.id, "Так выглядит твоя анкета:\n\n")
        return True
    elif action == 2:
        update_options(self)
    elif action == 3:
        random_profile(self)
    elif action == 4:
        Profile(self.db, user_id = self.user.id).active = 0
        self.reply("Ваша анкета отключена и больше не будет появляться в поиске.", keyboard = Keyboard.get_empty_keyboard())
    elif action == 5 and has_pending and not vip:
        browse_pending(self)
    elif action == 5 and not has_pending and vip:
        VIP.browse_history(self, 0)
    elif action == 5 and vip:
        browse_pending(self)
    elif action == 6 and vip:
        VIP.browse_history(self, 0)

@after_func("handle_pending")
def handle_pending(self):
    pending = self.db.select_one_struct("select * from pending where peer_id = ? ORDER BY rowid DESC LIMIT 1", [self.user.id])
    if self.text == "❤" and not pending.chat:
        self.reply(f"Вот ссылка на пользователя:\nvk.com/id{pending.sender_id}\nЖелаю приятного общения!")
    elif self.text == "💬" and pending.chat:
        self.reply("Вы вошли в чат. Напишите \"Выйти\", чтобы выйти из чата.", keyboard = Keyboard.get_empty_keyboard())
        send_profile(self, pending.peer_id, pending.sender_id, "Похоже, кто-то принял ваш запрос на чат. Напишите \"Выйти\", чтобы выйти из чата.\nАнкета пользователя:\n\n", Keyboard.get_empty_keyboard())
        peer_profile = Profile(self.db, user_id = pending.peer_id)
        sender_profile = Profile(self.db, user_id = pending.sender_id)
        peer_profile.chatting_with = sender_profile.user_id
        sender_profile.chatting_with = peer_profile.user_id
        pending.destroy()
        self.set_after("handle_chat")
        set_after("handle_chat", sender_profile.user_id)
        return
    pending.destroy()
    if len(self.db.select("select * from pending where peer_id = ?", [self.user.id])) > 0:
        browse_pending(self)
    else:
        random_profile(self)


def browse_pending(self):
    pending = self.db.select_one_struct("select * from pending where peer_id = ? ORDER BY rowid DESC LIMIT 1", [self.user.id])
    self.set_after("handle_pending")
    if len(pending.message) > 0:
        send_profile(self, pending.sender_id, pending.peer_id, f"Сообщение для тебя: {pending.message}\nАнкета:\n\n", {"❤": "green", "👎": "red"})
    elif not pending.chat:
        send_profile(self, pending.sender_id, pending.peer_id, "Анкета:\n\n", {"❤": "green", "👎": "red"})
    else:
        send_profile(self, pending.sender_id, pending.peer_id, "Пользователь приглашает вас в чат.\nАнкета:\n\n", {"💬": "green", "👎": "red"})