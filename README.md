[![Build Status](https://travis-ci.org/regulusweb/wagtail-extensions.svg?branch=master)](https://travis-ci.org/regulusweb/wagtail-extensions)

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
    'honeypot',
    'crispy_forms'
)
```

Set `GOOGLE_MAPS_V3_APIKEY` in your settings.


### Contact functionality

`wagtail_extensions.mixins.ContactMixin` is a simple mixin which bakes a contact form into the inheriting Wagtail pages.

The mixin is an abstract Django model which has an enquiry_email field.
This field is also added to the `content_panels`.

NOTE: The crispy helper has `form_tag` set to `False` to make it easy
to render the honeypot field within the form.

Set the `CRISPY_TEMPLATE_PACK` in your settings. `django-honeypot` also requires a few settings to be declared in settings.py.
See [django-honeypot](https://github.com/jamesturk/django-honeypot) for more information.

#### Usage
The Wagtail page you want to add this functionality should extend
`wagtail_extensions.mixins.ContactMixin`.

When rendering the form in your page template be sure to add the honeypot field using the
`render_honeypot_field` tag. Otherwise a HTTP BadRequest will explode when you try to submit the form without this.

Like so:

`{% load honeypot %}`

And then within the form include the honeypot field:

`{% render_honeypot_field %}`
