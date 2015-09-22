from django import template
from prozdo_main import models
from django.utils import timezone
from datetime import timedelta
from django.db.models.aggregates import Count
from django.core.urlresolvers import reverse_lazy
from string import ascii_lowercase, digits
from collections import OrderedDict, namedtuple
from django.core.urlresolvers import reverse


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
    res['user'] = request.user
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


@register.inclusion_tag('prozdo_main/widgets/_user_detail.html')
def user_detail(user):
    return {'user': user}



Breadcrumb = namedtuple('Breadcrumb', ['title', 'href', 'type'])

@register.inclusion_tag('prozdo_main/widgets/_breadcrumbs.html', takes_context=True)
def breadcrumbs(context):

    request = context['request']
    url_name = request.resolver_match.url_name
    #kwargs = request.resolver_match.kwargs

    if url_name == 'main-page':
        return

    breadcrumbs_list = [Breadcrumb(title='Главная', href=reverse('main-page'), type='link')]

    if url_name == 'drug-list':
        breadcrumbs_list.append(Breadcrumb(title='Отзывы о лекарствах', href='', type='text'))

    elif url_name == 'cosmetics-list':
        breadcrumbs_list.append(Breadcrumb(title='Отзывы об аптечной косметике', href='', type='text'))

    elif url_name == 'blog-list':
        breadcrumbs_list.append(Breadcrumb(title='Здоровый блог', href='', type='text'))

    elif url_name == 'component-list':
        breadcrumbs_list.append(Breadcrumb(title='Состав препаратов', href='', type='text'))

    elif url_name in ['post-detail-alias', 'post-detail-alias-comment', 'post-detail-pk', 'post-detail-pk-comment']:
        obj = context['obj']
        if isinstance(obj, models.Drug):
            list_title = 'Отзывы о лекарствах'
            href = reverse('drug-list')
        elif isinstance(obj, models.Blog):
            list_title = 'Здоровый блог'
            href = reverse('blog-list')
        elif isinstance(obj, models.Cosmetics):
            list_title = 'Отзывы об аптечной косметике'
            href = reverse('cosmetics-list')
        elif isinstance(obj, models.Component):
            list_title = 'Состав препаратов'
            href = reverse('component-list')

        breadcrumbs_list.append(Breadcrumb(title=list_title, href=href, type='link'))
        obj = context['obj']
        breadcrumbs_list.append(Breadcrumb(title=obj.title, href=obj.get_absolute_url(), type='text'))


    elif url_name == 'user-profile':
        user = context['user']
        breadcrumbs_list.append(Breadcrumb(title='Профиль пользователя {0}'.format(user), href='', type='text'))

    elif url_name == 'user-detail':
        user = context['current_user']
        breadcrumbs_list.append(Breadcrumb(title='Информация о пользователе {0}'.format(user), href='', type='text'))

    elif url_name in ['user-comments', 'user-karma']:
        user = context['current_user']
        breadcrumbs_list.append(Breadcrumb(title='Информация о пользователе {0}'.format(user), href=reverse('user-detail', kwargs={'pk': user.pk}), type='link'))
        if url_name == 'user-comments':
            breadcrumbs_list.append(Breadcrumb(title='Сообщения пользователя {0}'.format(user), href='', type='text'))
        elif url_name == 'user-karma':
            breadcrumbs_list.append(Breadcrumb(title='Карма пользователя {0}'.format(user), href='', type='text'))

    return {'breadcrumbs_list': breadcrumbs_list}

@register.inclusion_tag('prozdo_main/widgets/_metatags.html', takes_context=True)
def metatags(context):

    request = context['request']
    url_name = request.resolver_match.url_name
    #kwargs = request.resolver_match.kwargs



    metatags_dict = {}
    metatags_dict['title'] = 'Про здоровье'
    metatags_dict['keywords'] = "отзывы, лекарственные препараты, лекарства, аптечная косметика"
    metatags_dict['description'] = "Отзывы о лекарственных препаратах и аптечной косметике."
    metatags_dict['canonical'] = ''

    if url_name == 'main-page':
        pass

    elif url_name == 'drug-list':
        metatags_dict['title'] = 'Отзывы о лекарствах | Про здоровье'
        metatags_dict['keywords'] = "отзывы, лекарственные препараты, лекарства"
        metatags_dict['description'] = "Отзывы о лекарственных препаратах."

    elif url_name == 'cosmetics-list':
        metatags_dict['title'] = 'Отзывы об аптечной косметике | Про здоровье'
        metatags_dict['keywords'] = "отзывы, лекарственные препараты, лекарства"
        metatags_dict['description'] = "Отзывы о лекарственных препаратах."

    elif url_name == 'blog-list':
        metatags_dict['title'] = 'Здоровый блог | Про здоровье'
        metatags_dict['keywords'] = "блог о здоровье, статьи о здоровье, новости здоровья, здоровый образ жизни"
        metatags_dict['description'] = "Интересный блог о здоровье и здоровом образе жизни."

    elif url_name == 'component-list':
        metatags_dict['title'] = 'Состав препаратов | Про здоровье'
        metatags_dict['keywords'] = "отзывы, лекарственные препараты, лекарства, состав препаратов"
        metatags_dict['description'] = "Состав препаратов."

    elif url_name in ['post-detail-alias', 'post-detail-alias-comment', 'post-detail-pk', 'post-detail-pk-comment']:
        obj = context['obj']
        if isinstance(obj, models.Drug):
            metatags_dict['title'] = '{0} - отзывы | Про здоровье'.format(obj.title)
            metatags_dict['keywords'] = "{0} - отзывы, лекарственные препараты, лекарства, отзывы".format(obj.title)
            metatags_dict['description'] = "Отзывы о препарате {0}.".format(obj.title)
        elif isinstance(obj, models.Blog):
            metatags_dict['title'] = '{0} | Про здоровье'.format(obj.title)
            metatags_dict['keywords'] = "{0}, блог о здоровом образе жизни".format(obj.title)
            metatags_dict['description'] = obj.anons
        elif isinstance(obj, models.Cosmetics):
            metatags_dict['title'] = '{0} - отзывы | Про здоровье'.format(obj.title)
            metatags_dict['keywords'] = "{0} - отзывы, аптечная косметика, отзывы".format(obj.title)
            metatags_dict['description'] = "Отзывы об аптечной косметике: {0}.".format(obj.title)
        elif isinstance(obj, models.Component):
            metatags_dict['title'] = '{0} | Про здоровье'.format(obj.title)
            metatags_dict['keywords'] = "{0}, состав препаратов".format(obj.title)
            metatags_dict['description'] = "Описание компонента препаратов: {0}.".format(obj.title)

        if 'page' in request.GET:
            metatags_dict['canonical'] = obj.get_absolute_url()


    elif url_name == 'user-profile':
        user = context['user']

    elif url_name == 'user-detail':
        user = context['current_user']

    elif url_name in ['user-comments', 'user-karma']:
        user = context['current_user']
        if url_name == 'user-comments':
            pass
        elif url_name == 'user-karma':
            pass

    return metatags_dict

@register.filter(name='bool_as_text')
def bool_as_text(value):
    if value:
        return 'Да'
    else:
        return 'Нет'
