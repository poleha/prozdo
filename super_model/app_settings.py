from django.conf import settings as project_settings

class Settings:
    SUPER_MODEL_KEY_NAME = 'user_key'

    USER_ROLE_REGULAR = 1
    USER_ROLE_ADMIN = 33

    USER_ROLES = (
            (USER_ROLE_REGULAR, 'Обычный пользователь'),
            (USER_ROLE_ADMIN, 'Админ'),
        )


    def __getattribute__(self, item):
        if hasattr(project_settings, item):
            return getattr(project_settings, item)
        else:
            return super().__getattribute__(item)


settings = Settings()