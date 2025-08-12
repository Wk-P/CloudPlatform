#!/bin/bash
echo "Clear test enviroment..."
python manage.py flush --noinput


echo "Clear cloudplatform..."
mysql -u cloudadmin -p'soar009@CloudAdmin' -e "DROP DATABASE IF EXISTS cloudplatform; CREATE DATABASE cloudplatform CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
echo "Database rebuilding finished, migrate data to database ..."
python manage.py migrate
echo "Tables rebuilding finished."
