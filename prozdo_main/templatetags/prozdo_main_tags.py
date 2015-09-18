from django import template
from prozdo_main import models
from django.utils import timezone
from datetime import timedelta
from django.db.models.aggregates import Count
from django.core.urlresolvers import reverse_lazy
from string import ascii_lowercase, digits
from collections import OrderedDict, namedtuple



register = template.Library()

MenuItem = namedtuple('MenuItem', ['title', 'url', 'cls'])

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
    children_list = comment.get_children_tree()
    res['children'] = children_list
    res['request'] = context['request'] #Поскольку мы будем вызывать get_comment, требующий request, нам нужно,
    # чтобы request был доступен. Иначе _get_child_comments не получит request тк это inclusion tag, а request
    # доступен в контексте view
    res['show_as_child'] = True
    return res


@register.inclusion_tag('prozdo_main/widgets/_get_comment.html', takes_context=True)
def get_comment(context, comment):
    res = {}
    request = context['request']
    show_as_child = context.get('show_as_child', False)
    res['show_as_child'] = show_as_child
    res['show_tree'] = context.get('show_tree', False)

    res['comment'] = comment
    res['is_author'] = comment.is_author(request=request)

    res['can_mark'] = comment.can_perform_action(history_type=models.HISTORY_TYPE_COMMENT_RATED, request=request)
    res['can_unmark'] = comment.can_undo_action(history_type=models.HISTORY_TYPE_COMMENT_RATED, user=request.user)

    res['can_complain'] = comment.can_perform_action(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, request=request)
    res['can_uncomplain'] = comment.can_undo_action(history_type=models.HISTORY_TYPE_COMMENT_COMPLAINT, user=request.user)


    #if show_as_child:
    res['comment_class'] = 'single-comment-with-level-{0}'.format(comment.get_tree_level())
    #else:
    #    res['comment_class'] = 'single-comment-with-level-{0}'.format(0)
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


@register.inclusion_tag('prozdo_main/widgets/_top_menu.html', takes_context=True)
def top_menu(context):

    request = context['request']
    menu_items = []
    view_name = request.resolver_match.view_name
    menu_items.append(MenuItem(title='Главная', url=reverse_lazy('main-page'), cls='active' if view_name=='main-page' else ''))
    menu_items.append(MenuItem(title='Отзывы о лекарствах', url=reverse_lazy('drug-list'), cls='active' if view_name=='drug-list' else ''))
    menu_items.append(MenuItem(title='Аптечная косметика', url=reverse_lazy('cosmetics-list'), cls='active' if view_name=='cosmetics-list' else ''))
    menu_items.append(MenuItem(title='Здоровый блог', url=reverse_lazy('blog-list'), cls='active' if view_name=='blog-list' else ''))
    menu_items.append(MenuItem(title='Состав препаратов', url=reverse_lazy('component-list'), cls='active' if view_name=='component-list' else ''))

    return {'menu_items': menu_items}


@register.inclusion_tag('prozdo_main/widgets/_bottom_menu.html', takes_context=True)
def bottom_menu(context):
    user = context['request'].user
    res = {}
    res['main'] = reverse_lazy('main-page')
    res['drugs'] = reverse_lazy('drug-list')
    res['cosmetics'] = reverse_lazy('cosmetics-list')
    res['blog'] = reverse_lazy('blog-list')
    res['components'] = reverse_lazy('component-list')
    res['user_profile'] = reverse_lazy('user-profile')
    res['current_user'] = user
    res['logout'] = reverse_lazy('logout')
    res['login'] = reverse_lazy('login')
    res['signup'] = reverse_lazy('signup')
    return res

@register.simple_tag(takes_context=True)
def get_get_parameters_exclude(context, exclude=('page', ), page=None):
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

"""
@register.inclusion_tag('prozdo_main/widgets/_post_alphabet.html', takes_context=True)
def post_alphabet(context, post_type_text):
    request = context['request']
    current_letter = request.resolver_match.kwargs.get('letter', None)
    if post_type_text == 'drug':
        post_type = models.POST_TYPE_DRUG
        url = models.Drug.get_list_url()
    elif post_type_text == 'cosmetics':
        post_type = models.POST_TYPE_COSMETICS
        url = models.Cosmetics.get_list_url()
    elif post_type_text == 'component':
        post_type = models.POST_TYPE_COMPONENT
        url = models.Component.get_list_url()
    alph = OrderedDict()
    letters = digits + ascii_lowercase + 'абвгдеёжзийклмнопрстуфхцчшщъыбэюя'
    for letter in letters:
        posts = models.Post.objects.filter(post_type=post_type, title__istartswith=letter)
        count = posts.count()
        if count > 0:
            alph[letter] = letter

    total_count = models.Post.objects.get_available().filter(post_type=post_type).count()
    return {'alph': alph, 'total_count': total_count, 'url': url, 'current_letter': current_letter}
"""

@register.inclusion_tag('prozdo_main/widgets/_user_detail.html')
def user_detail(user):
    return {'user': user}

