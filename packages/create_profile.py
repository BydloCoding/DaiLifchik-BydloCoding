from Structs.profile import Profile
from packages.search import random_profile
from SDK.cmd import command, after_func
from geopy.geocoders import Nominatim
from SDK.keyboard import Keyboard
import utils
import message_utils


geolocator = Nominatim(user_agent="dai_lifchick")


@after_func("add_age")
def add_age(self):
    user_profile = self.db.select_one_struct(
        "select * from profiles where user_id = ?", [self.user.id])
    age = utils.parseInt(self.text)
    if age is None or age < 10 or age > 100:
        self.reply("Неправильно указан возраст!")
        return True
    user_profile.age = age
    self.reply("Кого тебе найти?\n\n1 - Парня.\n2 - Девушку.\n3 - Все равно.",
               {"1": "white", "2": "blue", "3": "white"})
    self.set_after("add_searching_for")


@after_func("add_searching_for")
def add_searching_for(self):
    user_profile = self.db.select_one_struct(
        "select * from profiles where user_id = ?", [self.user.id])
    search = utils.parseInt(self.text)
    if search is None or search < 1 or search > 3:
        self.reply("Нет такого варианта ответа. Попробуйте еще раз.")
        return True
    user_profile.searching_for = search
    self.reply("Какого ты пола?\n1 - Я парень.\n2 - Я девушка.",
               {"1": "white", "2": "blue"})
    self.set_after("add_gender")


@after_func("add_gender")
def add_gender(self):
    user_profile = self.db.select_one_struct(
        "select * from profiles where user_id = ?", [self.user.id])
    gender = utils.parseInt(self.text)
    if gender is None or gender < 1 or gender > 2:
        self.reply("Нет такого варианта ответа. Попробуйте еще раз.")
        return True
    user_profile.gender = gender
    self.reply("Отправь нам свое местоположение и мы найдем кого-то рядом с тобой",
               keyboard=["locationButton"])
    self.set_after("add_geolocate", [0])


@after_func("add_geolocate")
def add_geolocate(self, args):
    geopos = self.last_message.get("geo")
    cycle = args[0]
    user_profile = self.db.select_one_struct(
        "select * from profiles where user_id = ?", [self.user.id])
    if not cycle and geopos is None:
        self.reply(
            "Напиши из какого ты города, а еще лучше пришли свои координаты")
        self.set_after("add_geolocate", [1])
    elif geopos is not None and geopos.get("place") is not None and geopos.get("place").get("city") is not None:
        user_profile.lat, user_profile.long = geopos["coordinates"][
            "latitude"], geopos["coordinates"]["longitude"]
        user_profile.city = geopos["place"]["city"]
        self.reply("Как мне тебя называть?")
        self.set_after("add_name")
    elif not cycle:
        self.reply(
            "Нам не удалось определить город по отправленному местоположению. Введи город вручную.")
        user_profile.lat, user_profile.long = geopos["coordinates"][
            "latitude"], geopos["coordinates"]["longitude"]
        self.set_after("add_geolocate", [1])
    else:
        user_profile.city = self.raw_text.split("\n")[0].capitalize()
        located = geolocator.geocode(user_profile.city)
        if located is not None:
            user_profile.lat, user_profile.long = located.latitude, located.longitude
        self.reply("Как мне тебя называть?", Keyboard.get_empty_keyboard())
        self.set_after("add_name")


@after_func("add_name")
def add_name(self):
    user_profile = self.db.select_one_struct(
        "select * from profiles where user_id = ?", [self.user.id])
    user_profile.display_name = self.raw_text.split("\n")[0]
    self.reply("Теперь расскажи о себе\nИли напиши \"1\", чтобы пропустить этот шаг", {
               "1": "red"})
    self.set_after("add_profile_text")


@after_func("confirm_profile")
def confirm_profile(self):
    action = utils.parseInt(self.text)
    if not action or action < 1 or action > 2:
        self.reply("Нет такого варианта ответа. Попробуйте еще раз.")
        return True
    if action == 1:
        random_profile(self)
    else:
        message_utils.update_options(self)


@after_func("add_profile_text")
def add_profile_text(self):
    if self.text != "1":
        if len(self.raw_text) > 3000:
            self.reply("Похоже, ваш текст слишком большой!")
        else:
            Profile(self.db, user_id=self.user.id).profile_text = self.raw_text
    message_utils.confirm_message(self)


@command("начать")
def start_bot(self, args):
    user_profile = self.db.select_one_struct(
        "select * from profiles where user_id = ?", [self.user.id])
    if user_profile is None:
        Profile(self.db, user_id=self.user.id,
                profile_photo=self.user.avatar or "")
        self.reply(
            "Привет! Я помогу тебе найти пару или друзей. Для начала, ответь на мои вопросы.\nСколько тебе лет?")
        self.set_after("add_age")
        return
    message_utils.send_continue_action(self)