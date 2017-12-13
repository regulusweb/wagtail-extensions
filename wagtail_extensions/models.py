from django.db import models
from django.utils.timezone import now

from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from wagtail.wagtailcore import blocks, fields
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from . import blocks as extension_blocks
from . import utils


class ContentPage(Page):

    class Meta:
        abstract = True

    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        models.PROTECT,
        null=True,
        blank=True,
        related_name='+'
    )
    body = fields.StreamField([
        ('text', extension_blocks.TextBlock()),
        ('table', TableBlock()),
        ('images', extension_blocks.ImagesBlock()),
        ('carousel', extension_blocks.CarouselBlock()),
    ], blank=True)

    content_panels = Page.content_panels + [
        ImageChooserPanel('featured_image'),
        StreamFieldPanel('body'),
    ]


class LinksSetting(BaseSetting):

    class Meta:
        abstract = True

    links = fields.StreamField([
        ('link', extension_blocks.LinkBlock()),
    ])

    panels = (
        StreamFieldPanel('links'),
    )


class ContactDetailsSetting(BaseSetting):

    CACHE_KEY_OPENING_TODAY = "wagtail_extensions_opening_today_{:%Y%m%d}"

    locations = fields.StreamField([
        ('location', extension_blocks.LocationBlock()),
    ])

    panels = (
        StreamFieldPanel('locations'),
    )

    class Meta:
        abstract = True

    @classmethod
    def get_opening_today_cache_key(cls):
        today = now().date()
        return cls.CACHE_KEY_OPENING_TODAY.format(today)

    @property
    def primary_location(self):
        return utils.true_or_nth(self.locations, lambda x: x.value.get('primary') == True)

    @property
    def primary_department(self):
        location = self.primary_location
        if location:
            departments = location.value.get('departments', [])
            return utils.true_or_nth(departments, lambda x: x.get('primary') == True)
        return None

    @property
    def primary_phone(self):
        department = self.primary_department
        if department:
            phones = self.primary_department.get('phones', [])
            return utils.nth(phones, 0)
        return None

    @property
    def primary_opening_times(self):
        location = self.primary_location
        if location:
            return location.value.get('opening_times')
        return None

    @property
    def primary_opening_today(self):
        if self.primary_opening_times:
            cache_key = self.get_opening_today_cache_key()
            return self.primary_opening_times.block.opening_today(self.primary_opening_times, cache_key=cache_key)
        return None


class SocialMediaSetting(BaseSetting):

    class Meta:
        abstract = True

    profiles = fields.StreamField([
        ('profile', extension_blocks.SocialMediaProfileBlock()),
    ])

    panels = (
        StreamFieldPanel('profiles'),
    )
