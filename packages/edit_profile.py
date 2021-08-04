from SDK.listExtension import ListExtension
from Structs.profile import Profile
from SDK.cmd import after_func
from utils import parseInt
from SDK.keyboard import Keyboard
from main import Main
from message_utils import confirm_message, send_continue_action

@after_func("choose_new_profile_photo")
def choose_new_profile_photo(self: Main):
    if (photo:=self.attachments.find(lambda it: it.startswith("photo"))) is None or self.text == "1":
        send_continue_action(self)
        return
    Profile(self.db, user_id = self.user.id).profile_photo = photo
    self.reply("Фото анкеты обновлено!")
    confirm_message(self)

@after_func("add_profile_photos")
def choose_new_profile_photos(self: Main):
    if len((photos:=self.attachments.findall(lambda it: it.startswith("photo")))) == 0 or self.text == "1":
        send_continue_action(self)
        return
    profile = Profile(self.db, user_id = self.user.id)
    if profile.len_attachments() + len(photos) > 10:
        self.reply("При добавлении фотографий будет превышен лемит вложений в 10 вложений!")
        send_continue_action(self)
        return
    profile.photos += photos
    self.reply("Фотографии добавлены к профилю!")
    confirm_message(self)

@after_func("add_voice_message")
def add_voice_message(self):
    if (audio:=self.attachments.find(lambda it: it.startswith("audio_message"))) is None or self.text == "1":
        send_continue_action(self)
        return
    profile = Profile(self.db, user_id = self.user.id)
    if profile.len_attachments() + 1 > 10:
        self.reply("При добавлении голосового сообщения будет превышен лемит вложений в 10 вложений!")
        send_continue_action(self)
        return
    profile.voice_message = audio
    self.reply("Голосовое сообщение было успешно добавлено!")
    confirm_message(self)
    
@after_func("update_text_message")
def update_text_message(self):
    if self.text == "1" or len(self.raw_text) > 3000:
        send_continue_action(self)
        return
    Profile(self.db, user_id = self.user.id).profile_text = self.raw_text
    self.reply("Текст анкеты был обновлен!")
    confirm_message(self)


@after_func("delete_photo")
def delete_photo(self):
    index = parseInt(self.text)
    profile = Profile(self.db, user_id = self.user.id)
    if not index or self.text == "отменить" or index > len(profile.photos) or index < 1:
        send_continue_action()
    else:
        del Profile(self.db, user_id = self.user.id).photos[index - 1]
        self.reply("Фото было удалено!")
        confirm_message(self)

@after_func("choose_update_profile_option")
def choose_update_profile_option(self):
    action = parseInt(self.text)
    if not action or action < 1 or action > 6:
        self.reply("Нет такого варианта ответа. Попробуйте еще раз.")
        return True
    if action == 1:
            self.reply("Теперь отправь нам новое фото для своей анкеты.\nИли напиши \"1\", чтобы оставить как есть.", keyboard = {"1":"green"})
            self.set_after("choose_new_profile_photo")
    elif action == 2:
        Profile(self.db, user_id = self.user.id).destroy()
        Profile(self.db, user_id = self.user.id, profile_photo=self.user.avatar or "")
        self.reply("Первый вопрос: Сколько Тебе лет?", keyboard = Keyboard.get_empty_keyboard())
        self.set_after("add_age")
    elif action == 3:
        self.reply("Отправь нам одно или несколько фото и мы добавим их в твою анкету.\nИли напиши \"1\", чтобы оставить как есть.", keyboard = {"1":"green"})
        self.set_after("add_profile_photos")
    elif action == 4:
        self.reply("Отправь нам голосовое сообщение для анкеты.\nИли напиши \"1\", чтобы оставить как есть.", keyboard = {"1":"green"})
        self.set_after("add_voice_message")
    elif action == 5:
        self.reply("Теперь введи новый текст анкеты.\nИли напиши \"1\", чтобы оставить как есть.", keyboard = {"1":"green"})
        self.set_after("update_text_message")
    elif action == 6:
        profile = Profile(self.db, user_id = self.user.id)
        self.reply("Отправь номер фото, которое нужно удалить.\nИли напиши \"Отменить\", чтобы оставить как есть.", keyboard = Keyboard(ListExtension.indexList(profile.photos).map(lambda it: it + 1)).add_line().add_button("Отменить", color = Keyboard.colors["red"]), attachment = ",".join(profile.photos))
        self.set_after("delete_photo")