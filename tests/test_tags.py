from wagtail_extensions.templatetags.wagtailextensions_tags import bleachclean


def test_bleanclean_cleandata():
    cleaned = bleachclean('Hello')

    assert cleaned == 'Hello'


def test_bleanclean_strips():
    cleaned = bleachclean('<script>evil</script>')

    assert cleaned == 'evil'
