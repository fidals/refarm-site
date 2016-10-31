from collections import namedtuple

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class PriceRange(admin.SimpleListFilter):
    # Human-readable filter title
    title = _('price')

    # Parameter for the filter that will be used in the URL query
    parameter_name = 'price'

    def lookups(self, request, model_admin):
        """
        Return a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        price_segment = namedtuple('price_segment', ['name', 'size'])
        price_segment_list = [
            price_segment(
                '{}'.format(i - 1),
                _('{} 000 - {} 000 rub.'.format(i - 1, i))
            ) for i in range(2, 11)
        ]

        price_segment_list.insert(0, price_segment('0', _('0 rub.')))
        price_segment_list.append(price_segment('10', _('10 000+ rub.')))

        return price_segment_list

    def queryset(self, request, queryset):
        """
        Return the filtered queryset based on the value provided in the query string.
        """
        if not self.value():
            return

        related_model_name = queryset.first().related_model_name
        if self.value() == '0':
            return queryset.filter(**{'{}__price__exact'.format(related_model_name): 0})

        if self.value() == '10':
            return queryset.filter(**{'{}__price__gt'.format(related_model_name): 10000})

        price_ranges = {i: (i * 1000, (i + 1) * 1000)
                        for i in range(0, 10)}
        range_for_query = price_ranges[int(self.value())]
        return queryset.filter(**{'{}__price__in'.format(related_model_name): range(*range_for_query)})


class HasImages(admin.SimpleListFilter):
    # Human-readable filter title
    title = _('has images')

    # Parameter for the filter that will be used in the URL query
    parameter_name = 'has_images'

    def lookups(self, request, model_admin):
        """
        Return a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', 'Has images'),
            ('no', 'Has not images'),
        )

    def queryset(self, request, queryset):
        """
        Return the filtered queryset based on the value provided in the query string.
        """
        if not self.value():
            return

        return (
            queryset.exclude(images=None)
            if self.value() == 'yes' else
            queryset.filter(images=None)
        )


class HasContent(admin.SimpleListFilter):
    # Human-readable filter title
    title = _('has content')

    # Parameter for the filter that will be used in the URL query
    parameter_name = 'has_content'

    def lookups(self, request, model_admin):
        """
        Return a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', 'Has content'),
            ('no', 'Has not content'),
        )

    def queryset(self, request, queryset):
        """
        Return the filtered queryset based on the value provided in the query string.
        """
        if not self.value():
            return

        return (
            queryset.exclude(content='')
            if self.value() == 'yes' else
            queryset.filter(content='')
        )
