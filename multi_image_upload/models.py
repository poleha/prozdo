from django.db import models
from PIL import Image as PILImage
import io

from django.db.models.fields.files import ImageFieldFile, ImageFileDescriptor

import os

import string
import random
from django.utils import timezone


def generate_code(size=7, upper=False, chars=None):
    if chars is None:
        chars = string.ascii_lowercase + string.digits
        if upper:
            chars += string.ascii_uppercase
    return ''.join(random.choice(chars) for _ in range(size))


"""
Don't forget to add  self.[field_name].delete() to ensure, that files are deleted with model

from django.db import models
class Post(models.model):
...
image = MyImageField(verbose_name='Изображение', null=True, blank=True)
   ...
    def delete(self, *args, **kwargs):
        self.image.delete()
        return super().delete(*args, **kwargs)
    ...
"""




THUMB_SETTINGS = {}



UPLOAD_TO = 'images'
EFFECTS = ('ANTIALIAS',)


"""
models.ImageField имеет аттрибут - экземпляр ImageFieldFile, который имеет экземпляр - аттрибут File
Из-за технических сложностей ImageField получает ImageFieldFile через дескриптор ImageFileDescriptor

ImageField имеет аттрибут storage - экземпляр класса для работы с файловой системой


ImageFieldFile _commtitted


"""


def get_effects(ob):
    return [getattr(ob, effect) for effect in EFFECTS]



def save_thumbs(storage, thumb_settings, path, upload_to, name):
    image = PILImage.open(path)
    #image = PILImage.open(self.path)
    if not image.mode == 'RGB':
        bg = PILImage.new("RGB", image.size, (255, 255, 255))
        image = image.convert('RGBA')
        bg.paste(image, mask=image)
        #image = bg.convert('RGB')
        image = bg

    effects = get_effects(PILImage)
    #storage = self.field.storage
    #for key, value in self.field.thumb_settings.items():
    for key, value in thumb_settings.items():
        thumb = image.copy()
        thumb.thumbnail(value, *effects)


        thumb_io = io.BytesIO()
        thumb.save(thumb_io, 'jpeg', quality=100, optimize=True)



        #thumb_file = InMemoryUploadedFile(thumb_io, None, file_name, 'image/jpeg',   - смысла не вижу
        #                                  None, None)
        #storage.save(os.path.join(self.field.upload_to, key, self.short_name), thumb_io)
        save_path = os.path.join(upload_to, key, name)
        if storage.exists(save_path):
            storage.delete(save_path)
        storage.save(save_path, thumb_io)



def generate_filenames(storage, name):
    lst = name.split('.')
    if len(lst) > 1:
        ext = lst[-1]
    else:
        ext = ''
    name_is_correct = False
    while not name_is_correct:
        name = generate_code(size=50, upper=False)
        name_jpg = name + '.' + 'jpg'
        name_ext = name + '.' + ext
        name_is_correct = not (storage.exists(name) or storage.exists(name_jpg) or storage.exists(name_ext))
    return name, name_jpg, name_ext

class MyImageFieldFile(ImageFieldFile):
    def __init__(self, instance, field, name,  *args, **kwargs):
        super().__init__(instance, field, name, *args, **kwargs)
        if self.name is not None:
            self.short_name = os.path.split(self.name)[-1]
            self.short_name = self.short_name.split('.')[0] + '.jpg'
            for key in field.thumb_settings.keys():
                file_name = os.path.join(field.upload_to, key, self.short_name)
                url = self.storage.url(file_name)
                setattr(self, key, url)


    def save(self, name, content, save=True):
        name, name_jpg, name_ext = generate_filenames(self.storage, name)
        self.name = name_jpg
        name = self.field.generate_filename(self.instance, name_ext) #Оригинал сохраним с исходным расширением
        self.short_name = os.path.split(name_jpg)[-1]
        if self.instance.id is not None:
            #old_file1 = self.instance.__dict__.get(self.field.name)  #Не сработает, т.к. instance тут уже после изменений
            old_model = self.instance.__class__.objects.get(pk=self.instance.id)
            if old_model:
                old_file = getattr(old_model, self.field.attname)
                if old_file.name != '':
                    old_file.delete(save=False)
        super(MyImageFieldFile, self).save(name, content, save)
        #self._committed = False
        try:
            save_thumbs(self.storage, self.field.thumb_settings, self.path, self.field.upload_to, self.short_name)
        except:
            pass



    def delete(self, save):
        self.delete_thumbs()
        super(MyImageFieldFile, self).delete(save)


    #def get_thumb_filename(self, key):
        #return os.path.join(self.field.upload_to, key, self.short_name)

    def delete_thumbs(self):
        storage = self.field.storage
        #storage.delete(self.name)
        for key in self.field.thumb_settings.keys():
                try:
                    storage.delete(self.get_thumb_filename(key))
                except:
                    pass


class MyImageFileDescriptor(ImageFileDescriptor):
    pass



class MyImageField(models.ImageField):
    attr_class = MyImageFieldFile
    descriptor_class = MyImageFileDescriptor
    #allowed_extensions = ['jpg', 'jpeg', 'gif', 'tiff', 'bmp', 'jp2', 'pcx', 'jpe']

    #def validate(self, value, model_instance):
    #    name = value.name
    #    dot_position = name.rfind('.')
    #    ext = name[dot_position + 1:].lower()
    #    if ext not in self.allowed_extensions:
    #        raise ValidationError('Допустимы следующие расширения: {0}'.format(self.allowed_extensions))
    #    return super().validate(value, model_instance)

    #Вызывается один раз, при старте сервера. Не имеет файла.
    def __init__(self, *args, upload_to=UPLOAD_TO, thumb_settings=None, **kwargs):
        if thumb_settings is None:
            thumb_settings = THUMB_SETTINGS
        self.thumb_settings = thumb_settings
        super(MyImageField, self).__init__(upload_to=upload_to, *args, **kwargs)

    def save_form_data(self, instance, data, *args, **kwargs):
        if not data:
            old_file = instance.__dict__.get(self.name) #Сработает, т.к. instance тут еще до изменений
            try:
                old_file.delete(save=True)
            except (AssertionError, AttributeError):
                pass
        return super(MyImageField, self).save_form_data(instance, data, *args, **kwargs)






