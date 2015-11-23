FeedMe
===========  

[![Build Status](https://travis-ci.org/dotKom/feedme.svg?branch=master)](https://travis-ci.org/dotKom/feedme) [![codecov.io](https://codecov.io/github/dotKom/feedme/coverage.svg?branch=master)](https://codecov.io/github/dotKom/feedme?branch=master)

A food ordering management system for Django. 

This project was started to help 'dotKom' with ordering food for their work nights. 

[Feedme on PyPi][1]

### Install via pip
`pip install feedme`

### Add app to project

- `INSTALLED_APPS = (…, 'feedme', …)`
- `url(r'^feedme/', include('feedme.urls', namespace='feedme'))`

Give some groups the permissions to use feedme.

---

## Standalone setup

This app supports a standalone setup, rather than integrating it into a current project.

All you need is to create a `base.html` with these blocks

- title
- styles
- submenu (nav)
- content

And use whatever template you want.
The submenu included in feedme uses a bootstrap submenu, and some bootstrap elements and classes.

[1]: https://pypi.python.org/pypi/feedme "feedme on PyPi"
