import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

test_requires = [
    'freezegun>=0.3,<0.4',
    'pytest-django>=3.8,<3.10',
    'pytest-xdist>=1.29,<1.32',
    'psycopg2-binary',
]

setup(
    name='regulus-wagtail-extensions',
    version='2.5.2',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A few useful extensions for Wagtail',
    url='https://github.com/regulusweb/wagtail-extensions',
    author='Regulus Ltd',
    author_email='reg@regulusweb.com',
    python_requires='>=3.5',
    install_requires=[
        'wagtail>=2.7,<2.9',
        'django-phonenumber-field',
        'phonenumbers',
        'python-dateutil',
        'wagtailgeowidget',
        # contact
        'django-honeypot>=0.6.0',
        'django-crispy-forms>=1.7',
        'bleach>=2.0.0',
    ],
    extras_require={
        'test': test_requires,
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
