FeedMe
===========

A food ordering system for OnlineWeb4 and Django. 

Install: 
1. Add "feedme" to INSTALLED_APPS 
`INSTALLED_APPS = (…, 'feedme', …) 

2. Add the following to settings: 
`FEEDME_GROUP = 'dotkom'` 
`FEEDME_ADMIN_GROUP = 'feedmeadmin'` 

Add the groups if neccessary. 

3. Include feedme.urls into system urls.py 
`url(r'^feedme/', include('feedme.urls'))` 


---

If this app is installed into OnlineWeb4, remember to prepend `apps` to `feedme` where appliccable (`apps.feedme`) 
