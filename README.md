# ProShare

Python Course comprehensive assignment. 

A problem sharing platform based on django and html.

## Necessity

Python 3.10

And necessary packages:

```
pip install django
pip install pymysql
pip install logging
```

MySql 8.0

Please install corresponding mysql server on your server and set the root password to 123456 or change it in ProShare/settings.py.
Then you need to create a database.

Run "mysql" in your shell and run:

```shell
CREATE DATABASE proshare;
```
After that, exit mysql shell and run:

```shell
python manage.py makemigrations account
python manage.py migrate
```

to set up the database properly.

Then you can run the server:

```shell
python manage.py runserver
```

If encounter some server error, delete the database using:

```shell
drop database proshare;
```

and create a new one.

## Command

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

(If you encounter Unknown column 'xxx' in 'field list') Run this when you want to delete all the data in a table:

```shell
python manage.py migrate <app_name> zero
```

Create a superuser:

```shell
python manage.py createsuperuser
```
