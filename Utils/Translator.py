import gettext
from DataAccess.MainConfigDAO import MainConfigDAO
from Utils.PathHelper import PathHelper


class Translator:
    ALLOWED_LANGUAGES = ["en", "es"]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Translator, cls).__new__(cls, *args, **kwargs)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self) -> None:
        if self.initialized:
            return
        else:
            self.initialized = True

        self.translation = None
        self._mainConfigDAO = MainConfigDAO()

        self.set_language_from_config()

    def set_language_from_config(self):
        self.set_language(self._mainConfigDAO.get_language())

    def set_language(self, language: str):
        if not language in Translator.ALLOWED_LANGUAGES:
            language = Translator.ALLOWED_LANGUAGES[0]
        self.install_translation([language])

    def install_translation(self, languages: "list[str]"):
        self.translation = gettext.translation(
            "base",
            localedir=PathHelper().join_root_path("/Resources/locales"),
            languages=languages,
            fallback=True,
        )
        self.translation.install()

    def gettext(self, message):
        return self.translation.gettext(message)

    def ngettext(self, msgid1, msgid2, n):
        return self.translation.ngettext(msgid1, msgid2, n)
