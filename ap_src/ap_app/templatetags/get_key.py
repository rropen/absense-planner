from django import template

register = template.Library()


@register.filter(name="get_key")
def get_key(dictionary:dict, key):
    if dictionary and key in dictionary.keys(): 
        return dictionary[key]
    return []
