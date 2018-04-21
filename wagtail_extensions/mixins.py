from django.contrib import messages
from django.db import models
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.decorators import method_decorator

from honeypot.decorators import check_honeypot
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page

from .forms import ContactForm
from .models import ContactSubmission


class ContactMixin(models.Model):

    form_class = ContactForm
    success_url = None
    store_submissions = True
    success_message = 'Thank you! We will get back to you as soon as possible.'

    enquiry_email = models.EmailField(
        blank=True,
        help_text="Email address that will receive enquiries",
        null=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('enquiry_email'),
    ]

    class Meta:
        abstract = True

    def get_form(self, request):
        return self.form_class(request.POST or None)

    def store_submission(self, form_data):
        # We do this here, instead of in the form, so that a project
        # can make use of this regardless of which form it uses.
        if self.store_submissions:
            ContactSubmission.objects.create(data=form_data)

    @method_decorator(check_honeypot)
    def serve(self, request, *args, **kwargs):
        self.form = self.get_form(request)
        if request.method == 'POST':
            if self.form.is_valid():
                self.form.save(page=self)  # Save triggers an email
                self.store_submission(self.form.cleaned_data)
                # Add a message to be displayed to the user
                success_message = self.get_success_message()
                if success_message:
                    messages.add_message(request, messages.INFO, success_message)

                request.session['enquiry_form_submitted'] = timezone.now().strftime('%Y-%m-%d %H:%M')
                # Redirect to the current page, to prevent resubmissions
                return HttpResponseRedirect(self.get_success_url())

        return super().serve(request, *args, **kwargs)

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx['form'] = self.form
        return ctx

    def get_success_url(self):
        return self.success_url or self.url

    def get_success_message(self):
        return self.success_message
