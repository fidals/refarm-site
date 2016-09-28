from unidecode import unidecode
from datetime import date, datetime
from itertools import chain

from django.db import models, transaction
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.defaultfilters import slugify

from images.models import Image, ImageMixin
from images.templatetags.images import placeholder_image_url


class AbstractSeo(models.Model):
    class Meta:
        abstract = True

    h1 = models.CharField(max_length=255)
    keywords = models.CharField(blank=True, max_length=255)
    description = models.TextField(blank=True)
    seo_text = models.TextField(blank=True)

    _title = models.CharField(blank=True, max_length=255)

    @property
    def title(self):
        return self._title or self.h1

    @title.setter
    def title(self, value):
        self._title = value


class Page(AbstractSeo, ImageMixin):
    # pages with same templates (ex. news, about)
    FLAT_TYPE = 'flat'
    # pages with unique templates (ex. index, order)
    CUSTOM_TYPE = 'custom'
    # pages related with other models like Product or Category
    # pages with type 'flat' or 'custom' have not related model
    MODEL_TYPE = 'model'

    INDEX_SLUG = ''

    class Meta:
        unique_together = ('type', 'slug', 'related_model_name')

    type = models.CharField(default=FLAT_TYPE, max_length=100, editable=False)
    # Name for reversing at related model
    related_model_name = models.CharField(blank=True, max_length=255, editable=False)

    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)

    slug = models.SlugField(max_length=400, blank=True)
    is_active = models.BooleanField(default=True, blank=True)
    position = models.IntegerField(default=0, blank=True)
    content = models.TextField(blank=True)
    date_published = models.DateField(default=date.today, blank=True)

    _menu_title = models.CharField(
        max_length=180, blank=True,
        help_text='This field will be shown in the breadcrumbs, menu items and etc.'
    )

    @property
    def index(self):
        return Page.objects.filter(type=self.CUSTOM_TYPE, slug=self.INDEX_SLUG).first()

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def menu_title(self):
        return self._menu_title or self.h1

    @menu_title.setter
    def menu_title(self, value):
        self._menu_title = value

    @property
    def model(self) -> models.Model:
        """Return model, related to self"""
        return getattr(self, self.related_model_name)

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def is_root(self):
        return not self.parent and self.children

    @property
    def is_flat(self):
        return self.type == self.FLAT_TYPE

    @property
    def is_custom(self):
        return self.type == self.CUSTOM_TYPE

    @property
    def is_model(self):
        return self.type == self.MODEL_TYPE

    @property
    def is_section(self):
        """
        Defines if page is a list of other pages or not. Used in accordion.
        """
        return self.is_root and self.is_flat

    @property
    def image(self):
        """Used in microdata: http://ogp.me/#metadata """
        if self.model and hasattr(self.model, 'image'):
            return self.model.image
        else:
            return placeholder_image_url()

    def __str__(self):
        return self.h1

    def get_absolute_url(self):
        """Different page types reverse different urls"""
        if self.is_model:
            return self.model.get_absolute_url()

        if self.is_custom:
            return reverse(settings.CUSTOM_PAGES_URL_NAME, args=(self.slug, ))

        if self.is_flat:
            return reverse('pages:flat_page', args=self.get_ancestors_fields('slug'))

        return '/'

    def save(self, *args, **kwargs):
        if not self.slug:
            h1 = unidecode(self.h1.replace('.', '-').replace('+', '-'))
            if self.is_flat:
                self.slug = slugify(h1)

            #  We don't use slug field for model pages.
            #  I do not know how to avoid duplication data, we needed to respect unique_together.
            if self.is_model:
                self.slug = slugify('{}-{}'.format(h1, datetime.now().timestamp()))

        super(Page, self).save(*args, **kwargs)

    def get_ancestors(self, include_self=True) -> [models.Model]:
        def gather_ancestors(page):
            """Recursively gather ancestors in branch"""
            return gather_ancestors(page.parent) + [page] if page else []

        branch = gather_ancestors(self)
        return branch if include_self else branch[:-1]

    def get_ancestors_fields(self, *args, include_self=True) -> [[models.Field] or models.Field]:
        fields = [
            [getattr(page, field) for field in args]
            for page in self.get_ancestors(include_self=include_self)]

        if len(args) == 1:
            fields = list(chain(*fields))

        return fields


class CustomPageManager(models.Manager):
    def get_queryset(self):
        return super(CustomPageManager, self).get_queryset().filter(type=Page.CUSTOM_TYPE)


class FlatPageManager(models.Manager):
    def get_queryset(self):
        return super(FlatPageManager, self).get_queryset().filter(type=Page.FLAT_TYPE)


class ModelPageManager(models.Manager):
    def get_queryset(self):
        return super(ModelPageManager, self).get_queryset().filter(type=Page.MODEL_TYPE)


class CustomPage(Page):
    class Meta:
        proxy = True

    objects = CustomPageManager()

    def save(self, *args, **kwargs):
        self.type = Page.CUSTOM_TYPE
        super(CustomPage, self).save(*args, **kwargs)


class FlatPage(Page):
    class Meta:
        proxy = True

    objects = FlatPageManager()

    def save(self, *args, **kwargs):
        self.type = Page.FLAT_TYPE
        super(FlatPage, self).save(*args, **kwargs)


class ModelPage(Page):
    class Meta:
        proxy = True

    objects = ModelPageManager()

    def save(self, *args, **kwargs):
        self.type = Page.MODEL_TYPE
        super(ModelPage, self).save(*args, **kwargs)


class PageMixin(models.Model):
    """
    Add page functionality to your model.

    Requirements:
        - Inherit your model from this mixin.
        - Define CharField `name`.

    Functions:
        - Create relationships oneToOne for your model and Page.
        - Add save/delete hooks for related Page.
        - Sync relations with parent if them exist.

    Examples:
    obj1 = Obj.objects.create(...) -> p1 = Page.objects.create(h1=obj1.name)
    obj2 = Obj.objects.create(parent=obj1, ...) -> Page.objects.create(h1=obj1.name, parent=p1)
    obj2.delete() -> p2.delete()
    """

    class Meta:
        abstract = True

    # docs: https://goo.gl/MJIAYd
    MODEL_RELATION_PATTERN = '%(app_label)s_%(class)s'
    page = models.OneToOneField(
        Page, on_delete=models.CASCADE, related_name=MODEL_RELATION_PATTERN, null=True)

    @property
    def related_model_name(self):
        """
        Returns model class as string. For example:
        catalog.Category.type -> 'catalog_category'
        """
        return self.MODEL_RELATION_PATTERN % {
            'app_label': self._meta.app_label.lower(),
            'class': self._meta.model_name.lower(),
        }

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        super(PageMixin, self).delete(using, keep_parents)
        self.page.delete(using, keep_parents)

    @transaction.atomic
    def save(self, page_parent=None, page_fields=None, *args, **kwargs):
        self.update_related_page(page_parent, page_fields or {})
        super(PageMixin, self).save(*args, **kwargs)

    def update_related_page(self, parent, fields):
        def update_page():
            if not self.page:
                page_data = {
                    'h1': getattr(self, 'name', ''),
                    'related_model_name': self.related_model_name,
                    **fields,
                }
                self.page = ModelPage.objects.create(**page_data)
            else:
                self.page.h1 = self.name

        def update_page_tree():
            if getattr(self, 'parent', None):
                self.page.parent = self.parent.page
            else:
                self.page.parent = parent

            self.page.save()

        update_page()
        update_page_tree()
