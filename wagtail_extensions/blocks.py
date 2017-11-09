from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from wagtail.wagtailcore import blocks
from wagtailgeowidget.blocks import GeoBlock


class LinkBlock(blocks.StructBlock):
    text = blocks.CharBlock()
    page = blocks.PageChooserBlock(required=False)
    absolute_url = blocks.URLBlock(label="Url", required=False)

    class Meta:
        template = 'wagtail_extensions/blocks/link.html'

    def clean(self, value):
        page = value.get('page')
        absolute_url = value.get('absolute_url')
        if (not page and not absolute_url) or (page and absolute_url):
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
        return PhoneNumber.from_string(value)


class DepartmentBlock(blocks.StructBlock):

    name = blocks.CharBlock(required=False)
    phone = PhoneBlock(required=False)
    email = blocks.EmailBlock(required=False)

    def clean(self, value):
        phone = value.get('phone')
        email = value.get('email')
        if not phone and not email:
            errors = {
                'phone': ErrorList([
                    ValidationError('Either a phone or email must be defined'),
                ]),
            }
            raise ValidationError("There is a problem with this department", params=errors)
        return super().clean(value)


class LocationBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    address = AddressBlock(required=False)
    point = GeoBlock(required=False)
    departments = blocks.ListBlock(DepartmentBlock(label="department", required=False))
    primary = blocks.BooleanBlock(default=False, required=False)
