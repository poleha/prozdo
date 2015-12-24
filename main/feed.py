from django.contrib.syndication.views import Feed
from .models import Blog

class LatestBlogEntriesFeed(Feed):
    title = "Новые записи здорового блога"
    link = "/blog/"
    description = "Новый записи здорового блога портала Про здоровье: отзывы о лекарствах"

    def items(self):
        return Blog.objects.get_available().order_by('-created')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return item.get_absolute_url()