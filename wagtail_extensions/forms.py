from django import forms
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class ContactForm(forms.Form):

    subject_template = "wagtail_extensions/email/subject.txt"
    txt_template = "wagtail_extensions/email/message.txt"

    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': False}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(settings, "RECAPTCHA_PUBLIC_KEY", False):
            self.fields['captcha'] = ReCaptchaField(widget=ReCaptchaV3)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'name',
            'email',
            'message',
            StrictButton('Send', type="submit", css_class="btn btn-primary"),
        )

    def get_email_context(self):
        ctx = self.cleaned_data.copy()
        ctx['subject_prefix'] = settings.EMAIL_SUBJECT_PREFIX
        return ctx

    def send_email(self, to, subject_template, txt_template, reply_to):
        context = self.get_email_context()
        from_email = settings.DEFAULT_FROM_EMAIL
        subject = loader.render_to_string(subject_template, context)
        message = loader.render_to_string(txt_template, context)
        msg = EmailMessage(
            subject.strip(),
            message,
            from_email,
            to,
            reply_to=reply_to
        )
        msg.send()

    def get_to(self, page):
        if page.enquiry_email:
            return [page.enquiry_email]
        else:
            return [e for _, e in settings.MANAGERS]

    def save(self, page):
        # Forward enquiry
        to = self.get_to(page)
        reply_to = [self.cleaned_data['email']]
        self.send_email(to, self.subject_template, self.txt_template, reply_to)
