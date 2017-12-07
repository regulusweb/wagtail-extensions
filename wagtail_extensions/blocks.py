import calendar
from collections import defaultdict
import datetime
from itertools import groupby
import math
import uuid

from dateutils import relativedelta
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from phonenumber_field import phonenumber
from phonenumber_field.formfields import PhoneNumberField
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtailgeowidget.blocks import GeoBlock

from . import app_settings


class StrippedListBlock(blocks.ListBlock):
    """
    Does not save empty values
    """
    def get_prep_value(self, value):
        return [
            self.child_block.get_prep_value(item)
            for item in value if item != ''
        ]


class LinkBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=False)
    page = blocks.PageChooserBlock(required=False)
    absolute_url = blocks.CharBlock(label="Url", required=False)

    class Meta:
        template = 'wagtail_extensions/blocks/link.html'

    def clean(self, value):
        if value.get('page') and value.get('absolute_url'):
            errors = {
                'page': ErrorList([
                    ValidationError('Either a page or url must be defined'),
                ]),
            }
            raise ValidationError('There is a problem with this link', params=errors)

        return super().clean(value)

    def to_python(self, value):
        value = super().to_python(value)
        if value.get('page'):
            value['url'] = value['page'].url
        elif value.get('absolute_url'):
            value['url'] = value.get('absolute_url')
        return value

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        ctx['has_url'] = 'url' in value
        return ctx


class CarouselItemBlock(blocks.StructBlock):

    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)
    link = LinkBlock(required=False)

    class Meta:
        template = 'wagtail_extensions/blocks/carousel_item.html'


class CarouselBlock(blocks.StructBlock):

    items = blocks.ListBlock(CarouselItemBlock())

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

    Period is left as a free text input to allow for
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
        template = 'wagtail_extensions/blocks/openingtime.html'

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
        if weekday is not None:
            weekday_int = int(weekday)
            value['weekday'] = weekday_int

            label = value.get('label')
            if weekday_int == self.PUBLIC and not label:
                value['label'] = self.PUBLIC_LABEL

            if weekday_int == self.PUBLIC or value.get('date'):
                value['specific'] = True
            else:
                # Next date with this weekday
                today = datetime.date.today()
                value['next_date'] = today + relativedelta(weekday=weekday_int)
        return value


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
        if opening_time.get('specific'):
            return opening_time
        else:
            return (
                opening_time.get('start'),
                opening_time.get('end'),
            )

    @classmethod
    def group_times(cls, value):
        return groupby(value, cls.time_keyfunc)

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        grouped_times = self.group_times(value.get('times'))
        # Read out groups to simplify templates
        ctx['times'] = [list(grouper) for key, grouper in grouped_times]
        return ctx


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
        ctx['column_width'] = math.floor(12 / len(value.get('images', [])))
        return ctx
