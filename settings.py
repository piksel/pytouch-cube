import datetime
import os
from pickle import Pickler, Unpickler

import appdirs
import yaml

from app import APP_NAME, APP_AUTHOR
from printables.printable import PrintableData


class Settings:

    class __Settings:
        def __init__(self):
            self.last_used_label_dir = None
            self.last_used_image_dir = None
            self.recent_labels = []
            self.default_font = None

    __instance: __Settings = None

    __appdirs: appdirs.AppDirs = None
    __file_path: str = None
    __defaults_dir: str = None

    def __getattr__(self, name):
        return getattr(self.instance, name)

    @classmethod
    def get_propsdata_file_path(cls, class_name: str):
        return os.path.join(cls.__defaults_dir, class_name + '.p3props')

    @classmethod
    def load(cls):
        ad = appdirs.AppDirs(APP_NAME, APP_AUTHOR)

        config_dir = ad.user_config_dir
        if not os.path.isdir(config_dir):
            os.mkdirs(config_dir)

        defaults_dir = os.path.join(config_dir, 'defaults')
        if not os.path.isdir(defaults_dir):
            os.mkdirs(defaults_dir)

        file_path = os.path.join(config_dir, 'settings.yml')

        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as file:
                    settings = yaml.load(file)
            except Exception as x:
                error = x
                time = datetime.datetime.now().isoformat('_', 'seconds').replace(':','')
                os.rename(file_path, os.path.join(ad.site_config_dir(), 'settings_invalid_{0}.yml'.format(time)))
                settings = cls.__Settings()
        else:
            settings = cls.__Settings()

        cls.__appdirs = ad
        cls.__defaults_dir = defaults_dir
        cls.__file_path = file_path
        cls.__instance = settings

    @classmethod
    def set_propsdata_default(cls, data: PrintableData):
        s = Settings.__instance
        file_path = cls.get_propsdata_file_path(type(data).__name__)
        with open(file_path, 'wb') as file:
            Pickler(file).dump(data)

    @classmethod
    def get_propsdata_default(cls, data_type: type):
        s = Settings.__instance
        file_path = cls.get_propsdata_file_path(data_type.__name__)
        if not os.path.isfile(file_path):
            return None
        with open(file_path, 'rb') as file:
            data = Unpickler(file).load()
        return data
