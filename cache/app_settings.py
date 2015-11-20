from django.conf import settings as project_settings
from django.utils.module_loading import import_string

class Settings:
    def __init__(self):
        special_cases = {}
        special_cases_from_settings = getattr(project_settings, 'CACHED_METHOD_SPECIAL_CASES', tuple())
        for path, val in special_cases_from_settings.items():
            klass = import_string(path)
            special_cases[klass] = val
        self.special_cases = special_cases

    def __getattr__(self, item):
        if hasattr(project_settings, item):
            return getattr(project_settings, item)
        else:
            super().__getattribute__(item)

    @property
    def CACHED_VIEW_DURATION(self):
        return 60 * 60 * 24 * 7

    @property
    def CACHED_PROPERTY_DURATION(self):
        return 60 * 60 * 24 * 7

    @property
    def CACHED_METHOD_DURATION(self):
        return 60 * 60

    @property
    def CACHE_ENABLED(self):
        return True


settings = Settings()