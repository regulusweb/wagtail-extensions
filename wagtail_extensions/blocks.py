import calendar
from collections import defaultdict
import datetime
from functools import partial
from itertools import groupby
import math
import uuid

from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.functional import cached_property
from django.utils.timezone import now
from phonenumber_field import phonenumber
from phonenumber_field.formfields import PhoneNumberField
from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailgeowidget.blocks import GeoBlock

from . import app_settings
from . import utils


class StrippedListBlock(blocks.ListBlock):
    """
    Does not save empty values
    """
    def get_prep_value(self, value):
        return [
            self.child_block.get_prep_value(item)
            for item in value if item != ''
        ]


class LinkBlockStructValue(blocks.StructValue):

    @cached_property
    def link_url(self):
        try:
            link_item = self['link'][0]
        except IndexError:
            return ''

        if link_item.block_type in ('page', 'document'):
            return link_item.value.url if link_item.value else ''
        else:
            return link_item.value      # raw url

    @cached_property
    def link_text(self):
        try:
            link_item = self['link'][0]
        except IndexError:
            return ''

        if link_item.block_type in ('page', 'document'):
            link_text = link_item.value.title  if link_item.value else ''
        else:
            link_text = link_item.value

        # If text is set then it takes precedence
        if self.get('text'):
            link_text = self['text']

        return link_text


class LinkBlock(blocks.StructBlock):

    text = blocks.CharBlock(required=False)
    # required=False because of https://github.com/wagtail/wagtail/issues/2665
    link = blocks.StreamBlock([
        ('page', blocks.PageChooserBlock()),
        ('document', DocumentChooserBlock()),
        ('url', blocks.CharBlock(label="URL (absolute or relative)"))
    ], max_num=1, required=False)

    def clean(self, value):
        result = super().clean(value)
        if len(result['link']) == 0 and getattr(self.meta, 'required', True):
            errors = {
                'link': ErrorList([
                    blocks.StreamBlockValidationError(non_block_errors=ErrorList([
                        ValidationError('A page, document or URL must be defined.'),
                    ]))
                ]),
            }
            raise ValidationError('LinkBlock validation error', params=errors)
        return result


    class Meta:
        template = 'wagtail_extensions/blocks/link.html'
        value_class = LinkBlockStructValue


class CarouselItemBlock(blocks.StructBlock):

    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)
    link = LinkBlock(required=False)

    class Meta:
        template = 'wagtail_extensions/blocks/carousel_item.html'


class CarouselBlock(blocks.StructBlock):

    items = blocks.ListBlock(CarouselItemBlock())
    show_thumbnails = blocks.BooleanBlock(default=False, required=False)

    class Meta:
        template = 'wagtail_extensions/blocks/carousel.html'

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        ctx['dom_id'] = 'carousel-'+uuid.uuid4().hex
        ctx['show_indicators'] = len(value.get('items', [])) > 1
        return ctx


class AddressBlock(blocks.StructBlock):

    lines = blocks.ListBlock(blocks.CharBlock(label="Line", required=False))

    class Meta:
        template = 'wagtail_extensions/blocks/address.html'


class PhoneBlock(blocks.FieldBlock):

    def __init__(self, required=True, help_text=None, **kwargs):
        self.field = PhoneNumberField(required=required, help_text=help_text)
        super().__init__(**kwargs)

    def get_prep_value(self, value):
        return str(value)

    def to_python(self, value):
        return phonenumber.to_python(value)


class DepartmentBlock(blocks.StructBlock):

    name = blocks.CharBlock(required=False)
    phones = StrippedListBlock(PhoneBlock(required=False))
    email = blocks.EmailBlock(required=False)
    primary = blocks.BooleanBlock(required=False, default=False)

    def clean(self, value):
        phones = value.get('phones', [])
        email = value.get('email')
        if not phones and not email:
            errors = {
                'phone': ErrorList([
                    ValidationError('Either a phone or email must be defined'),
                ]),
            }
            raise ValidationError("There is a problem with this department", params=errors)
        return super().clean(value)


class OpeningTimeBlock(blocks.StructBlock):
    """
    A semi-structured opening times block.
    """
    PUBLIC = 7
    PUBLIC_LABEL = 'Public holiday'
    WEEKDAYS = tuple(enumerate(calendar.day_name))
    ALL_DAYS = WEEKDAYS + ((PUBLIC, PUBLIC_LABEL),)

    weekday = blocks.ChoiceBlock(choices=ALL_DAYS, required=False)
    label = blocks.CharBlock(help_text='Optionally override default weekday label', required=False)
    date = blocks.DateBlock(help_text='Optionally specify a day these times are for', required=False)
    start = blocks.TimeBlock(required=False)
    end = blocks.TimeBlock(required=False)
    closed = blocks.BooleanBlock(default=False, required=False)

    class Meta:
        template = 'wagtail_extensions/blocks/opening_time.html'

    def clean(self, value):
        cleaned = super().clean(value)
        start, end, weekday, date = map(cleaned.get, ['start', 'end', 'weekday', 'date'])
        errors = defaultdict(ErrorList)

        if date and date < datetime.date.today():
            err = ValidationError('Dates need to be in the future')
            errors['date'].append(err)

        if (start or end) and not (weekday or date):
            err = ValidationError('Specifying a weekday or date is required')
            errors['weekday'].append(err)

        if start and end and end <= start:
            err = ValidationError('End must be after start')
            errors['end'].append(err)

        if errors:
            raise ValidationError("There is a problem with this opening time", params=errors)

        return cleaned

    def to_python(self, value):
        value = super().to_python(value)
        weekday = value.get('weekday')
        if weekday is not None and weekday != '':
            value['weekday'] = int(weekday)

            label = value.get('label')
            if value['weekday'] == self.PUBLIC and (label is None or label == ''):
                value['label'] = self.PUBLIC_LABEL
        return value

    @classmethod
    def single_date(cls, value):
        if value.get('date'):
            return True
        elif value.get('weekday') == cls.PUBLIC:
            return True
        else:
            return False

    @classmethod
    def next_date(cls, value):
        weekday = value.get('weekday')
        if weekday is not None and weekday != cls.PUBLIC:
            # Next date with this weekday
            today = now().date()
            return today + relativedelta(weekday=weekday)
        else:
            return None


class OpeningTimesBlock(blocks.StructBlock):
    """
    Using a StructBlock as subclassing ListBlock leads to problems when
    Wagtail does template rendering.
    """
    times = blocks.ListBlock(OpeningTimeBlock(required=False))

    class Meta:
        template = 'wagtail_extensions/blocks/opening_times.html'

    @staticmethod
    def time_keyfunc(opening_time):
        if opening_time.block.single_date(opening_time):
            return opening_time
        else:
            return (
                opening_time.get('closed'),
                opening_time.get('start'),
                opening_time.get('end'),
            )

    @classmethod
    def group_times(cls, value):
        # Read out groups to simplify templates
        return [list(group) for key, group in groupby(value, cls.time_keyfunc)]

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        ctx['times'] = self.group_times(value.get('times'))
        ctx['today'] = self.opening_today(value)
        return ctx

    @staticmethod
    def get_time_for_date(value, date):
        if value:
            times = value.get('times')
            specific_times = utils.first_true(times, lambda x: x.get('date') == date)
            times = specific_times or utils.first_true(times, lambda x: x.get('weekday') == date.weekday())
            if times:
                return dict(times)
        return None

    @classmethod
    def opening_today(cls, value, cache_key=None):
        today = now().date()
        partialed_getter = partial(cls.get_time_for_date, value, today)
        if cache_key:
            return cache.get_or_set(cache_key, partialed_getter, 60*60*24)
        else:
            return partialed_getter()


class LocationBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    address = AddressBlock(required=False)
    point = GeoBlock(required=False)
    departments = blocks.ListBlock(DepartmentBlock(label="department", required=False))
    opening_times = OpeningTimesBlock(required=False)
    primary = blocks.BooleanBlock(default=False, required=False)


class SocialMediaProfileBlock(blocks.StructBlock):

    icon = blocks.ChoiceBlock(choices=app_settings.SOCIAL_MEDIA_TYPES)
    url = blocks.URLBlock()

    class Meta:
        template = 'wagtail_extensions/blocks/social_media_profile.html'


class TextBlock(blocks.StructBlock):

    title = blocks.CharBlock(required=False)
    body = blocks.RichTextBlock()

    class Meta:
        template = 'wagtail_extensions/blocks/text.html'


class ImagesBlock(blocks.StructBlock):

    images = blocks.ListBlock(ImageChooserBlock(required=False))

    class Meta:
        template = 'wagtail_extensions/blocks/images.html'

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        images = value.get('images', None)
        ctx['column_width'] = math.floor(12 / len(images)) if images else 12
        return ctx
