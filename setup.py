import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

test_requires = [
    'wagtail==1.13',
    'pytest==3.2.3',
    'pytest-django==3.1.2',
    'pytest-xdist==1.20.1',
]

setup(
    name='wagtail-extensions',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A few useful extensions for Wagtail',
    url='https://regulusweb.com/',
    author='Craig Loftus',
    author_email='craig@regulusweb.com',
    install_requires=[
        'django-phonenumber-field',
        'wagtailgeowidget',
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
