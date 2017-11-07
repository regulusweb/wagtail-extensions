from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

from wagtail.wagtailcore import blocks


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
