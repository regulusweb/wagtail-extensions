![Tests](https://github.com/regulusweb/wagtail-extensions/workflows/Tests/badge.svg)

# Wagtail Extensions

For various reusable wagtail blocks and models and other common niceties.

### Installing

```
$ pip install regulus-wagtail-extensions
```

Add the following to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    'wagtail.contrib.table_block',
    'wagtail_extensions',
    'wagtailgeowidget',
    'captcha',
    'crispy_forms'
)
```

Set `GOOGLE_MAPS_V3_APIKEY`, `RECAPTCHA_PRIVATE_KEY` and `RECAPTCHA_PUBLIC_KEY` (use the V3 API) in your settings.
Recaptcha will not be enabled if the keys are not supplied, but it is strongly recommended to enable it in production.


### Contact functionality

`wagtail_extensions.mixins.ContactMixin` is a simple mixin which bakes a contact form into the inheriting Wagtail pages.

The mixin is an abstract Django model which has an enquiry_email field.
This field is also added to the `content_panels`.

NOTE: The crispy helper has `form_tag` set to `False`, so the form tag has to be rendered manually - this is to
make it easier to render the captcha field.

Set the `CRISPY_TEMPLATE_PACK` in your settings.

#### Usage
The Wagtail page you want to add this functionality should extend
`wagtail_extensions.mixins.ContactMixin`.

You will need to manually render the `captcha` field in your form, e.g., with `{{ form.captcha }}`.
