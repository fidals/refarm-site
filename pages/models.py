from unidecode import unidecode
from datetime import date
from itertools import chain

from django.db import models, transaction
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from mptt import models as mptt_models
from images.models import ImageMixin


class PageTemplate(models.Model):

    name = models.CharField(blank=False, max_length=255, unique=True)
    h1 = models.CharField(blank=True, max_length=255)
    keywords = models.CharField(blank=True, max_length=255, verbose_name=_('keywords'))
    description = models.TextField(blank=True, verbose_name=_('description'))
    title = models.TextField(blank=True, verbose_name=_('title'))
    seo_text = models.TextField(blank=True, verbose_name=_('seo text'))

    class Meta:
        verbose_name = _('Page Template')
        verbose_name_plural = _('Page Templates')

    def __str__(self):
        return self.name

    def render(self, field, context):
        template = Template(field)
        context = Context(context)
        return template.render(context)


class Page(mptt_models.MPTTModel, ImageMixin):
    # pages with same templates (ex. news, about)
    FLAT_TYPE = 'flat'
    # pages with unique templates (ex. index, order)
    CUSTOM_TYPE = 'custom'
    # pages related with other models like Product or Category
    # pages with type 'flat' or 'custom' have not related model
    MODEL_TYPE = 'model'

    # This field
    INDEX_PAGE_SLUG = ''

    # Use for reversing custom pages
    CUSTOM_PAGES_URL_NAME = 'custom_page'

    class Meta:
        unique_together = ('type', 'slug', 'related_model_name')
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    name = models.CharField(max_length=255, default='', db_index=True, verbose_name=_('name'))
    type = models.CharField(default=FLAT_TYPE, max_length=100, editable=False, db_index=True)
    # Name for reversing at related model
    related_model_name = models.CharField(blank=True, max_length=255, editable=False)

    parent = mptt_models.TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        verbose_name=_('parent'),
    )

    slug = models.SlugField(max_length=400, blank=True, db_index=True, verbose_name=_('slug'))
    is_active = models.BooleanField(
        default=True,
        blank=True,
        db_index=True,
        verbose_name=_('is active'),
    )
    position = models.IntegerField(default=0, blank=True, db_index=True, verbose_name=_('position'))
    content = models.TextField(blank=True, verbose_name=_('content'))
    date_published = models.DateField(
        default=date.today,
        blank=True,
        db_index=True,
        verbose_name=_('date published'),
    )

    menu_title = models.CharField(
        max_length=255, blank=True,
        help_text=_('This field will be shown in the breadcrumbs, menu items and etc.'),
        verbose_name=_('menu title'),
    )

    h1 = models.CharField(blank=True, max_length=255)
    keywords = models.CharField(blank=True, max_length=255, verbose_name=_('keywords'))
    description = models.TextField(blank=True, verbose_name=_('description'))
    seo_text = models.TextField(blank=True, verbose_name=_('seo text'))
    title = models.TextField(blank=True, verbose_name=_('title'))

    template = models.ForeignKey(
        PageTemplate,
        default=1,  # базовый шаблон страницы (ID=1), создается при миграции
        verbose_name=_('page template')
    )

    @classmethod
    def get_index(cls):
        return Page.objects.filter(type=cls.CUSTOM_TYPE, slug=cls.INDEX_PAGE_SLUG).first()

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def model(self) -> models.Model:
        """Return model, related to self"""
        return getattr(self, self.related_model_name, None)

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

    def __str__(self):
        return self.slug

    def __getattribute__(self, name):
        """Some fields should give default value."""
        attr = super(Page, self).__getattribute__(name)
        if not attr:
            if name in {'title', 'h1', 'description', 'keywords'}:
                return self.template.render(
                    getattr(self.template, name),
                    self.get_template_render_context(),
                )
            elif name in {'menu_title'}:
                return self.name
        return attr

    def get_absolute_url(self):
        """Different page types reverse different urls"""
        if self.is_model:
            return self.model.get_absolute_url()

        if self.is_custom:
            return reverse(Page.CUSTOM_PAGES_URL_NAME, args=(self.slug, ))

        if self.is_flat:
            return reverse('pages:flat_page', args=self.get_ancestors_fields('slug'))

        # TODO http://bit.ly/refarm-tail-enable-logging
        return '/'

    def save(self, *args, **kwargs):
        def update_slug():
            if self.slug or self.is_custom:
                return

            self.slug = slugify(unidecode(self.name.replace('.', '-').replace('+', '-')))

        update_slug()
        super(Page, self).save(*args, **kwargs)

    def get_ancestors_fields(self, *args, include_self=True) -> [[models.Field] or models.Field]:
        fields = tuple(
            tuple(getattr(page, field) for field in args)
            for page in self.get_ancestors(include_self=include_self)
        )

        if len(args) == 1:
            fields = tuple(chain.from_iterable(fields))

        return fields

    def get_template_render_context(self):
        return {
            'page': self,
        }


# ------- Managers -------
class CustomPageManager(mptt_models.TreeManager):
    def get_queryset(self):
        return super(CustomPageManager, self).get_queryset().filter(type=Page.CUSTOM_TYPE)


class FlatPageManager(mptt_models.TreeManager):
    def get_queryset(self):
        return super(FlatPageManager, self).get_queryset().filter(type=Page.FLAT_TYPE)


class ModelPageManager(mptt_models.TreeManager):
    def get_queryset(self):
        return super(ModelPageManager, self).get_queryset().filter(type=Page.MODEL_TYPE)


# ------- Proxies ----------
class CustomPage(Page):
    class Meta:
        proxy = True
        verbose_name = _('Custom Page')
        verbose_name_plural = _('Custom Pages')

    objects = CustomPageManager()

    def save(self, *args, **kwargs):
        self.type = Page.CUSTOM_TYPE
        super(CustomPage, self).save(*args, **kwargs)


class FlatPage(Page):
    class Meta:
        proxy = True
        verbose_name = _('Flat Page')
        verbose_name_plural = _('Flat Pages')

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

    @staticmethod
    def create_model_page_managers(model: models.Model):
        """Create managers for dividing ModelPage entities"""
        assert isinstance(model, type(models.Model)), 'arg should be ModelBase type'

        class ModelPageManager(mptt_models.TreeManager):
            def get_queryset(self):
                return super(ModelPageManager, self).get_queryset().filter(
                    related_model_name=model._meta.db_table)

        return ModelPageManager()


# ------- Mixins -------
class PageMixin(models.Model):
    """
    Add page functionality with sync page's relations feature to your model.

    Usage:
        - Inherit your model from this mixin.
        - Define CharField `name`.
        - If necessary define recursive relationships at itself with reversing
        name `parent`. It provide sync page's relations feature.

    Functions:
        - Create relationships oneToOne for your model and Page.
        - Sync page's relations with parent if it exist.

    Examples:
    >>> p1 = Page.objects.create(name=obj1.name)
    >>> obj1 = RelatedObject.objects.create(page=p1, ...)

    >>> p2 = Page.objects.create(name=obj1.name)
    >>> obj2 = RelatedObject.objects.create(parent=obj1, ...) -> p2.parent = p1; p2.save()
    """
    class Meta:
        abstract = True

    page = models.OneToOneField(
        Page, on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s',  # docs: https://goo.gl/MJIAYd
        null=True,
    )

    @classmethod
    def get_default_parent(cls):
        """You can override this method, if need a default parent"""
        return None

    @property
    def related_model_name(self):
        """
        Return model class as string. For example:
        catalog.Category.type -> 'catalog_category'
        """
        return self._meta.db_table

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Extend base class save of add `update related page` feature
        """
        def update_page_name():
            if not self.page:
                return
            self.page.name = self.name
            self.page.save()

        def update_relations():
            if not self.page:
                return

            self.page.parent = (
                self.parent.page if getattr(self, 'parent', None)
                else self.get_default_parent()
            )

            if not self.page.related_model_name:
                self.page.related_model_name = self.related_model_name

            self.page.save()

        update_page_name()
        update_relations()
        super(PageMixin, self).save(*args, **kwargs)


class SyncPageMixin(PageMixin):
    """
    Extend PageMixin with related page autocreation feature.

    Usage:
        - Inherit your model from this mixin.
        - Define CharField `name`.

    Functions:
        - Create relationships oneToOne for your model and Page.
        - Sync page's relations with parent if it exist.
        - Add save/delete hooks for related Page.

    Examples:
    >>> obj1 = RelatedObject.objects.create(...) -> p1 = Page.objects.create(name=obj1.name)
    >>> obj2.delete() -> RelatedObject.delete()
    """
    class Meta:
        abstract = True

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        """Extend base class method of add `auto delete related page's` feature"""
        super(SyncPageMixin, self).delete(using, keep_parents)
        self.page.delete(using, keep_parents)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Create related page on instance save() hook"""
        def create_page(**kwargs):
            if self.page:
                return

            page_data = {
                'name': getattr(self, 'name', ''),
                'related_model_name': self.related_model_name,
                'slug': slug,
                **kwargs,
            }

            self.page = ModelPage.objects.create(**page_data)
            self.save()

        super(SyncPageMixin, self).save(*args, **kwargs)
        slug = slugify(unidecode(self.name.replace('.', '-').replace('+', '-')))
        try:
            with transaction.atomic():
                create_page()
        except:
            create_page(slug='{}-{}'.format(slug, self.id))
