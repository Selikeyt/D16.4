from django import template

register = template.Library()

@register.filter()
def cenzor(value):
    mat = ['idiot', 'fizz', 'nasty', 'euro']
    word = ''

    text = value.split()
    for i in range(len(text)):
        for j in mat:
            if j in text[i].lower():
                for c in (text[i]):
                    word += '*' if c.isalpha() else c
                    text[i] = text[i][0] + word

    return ' '.join(text)