import string
from .app_settings import settings
import random


def generate_key(size=128, upper=False, chars=None):
    if chars is None:
        chars = string.ascii_lowercase + string.digits
        if upper:
            chars += string.ascii_uppercase
    return ''.join(random.choice(chars) for _ in range(size))


def set_and_get_session_key(session):
    key = session.get(settings.SUPER_MODEL_KEY_NAME, None)
    if key is None:
        key = generate_key(128)
        session[settings.SUPER_MODEL_KEY_NAME] = key
    return key