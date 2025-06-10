### Developers

- Cardona, Alissha Mae
- Damian, Beam Railey
- Fabregas, Aaron Kenzo

## SPLITIFY

Splitify is a debt management command line app that runs through Python and Mariadb. The user is allowed to:

- Sign up and Log in
- Add friends
- Remove friends
- Create debts between friends
- Create groups
- Edit groups
- Add members to groups
- Leave groups
- Delete groups
- Create debts within a group
- Settle or decrease debts
- Delete expenses
- Search expenses
- View all expenses made within a month
- View all expenses made with a friend
- View all expenses made with a group
- View current balance from all expenses
- View all friends with outstanding balance
- View all groups
- View all groups with an outstanding balance

# Setup

Make sure to installl the MySQL connector library for Python and MariaDB before running the application.

Install MariaDB: https://mariadb.com/downloads/
- Follow installation instructions.
-
-
- Enter root password and take note for later.


Test if MariaDB is functional:
- Open MariaDB Command Prompt

- Enter the following:
```
mysql -u root -p
#after entering password
show databases;
```


Try this in visual studio code:
```
pip install mysql-connector-python
```


!IMPORTANT!

- Go to main.py and press ctrl+F to use the find feature.
- Enter "TODO" in the search field
- Change the password of the root user connector to your root user password.
- Check your root user for a database called project
- If the database exists run this query: DROP DATABASE project
