from ._core import ValidationPluginBase


class FileRoot(ValidationPluginBase):
    def register(self):
        print(f"register: {__file__}::{self.__class__.__name__}")

    def action(self):
        print(f"action: {__file__}::{self.__class__.__name__}")
