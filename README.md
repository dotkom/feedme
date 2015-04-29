FeedMe
===========  

[![Build Status](https://travis-ci.org/dotKom/feedme.svg?branch=master)](https://travis-ci.org/dotKom/feedme)

A food ordering management system for Django. 

This project was started to help 'dotKom' with ordering food for their work nights. 

[Feedme on PyPi][1]

### Install via pip
`pip install feedme`

### Manual install:

0. Download any of the releases.
1. Add "feedme" to INSTALLED_APPS  
 - `INSTALLED_APPS = (…, 'feedme', …)  
2. Make sure the groups defined in feedme/settings.py actually exists  
3. Include feedme.urls into system urls.py
 - `url(r'^feedme/', include('feedme.urls', namespace='feedme'))`  

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
