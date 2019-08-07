import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

test_requires = [
    'freezegun==0.3.9',
    'wagtail>=2.0,<2.1',
    'pytest==3.2.3',
    'pytest-django==3.1.2',
    'pytest-xdist==1.20.1',
    'psycopg2>=2.7.4',
]

setup(
    name='regulus-wagtail-extensions',
    version='2.5',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A few useful extensions for Wagtail',
    url='https://github.com/regulusweb/wagtail-extensions',
    author='Regulus Ltd',
    author_email='reg@regulusweb.com',
    python_requires='>=3.4',
    install_requires=[
        'wagtail>=2.0',
        'django-phonenumber-field',
        'phonenumbers',
        'python-dateutil',
        'wagtailgeowidget',
        # contact
        'django-honeypot>=0.6.0',
        'django-crispy-forms>=1.6.1',
        'bleach>=2.0.0',
    ],
    extras_require={
        'test': test_requires,
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
