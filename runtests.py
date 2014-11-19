import sys

try:
    from django.conf import settings

    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            }
        },
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            ),
        ROOT_URLCONF="feedme.urls",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "feedme",
        ],
        SITE_ID=1,
        NOSE_ARGS=['-s'],
    )

    try:
        import django
        setup = django.setup
    except AttributeError:
        pass
    else:
        setup()

    #from django.test.simple import DjangoTestSuiteRunner
    from django_nose import NoseTestSuiteRunner
except ImportError:
    raise ImportError("Missing NoseTestSuiteRunner -- install nosetests")


def run_tests(*test_args):
    if not test_args:
        try:
            # This runs on Online/dotKom Jenkins to create statistics
            import nosexcover
            test_args = ['feedme', '--with-xunit', '--with-xcoverage', '--cover-package=feedme']
        except:
            test_args = ['feedme', '--with-coverage','--cover-package=feedme']


    # Run tests
    test_runner = NoseTestSuiteRunner(verbosity=1)

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
