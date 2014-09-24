FeedMe
===========  

A food ordering system for OnlineWeb4 and Django.

### Install via requirements/http+git
@TODO

### Install (probably deprecated):

1. Add "feedme" to INSTALLED_APPS  
 - `INSTALLED_APPS = (…, 'feedme', …)  
2. Add the following to settings:  
 - `FEEDME_GROUP = 'dotkom'`  
 - `FEEDME_ADMIN_GROUP = 'feedmeadmin'`  
 - Add the groups in admin if neccessary.  
3. Include feedme.urls into system urls.py
 - `url(r'^feedme/', include('feedme.urls'))`  

---

If this app is installed into OnlineWeb4, remember to prepend `apps` to `feedme` where applicable (`apps.feedme`)

---
# Standalone setup

Create a "base.html" with the blocks

- title
- styles
- submenu
- content

And use whatever template you want.
The submenu included in feedme uses a bootstrap submenu.

Remember to set and serve static files.
