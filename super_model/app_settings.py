from django.conf import settings as project_settings

class Settings:
    SUPER_MODEL_KEY_NAME = 'user_key'

    def __getattribute__(self, item):
        if hasattr(project_settings, item):
            return getattr(project_settings, item)
        else:
            return super().__getattribute__(item)


settings = Settings()