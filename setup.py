from distutils.core import setup

setup(
    name = 'django-safeform',
    version = '1.0',
    url = 'http://github.com/simonw/django-safeform',
    author = 'Simon Willison',
    author_email = 'simon+safeform@simonwillison.net',
    description = 'CSRF protection for Django forms',
    long_description = open('README').read(),
    license = 'BSD',
    classifiers = [
        'Classifier: Development Status :: 4 - Beta',
        'Classifier: Environment :: Web Environment',
        'Classifier: Framework :: Django',
        'Classifier: Intended Audience :: Developers',
        'Classifier: License :: OSI Approved :: BSD License',
        'Classifier: Operating System :: OS Independent',
        'Classifier: Programming Language :: Python',
        'Classifier: Topic :: Internet :: WWW/HTTP',
    ],
    platforms = 'Any',
    packages = ['django_safeform']
)
