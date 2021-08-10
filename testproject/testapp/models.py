from wagtail.core.models import Page

from wagtail_extensions.models import ContactDetailsSetting
from wagtail_extensions.mixins import ContactMixin


class ContactPage(ContactMixin, Page):
    pass


class ContactDetailsTestSetting(ContactDetailsSetting):
    pass
