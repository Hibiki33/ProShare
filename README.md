# wfynb

Python Course comprehensive assignment. 

A problem sharing platform based on django and html.

## necessity

Python 3.10

MySql 8.0

And necessary packages:

```
pip install django
pip install pymysql
```

## command

Run server:

```shell
python manage.py runserver
```

Start a new app:

```shell
python manage.py startapp <app_name>
```

After creating new models, run the following command to generate migration files:

```shell
python manage.py makemigrations <app_name>
```

Then run the following command to apply the migration files:

```shell
python manage.py migrate
```

Create a superuser:

```shell
python manage.py createsuperuser
```

## Database

The password of mysql should be set to '123456', or you can change it in settings.py.