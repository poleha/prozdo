from django import template
from prozdo_main import models

register = template.Library()

@register.filter(name='cut_text')
def cut_text(value, length): # Only one argument.
    """Cuts first length letters from string"""
    return value[0:length]


@register.filter(name='bool_as_yes')
def bool_as_yes(value):
    if value:
        return 'Да'
    else:
        return 'Нет'


@register.filter(name='get_item')
def get_item(dct, key):
    if hasattr(dct, 'get'): #У форм нет метода get
        res = dct.get(key, None)
    else:
        try:
            res = dct[key]
        except:
            res = None
    return res


@register.filter(name='get_attr')
def get_attr(ob, item):
    res = getattr(ob, item, None)
    if callable(res):
        return res()
    else:
        return res


@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    return instance._meta.get_field(field_name).verbose_name.title()


@register.inclusion_tag('prozdo_main/widgets/_get_comments.html', takes_context=True)
def get_comments(context, post):
    res = {}
    comments = post.comments.all()
    res['comments'] = comments
    res['request'] = context['request']
    return res



@register.inclusion_tag('prozdo_main/widgets/_get_comment.html', takes_context=True)
def get_comment(context, comment):
    res = {}
    request = context['request']

    res['comment'] = comment
    res['is_author'] = comment.is_author(request=request)

    res['can_mark'] = comment.can_perform_action(history_type=models.HISTORY_TYPE_COMMENT_RATED, request=request)
    res['can_unmark'] = comment.can_undo_action(history_type=models.HISTORY_TYPE_COMMENT_RATED, user=request.user)

    res['can_complain'] = comment.can_perform_action(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, request=request)
    res['can_uncomplain'] = comment.can_undo_action(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, user=request.user)

    return res

