import uuid

import transliterate
from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Recipes.Status.PUBLISHED)

def translit_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'r', 'ю': 'yu', 'я': 'ya'}

    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))



class Recipes(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'


    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='Slug')

    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=True, verbose_name='Фото')
    content = models.TextField(blank=True, verbose_name='Описание')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                                     default=Status.DRAFT, verbose_name='Статус')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT,
                            related_name='posts', verbose_name='Категория')
    tags = models.ManyToManyField('TagPost', blank=True, related_name='tags', verbose_name='Теги')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL,
                               related_name='posts', null=True, default=None)

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    # def get_absolute_url(self):
    #     return reverse('post', kwargs={'post_slug': self.slug})

    def get_absolute_url(self):
        if not self.slug:  # Защита на случай, если slug пустой
            self.save()  # Пересохраняем, чтобы сгенерировать slug
        return reverse('post', kwargs={'post_slug': self.slug})

    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.title)
    #     super(Recipes, self).save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     if not self.slug:  # Генерируем slug только если он не задан
    #         self.slug = slugify(self.title)
    #
    #         # Если slug пустой (например, title был "---"), создаем случайный
    #         if not self.slug:
    #             self.slug = f"post-{uuid.uuid4().hex[:8]}"
    #
    #         # Проверяем уникальность
    #         original_slug = self.slug
    #         counter = 1
    #         while Recipes.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
    #             self.slug = f"{original_slug}-{counter}"
    #             counter += 1
    #
    #     super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         try:
    #             title_en = transliterate.translit(self.title, reversed=True)  # "Привет" → "Privet"
    #         except:
    #             title_en = self.title
    #         self.slug = slugify(title_en)
    #         if not self.slug:
    #             self.slug = f"post-{uuid.uuid4().hex[:8]}"
    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.slug:  # Генерируем slug, только если он пустой
            self.slug = slugify(self.title) or f"post-{uuid.uuid4().hex[:8]}"

            # Проверяем уникальность и добавляем суффикс, если нужно
            original_slug = self.slug
            counter = 1
            while Recipes.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)



class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Категория')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})

class UploadFiles(models.Model):
    file = models.FileField(upload_to='uploads_model')