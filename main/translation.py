from modeltranslation.translator import register, TranslationOptions

from .models import Group, Lesson


@register(Group)
class GroupTranslationOptions(TranslationOptions):
    fields = ('name', )


@register(Lesson)
class LessonTranslationOptions(TranslationOptions):
    fields = ('name', )