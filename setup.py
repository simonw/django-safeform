from distutils.core import setup

setup(
    name = 'django-safeform',
    version = '2.0.0',
    url = 'http://github.com/simonw/django-safeform',
    author = 'Simon Willison',
    author_email = 'simon+safeform@simonwillison.net',
    description = 'CSRF protection for Django forms',
    long_description = open('README').read(),
    license = 'BSD',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    platforms = 'Any',
    packages = ['django_safeform']
)
