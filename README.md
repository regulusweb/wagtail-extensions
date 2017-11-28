# Wagtail Extensions

For various reusabled wagtail blocks and models.

### Installing

```
$ pip install https://github.com/regulusweb/wagtail-extensions/archive/master.zip
```

Add the following to your `INSTALLED_APPS`:

```
INSTALLED_APPS = (
    'wagtail.contrib.table_block',
    'wagtail_extensions',
    'wagtailgeowidget',
)
```

Set `GOOGLE_MAPS_V3_APIKEY` in your settings.
