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

# Screenshots

![image](https://github.com/user-attachments/assets/edc1960a-de2e-4dba-bb80-8c25f4f7443b) 
![image](https://github.com/user-attachments/assets/3117e190-8d06-44f3-a7df-c538fecfc531) 
![image](https://github.com/user-attachments/assets/51e47740-9543-4c7e-9309-09bbdd4212ec) 
![image](https://github.com/user-attachments/assets/1936c1f1-44a5-40e1-aae6-eef688717edb)
![image](https://github.com/user-attachments/assets/e74d650a-d2b7-400f-883e-888d108ce08c) 
![image](https://github.com/user-attachments/assets/edf0a68e-5366-4d44-9210-17523ddacc5a)





# Setup

Make sure to installl the MySQL connector library for Python and MariaDB before running the application.

Install MariaDB: https://mariadb.com/downloads/
- Follow installation instructions.
  
![image](https://github.com/user-attachments/assets/262b952d-88da-41e9-8301-5e15786a23b5) ![image](https://github.com/user-attachments/assets/1b3ed85d-c222-40ea-beb1-f5bc7e89a0a1) 

- Take note of root password for later.


Test if MariaDB is functional:
- Open MariaDB Command Prompt

![image](https://github.com/user-attachments/assets/39b8c3dd-6b06-49af-bcf8-d49898577713)


- Enter the following:
```
mysql -u root -p
//after entering password
show databases;
```


Try this in visual studio code:
```
pip install mysql-connector-python
```


## IMPORTANT

- Go to main.py and press ctrl+F to use the find feature.
- Enter "TODO" in the search field
- Change the password of the root user connector to your root user password.

![image](https://github.com/user-attachments/assets/88a551ee-ad3f-47eb-b572-2bd0140c44d6)

- Check your root user for a database called project
```
mysql -u root -p
//after entering password
show databases;
```
- If the database exists run this query: DROP DATABASE project
