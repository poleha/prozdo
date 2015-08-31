from django import template
from prozdo_main import models
from django.utils import timezone
from datetime import timedelta
from django.db.models.aggregates import Count
from django.core.urlresolvers import reverse

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


@register.inclusion_tag('prozdo_main/widgets/_get_child_comments.html', takes_context=True)
def get_child_comments(context):
    res = {}
    comment = context['comment']
    childs_list = comment.get_childs_tree()
    res['childs'] = childs_list
    res['request'] = context['request']
    return res


@register.inclusion_tag('prozdo_main/widgets/_get_comment.html', takes_context=True)
def get_comment(context, comment):
    res = {}
    request = context['request']
    res['show_tree'] = context.get('show_tree', False)

    res['comment'] = comment
    res['is_author'] = comment.is_author(request=request)

    res['can_mark'] = comment.can_perform_action(history_type=models.HISTORY_TYPE_COMMENT_RATED, request=request)
    res['can_unmark'] = comment.can_undo_action(history_type=models.HISTORY_TYPE_COMMENT_RATED, user=request.user)

    res['can_complain'] = comment.can_perform_action(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, request=request)
    res['can_uncomplain'] = comment.can_undo_action(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, user=request.user)

    return res


@register.inclusion_tag('prozdo_main/widgets/_recent_comments.html')
def recent_comments():
    res = {}
    comments = models.Comment.objects.get_available().order_by('-created')[:10]
    res['comments'] = comments
    return res


@register.inclusion_tag('prozdo_main/widgets/_best_comments.html')
def best_comments():
    res = {}
    date = timezone.now() - timedelta(days=30)
    comments = models.Comment.objects.filter(history_comment__history_type=models.HISTORY_TYPE_COMMENT_RATED, history_comment__created__gte=date).annotate(hist_count=Count('history_comment')).order_by('-hist_count')[:10]

    res['comments'] = comments
    return res


@register.inclusion_tag('prozdo_main/widgets/_top_menu.html')
def top_menu():
    res = {}
    res['main'] = '/'
    res['drugs'] = reverse('drug-list')
    return res




@register.simple_tag(takes_context=True)
def get_get_parameters_exclude(context, exclude=('page',), page=None):
    request = context['request']
    params = ''
    for key in request.GET:
        if key in exclude:
            continue
        if params == '':
            params = '?'
        lst = request.GET.getlist(key)
        if len(lst) == 1:
            params +="&{0}={1}".format(key, request.GET[key])
        else:
            for item in lst:
                params +="&{0}={1}".format(key, item)
    if page is not None and page > 1:
        if params == '':
            params += '?page=' + str(page)
        elif params == '?':
            params += 'page=' + str(page)
        else:
            params += '&page=' + str(page)
    return params

