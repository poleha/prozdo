from haystack import indexes
from . import models


class ProzdoBaseIndex(indexes.SearchIndex):
    class Meta:
        abstract = True

    weight = indexes.CharField()
    text = indexes.CharField(document=True, use_template=True)
    created = indexes.DateTimeField(model_attr='created')

    def index_queryset(self, using=None):
        return self.get_model().objects.get_available()

class DrugIndex(ProzdoBaseIndex, indexes.Indexable):

    def get_model(self):
        return models.Drug

    def prepare_weight(self,obj):
        return 1


class BlogIndex(ProzdoBaseIndex, indexes.Indexable):

    def get_model(self):
        return models.Blog

    def prepare_weight(self,obj):
        return 2


class CosmeticsIndex(ProzdoBaseIndex, indexes.Indexable):

    def get_model(self):
        return models.Cosmetics

    def prepare_weight(self,obj):
        return 2


class ComponentIndex(ProzdoBaseIndex, indexes.Indexable):

    def get_model(self):
        return models.Component

    def prepare_weight(self,obj):
        return 3

class CommentIndex(ProzdoBaseIndex, indexes.Indexable):

    def get_model(self):
        return models.Comment

    def prepare_weight(self,obj):
        return 4