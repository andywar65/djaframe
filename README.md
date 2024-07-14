# django-a-frame
A [Django](https://djangoproject.com) app that shows 3D objects with [A-Frame](https://aframe.io/docs/1.6.0/introduction/)
## Requirements
This project is tested on Django 5.0.7 and Python 3.12. it uses [HTMX](https://htmx.org) and [django-htmx](https://django-htmx.readthedocs.io/en/latest/) to manage interactions. I use [Bootstrap 5](https://getbootstrap.com/) for styling. A `SQLite` database is enough.
## Installation
In your Django project root, clone this repository (`git clone https://github.com/andywar65/djaframe`) and be sure to install required packages (`python -m pip install -r requirements.txt`). Add `djaframe.apps.DjaframeConfig` to `INSTALLED_APPS` and `path("3D/", include("djaframe.urls", namespace="djaframe"))` to your project `urls.py`, migrate.
