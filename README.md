FeedMe
===========  

A food ordering management system for Django.

This project was started to help 'dotKom' with ordering food for their work nights.

### Install via pip
`pip install git+https://github.com/dotKom/feedme.git`

### Manual install:

0. Download any of the releases.
1. Add "feedme" to INSTALLED_APPS  
 - `INSTALLED_APPS = (…, 'feedme', …)  
2. Add the following to settings:  
 - `FEEDME_GROUP = 'feedme_users_group'`  
 - `FEEDME_ADMIN_GROUP = 'feedme_admins_group'`  
 - Add the groups in admin if neccessary.  
3. Include feedme.urls into system urls.py
 - `url(r'^feedme/', include('feedme.urls'))`  

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

Remember to set and serve static files.
