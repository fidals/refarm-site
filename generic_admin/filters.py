from collections import namedtuple

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class PriceRange(admin.SimpleListFilter):
    """https://goo.gl/IYojpl"""
    title = _('price')

    parameter_name = 'price'

    def lookups(self, request, model_admin):
        price_segment = namedtuple('price_segment', ['name', 'size'])
        rub = _('rub')
        price_segment_list = [
            price_segment(
                '{}'.format(i - 1),
                '{} 000 - {} 000 {}.'.format(i - 1, i, rub)
            ) for i in range(2, 11)
        ]

        price_segment_list.insert(0, price_segment('0', '0 {}.'.format(rub)))
        price_segment_list.append(price_segment('10', '10 000+ {}.'.format(rub)))

        return price_segment_list

    def queryset(self, request, queryset):
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
        return queryset.filter(**{
            '{}__price__in'.format(related_model_name): range(*range_for_query)
        })


class HasImages(admin.SimpleListFilter):
    """https://goo.gl/IYojpl"""
    title = _('has images')

    parameter_name = 'has_images'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Has images')),
            ('no', _('Has not images')),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return

        return (
            queryset.exclude(images=None)
            if self.value() == 'yes' else
            queryset.filter(images=None)
        )


class HasContent(admin.SimpleListFilter):
    """https://goo.gl/IYojpl"""
    title = _('has content')

    parameter_name = 'has_content'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Has content')),
            ('no', _('Has not content')),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return

        return (
            queryset.exclude(content='')
            if self.value() == 'yes' else
            queryset.filter(content='')
        )
