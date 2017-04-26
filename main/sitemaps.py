from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse_lazy

from .models import Drug, Cosmetics, Blog, Component


class BaseSitemap(Sitemap):
    protocol = 'https'


class PostSitemap(BaseSitemap):
    changefreq = "daily"
    priority = 1.0

    def lastmod(self, obj):
        return obj.last_modified


class DrugSitemap(PostSitemap):
    def items(self):
        return Drug.objects.get_available()


class CosmeticsSitemap(PostSitemap):
    def items(self):
        return Cosmetics.objects.get_available()


class BlogSitemap(PostSitemap):
    def items(self):
        return Blog.objects.get_available()


class ComponentSitemap(PostSitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Component.objects.get_available()


class DrugListSitemap(BaseSitemap):
    def items(self):
        return [self]

    location = reverse_lazy('drug-list')
    changefreq = "weekly"
    priority = 0.7


class ComponentListSitemap(BaseSitemap):
    def items(self):
        return [self]

    location = reverse_lazy('component-list')
    changefreq = "weekly"
    priority = 0.7


class BlogListSitemap(BaseSitemap):
    def items(self):
        return [self]

    location = reverse_lazy('blog-list')
    changefreq = "weekly"
    priority = 0.7


class CosmeticsListSitemap(BaseSitemap):
    def items(self):
        return [self]

    location = reverse_lazy('cosmetics-list')
    changefreq = "weekly"
    priority = 0.7


class MainPageSitemap(BaseSitemap):
    def items(self):
        return [self]

    location = reverse_lazy('main-page')
    changefreq = "daily"
    priority = 1.0


sitemaps = {
    'drud-detail': DrugSitemap,
    'cosmetics-detail': CosmeticsSitemap,
    'blog-detail': BlogSitemap,
    'component-detail': ComponentSitemap,
    'drud-list': DrugListSitemap,
    'cosmetics-list': CosmeticsListSitemap,
    'blog-list': BlogListSitemap,
    'component-list': ComponentListSitemap,
    'main-page': MainPageSitemap,
}
