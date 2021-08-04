
import geopy.distance


def parseInt(string):
    try:
        return int(string)
    except:
        return None


def send_profile(self, user_id, to_id, message="", keyboard=None):
    user_profile = self.db.select_one_struct(
        "select * from profiles where user_id = ?", [user_id])
    m = f"{message}{user_profile.display_name}, {user_profile.city}, {user_profile.age}\n\n{user_profile.profile_text}"
    if to_id != user_id:
        to_profile = self.db.select_one_struct(
            "select * from profiles where user_id = ?", [to_id])
        distance = geopy.distance.distance(
            (user_profile.lat, user_profile.long), (to_profile.lat, to_profile.long))
        distance_str = f"{distance.kilometers} км." if distance.kilometers > 1 else f"{distance.meters} м."
        m = f"{message}{user_profile.display_name}, {user_profile.city}, {user_profile.age} | {distance_str}\n\n{user_profile.profile_text}" if distance > 0 else m
    attachments = f"{user_profile.profile_photo},"
    if user_profile.photos:
        attachments += ",".join(user_profile.photos) + ","
    if user_profile.voice_message:
        attachments += user_profile.voice_message
    self.write(to_id, m, attachment=attachments) if keyboard is None else self.write(
        to_id, m, attachment=attachments, keyboard=keyboard)
