#!/bin/bash

# this will ask you for password, use 'manager' - this is our default pass for postgres container
echo "Create new user: macroplate_user"
echo "-------------------------------------------------------------------------------"
createuser -U postgres -h postgres -P -s -e  macroplate_user

echo
echo "Create new db: macroplate_dev"
echo "-------------------------------------------------------------------------------"
createdb -U macroplate_user -h postgres  macroplate_dev

echo
echo "Giving user standard password 'manager'"
echo "-------------------------------------------------------------------------------"
psql -U postgres -h postgres -c "ALTER USER macroplate_user WITH PASSWORD 'manager';"

echo
echo "Grant all privileges to the user on DB "
echo "-------------------------------------------------------------------------------"
psql -U postgres -h postgres -c "GRANT ALL PRIVILEGES ON DATABASE macroplate_dev TO macroplate_user;"
