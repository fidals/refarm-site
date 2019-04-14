from collections import namedtuple

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class PriceRange(admin.SimpleListFilter):
    """https://goo.gl/IYojpl"""
    title = _('price')
    parameter_name = 'price'
    price_lookup = 'price'

    def lookups(self, request, model_admin):
        price_segment = namedtuple('price_segment', ['name', 'size'])
        rub = _('rub')
        price_segment_list = [
            price_segment(
                f'{i - 1}',
                f'{i - 1} 000 - {i} 000 {rub}.'
            ) for i in range(2, 11)
        ]

        price_segment_list.insert(0, price_segment('0', f'0 {rub}.'))
        price_segment_list.append(price_segment('10', f'10 000+ {rub}.'))

        return price_segment_list

    def queryset(self, request, queryset):
        if not self.value():
            return

        if self.value() == '0':
            return queryset.filter(**{f'{self.price_lookup}__exact': 0})

        if self.value() == '10':
            return queryset.filter(**{f'{self.price_lookup}__gt': 10000})

        price_ranges = {i: (i * 1000, (i + 1) * 1000)
                        for i in range(0, 10)}
        range_for_query = price_ranges[int(self.value())]
        return queryset.filter(**{
            f'{self.price_lookup}__in': range(*range_for_query)
        })


class HasImages(admin.SimpleListFilter):
    """https://goo.gl/IYojpl"""
    title = _('has images')
    parameter_name = 'has_images'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Has images')),
            ('no', _('Has no images')),
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
            ('no', _('Has no content')),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return

        return (
            queryset.exclude(content='')
            if self.value() == 'yes' else
            queryset.filter(content='')
        )
