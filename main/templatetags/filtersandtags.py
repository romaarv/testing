from django import template

register = template.Library()


#page-номер страницы, item- номер записи
def multiplic (page, item):
    return '%d' % ((page-1)*item)

register.filter ('multiplic', multiplic)


# register.simple_tag (multiplic)