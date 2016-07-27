from unidecode import unidecode

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify


class SeoMixin(models.Model):
    title = models.CharField(max_length=255, null=False, blank=True)
    _h1 = models.CharField(default='', max_length=255, null=False, blank=True)
    keywords = models.CharField(
        max_length=255, default='', null=False, blank=True)
    description = models.TextField(default='', null=False, blank=True)

    @property
    def h1(self):
        return self._h1 or self.title

    @h1.setter
    def h1(self, value):
        self._h1 = value

    class Meta:
        abstract = True


class Page(SeoMixin, models.Model):

    # pages without related models: contacts, about site, etc
    DEFAULT_TYPE = 'page'
    # hardcoded pages: catalog/, index page, etc
    STRUCT_TYPE = 'structure'

    class Meta:
        # for example, every category's page should have unique slug
        unique_together = ('type', 'slug')

    slug = models.SlugField(max_length=255, blank=True)
    # Django.conf.url name for generating page url
    # Used in get_absolute_url method only for pages with type=='structure'
    route = models.SlugField(max_length=255, null=True, blank=True)
    _menu_title = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.IntegerField(default=0, null=False)
    type = models.CharField(  # Page with type 'page' or 'structure'have no related model
        default=DEFAULT_TYPE, max_length=255, null=False, blank=True)
    content = models.TextField(null=True, blank=True)
    seo_text = models.TextField(null=True, blank=True)
    _date_published = models.DateField(auto_now_add=True, null=True, blank=True)

    _parent = models.ForeignKey(
        'Page',
        on_delete=models.CASCADE,
        related_name='children',
        null=True, blank=True, default=None
    )

    @property
    def parent(self):

        def is_category(model):
            return type(model).__name__.lower() == 'category'

        def is_page_of_root_category():
            return is_category(self.model) and not self._parent

        # Duker 20.07.16 - Dirty check of 'category_tree' special case.
        # Now i don't know how to inject this code correctly from catalog app
        if is_page_of_root_category():
            return get_or_create_struct_page(slug='category_tree')
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def date_published(self):
        if self._date_published:
            return self._date_published
        if hasattr(settings, 'SITE_CREATED'):
            return settings.SITE_CREATED
        return None

    @date_published.setter
    def date_published(self, value):
        self._date_published = value

    @property
    def menu_title(self):
        return self._menu_title or self.title

    @menu_title.setter
    def menu_title(self, value):
        self._menu_title = value

    @property
    def model(self) -> models.Model:
        """Return model, related to self"""
        if self.type not in [self.DEFAULT_TYPE, self.STRUCT_TYPE]:
            return getattr(self, self.type)

    def __str__(self):
        return self.title

    def get_path(self, include_self=True):
        """Get page parents list"""
        path = []
        page = self
        while page:
            if page != self or include_self:
                path = [page] + path
            page = page.parent
        return path

    def get_path_as_slugs(self):
        """Get page parent slugs list"""
        return tuple(p.slug for p in self.get_path())

    def get_absolute_url(self):

        # Different page types reverse different urls
        if self.model:
            return self.model.get_absolute_url()

        if self.type == self.STRUCT_TYPE:
            return reverse(self.route)

        if self.type == self.DEFAULT_TYPE:
            return reverse('pages:page', args=self.get_path_as_slugs())

        return '/'

    @property
    def is_section(self):
        """
        Defines if page is a list of other pages or not. Used in accordion.
        """
        return (
            self.type == self.DEFAULT_TYPE and
            not self.parent and
            self.children
        )

    @property
    def image(self):
        if self.model and hasattr(self.model, 'image'):
            return self.model.image

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        super(Page, self).save(*args, **kwargs)


class PageConnectorMixin(models.Model):
    """
    To connect your model to page, inherit your model from from this mixin.
    And you should (re)define some attributes:
     - title - str for page's title (h1)
     - parent - if your model has it

    Mixin contains:
     - Fields set, that every entity should have to connect to model
     - Model<->page sync logic
    """

    class Meta:
        abstract = True

    MODEL_RELATION_PATTERN = '%(app_label)s_%(class)s'

    # if we get some error on Page-Model connection,
    # we use id to output error message
    id = None
    parent = None
    title = None
    slug = None

    page = models.OneToOneField(
        Page, on_delete=models.SET_NULL, null=True, blank=True,
        related_name=MODEL_RELATION_PATTERN  # Dj doc: https://goo.gl/MJIAYd
    )

    @property
    def type(self):
        """
        Returns model class as string. For example:
        catalog.Category.type -> 'catalog_category'
        """
        return self.MODEL_RELATION_PATTERN % {
            'app_label': self._meta.app_label.lower(),
            'class': self._meta.model_name.lower(),
        }

    def save(self, *args, **kwargs):
        self.update_page()
        super(PageConnectorMixin, self).save(*args, **kwargs)

    def assert_page_is_correct(self):
        assert self.page, '{} #{} has no page'.format(self.type, self.id)
        is_correct = (self.type, self.slug) == (self.page.type, self.page.slug)
        assert is_correct, '{} #{} has wrong page'.format(self.type, self.id)

    def update_page(self):
        self.__update_page_fields()
        self.__update_page_relation()
        self.__update_page_tree()

    def __update_page_fields(self):
        if not self.page:
            return
        source, dest = self, self.page
        dest.type, dest.slug = source.type, source.slug
        dest.save()

    def __update_page_relation(self):
        self.page, _ = Page.objects.get_or_create(
            type=self.type,
            slug=self.slug,
            defaults={'title': self.title, }
        )

    def __update_page_tree(self):
        """
        Me - current category.
        Set my parent.page as my page.parent.
        Precondition:
        My page and my parent's page should be correct.
        """
        self.assert_page_is_correct()
        if not self.parent:
            self.page.parent = None
            return
        self.parent.assert_page_is_correct()
        self.page.parent = self.parent.page
        self.page.save()


def get_or_create_struct_page(*, slug):
    """
    Get or create struct page object. For example /catalog/ or index page
    Get default fields from settings.PAGES set
    """

    page_fields = (
        settings.PAGES[slug]
        if settings.PAGES and slug in settings.PAGES
        else {'title': slug}
    )

    return Page.objects.get_or_create(
        type=Page.STRUCT_TYPE, slug=slug, defaults=page_fields,
    )[0]
