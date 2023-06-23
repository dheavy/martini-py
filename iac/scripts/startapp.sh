#!/usr/bin/env bash

if [ "$1" == "-h" ]; then
    echo "This script will create an app inside the apps folder"
    echo "To use type the following line:"
    echo "bash start-app.sh app_name"
    echo "Replace app_name with the actual name for your app"
    elif [ "$1" != "" ]; then
    if [ ! -d "apps" ]; then
        mkdir apps
        touch apps/__init__.py
    fi
    mkdir apps/$1
    python manage.py startapp $1 apps/$1
    echo "Success! The app $1 has been aded, don't forget to add INSTALLED_APPS += ['apps.$1'] in your project's settings.py."
    echo "Also, don't forget to update the 'name' of the 'apps.$1' app in apps/$1/apps.py."
else
    echo "Error! One parameter is expected: app_name"
fi
