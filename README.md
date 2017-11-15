# Wagtail Extensions

For various reusabled wagtail blocks and models.

### Installing

```
$ pip install https://github.com/regulusweb/wagtail-extensions/archive/master.zip
```

Add `wagtail_extensions` and `wagtailgeowidget` to your `INSTALLED_APPS`:

```
INSTALLED_APPS = (
    # ...
    'wagtail_extensions',
    'wagtailgeowidget',
)
```

Set `GOOGLE_MAPS_V3_APIKEY` in your settings.
