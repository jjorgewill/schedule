from modeltranslation.translator import translator, TranslationOptions

from apps.core.models import Profession


class ProfessionOptions(TranslationOptions):
    fields = ('name',)


translator.register(Profession, ProfessionOptions)
