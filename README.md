Pizzasystem
===========

Pizza ordering managing

Install:
1. Add "pizzasystem" to your INSTALLED_APPS setting like this:

      INSTALLED_APPS = (
          ...
          'pizzasystem',
      )

2. Add the following to settings:

      PIZZA_GROUP = 'dotkom'
      
      PIZZA_ADMIN_GROUP = 'pizzaadmin'

3. Include the pizzasystem URLconf in your project urls.py like this:

      url(r'^pizza/', include('pizzasystem.urls')),

4. Run `python manage.py syncdb` to create the pizzasystem models.

5. Visit http://127.0.0.1:8000/pizza/

**Remember to update version number in setup.py before making a new release!**
