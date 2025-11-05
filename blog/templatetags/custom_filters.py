from django import template

register = template.Library()

@register.filter(name='censor')
def censor(value):
    bad_words = ['жопа', 'говно', 'мразь']
    for bad_word in bad_words:
        value = value.replace(bad_word, '*' * len(bad_word))
    return value