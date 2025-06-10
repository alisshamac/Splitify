import expense
import friend
import group
import mysql.connector as db

def generate_report(cursor, currentUserID):
    print("\n[1] View all expenses made within a month")
    print("[2] View all expenses made with a friend")
    print("[3] View all expenses made with a group")
    print("[4] View current balance from all expenses")
    print("[5] View all friends with outstanding balance")
    print("[6] View all groups")
    print("[7] View all groups with an outstanding balance")
    print("[0] Return")

    choice = input("Input: ")

    # [1] View all expenses made within a month
    if choice == "1":
        inputYear = input(
            "Which month would you like to view? [Ex. June, March 2022]: ")

    # If the user doesn't put a filter, then put the current month and year.
        if inputYear == "":
            print("No date detected. Using current date...")
            cursor.execute(
                """SELECT DATE_FORMAT(CURDATE(),"%M %Y") as d from expense""")
            try:
                inputYear = cursor.fetchall()[0][0]
            except:
                print("None")
                return
    # If the user puts "June" only, then the program automatically adds the current year.
        elif len(inputYear.split(" ")) == 1:
            print("No year detected. Using current year...")
            cursor.execute(
                """SELECT DATE_FORMAT(CURDATE(),"%Y") as d from expense""")
            try:
                inputYear = inputYear + " " + cursor.fetchall()[0][0]
            except:
                print("None")
                return

    # Select the expense ID's that match the filter, which is sorted by date.
    # It will only select expense IDs where the user is a lender, borrower, or borrower of a group the user is in.
        try:
            cursor.execute("""
                        select DATE_FORMAT(date, "%M %Y") as Month, details, expense_id, amount from expense 
                                            where (lender_user_id = %s
                                            or borrower_user_id = %s
                                            or (group_id in (select group_id from group_member where user_id = %s)
                                            and lender_user_id != %s))
                                            and LOWER(DATE_FORMAT(date, "%M %Y")) = LOWER(%s)
                                            GROUP BY Month, expense_id
                                            ORDER BY date;
                        """, (currentUserID, currentUserID, currentUserID, currentUserID, inputYear.strip()))

    # This is for cases where the person types an invalid filter.
        except Exception as e:
            print("No expenses found matching the filter " + inputYear)

        e = cursor.fetchall()
    # This sorts the expenses based on month
        currentDate = ""
        if len(e) != 0:
            for (month, desc, id, amt) in e:
                if not month == currentDate:
                    currentDate = month
                    print("## Expenses for " + currentDate + " ##")
                print("     [ID: {}] [{}] - {}".format(id, amt, desc))

    # Ask whether the user wants to ask more details about an expense
            detailsDisplayer(cursor, currentUserID)

    # This is for cases where the user inputs a valid filter, but has no results.
        else:
            print("No expenses found matching the filter " + inputYear)

    # [2] View all expenses made with a friend
    elif choice == "2":
    # Get all the user's friends
        cursor.execute(
            "SELECT u.user_id, u.username FROM user u WHERE u.user_id IN (SELECT f.friend_id FROM friend f WHERE f.user_id = %s)", (currentUserID,))
        results = cursor.fetchall()
    # Display the friends list
        if results is not None and len(results) != 0:
            print("\n=== FRIENDS ===")
            for friend in results:
                print(friend[0], ": ", friend[1])
        else:
            print("No friends.")
            return

    # Ask for the user's input for choosing which friend
        try:
            while True:
                inputID = input("Input your friend's user ID: ")
                if inputID == currentUserID:
                    print("You may not put your own ID!")
                    continue
                elif not inputID.isdigit():
                    print("Thats not a valid number.")
                    return False

                cursor.execute("""
                select * from friend where user_id = %s AND friend_id = %s
                """, (currentUserID, inputID))
                data = cursor.fetchall()

                if len(data) != 0:
                    break
                else:
                    print("User is not a friend!")
        except:
            print("Invalid ID")

    # Selects all expenses where the user and friend borrows from each other.
        print("\n == Friend to friend expenses ==")
        cursor.execute("""
            SELECT expense_id, amount, details FROM expense 
            WHERE (lender_user_id = %s AND borrower_user_id = %s) 
            OR (lender_user_id = %s  AND borrower_user_id = %s);
            """, (currentUserID, inputID, inputID, currentUserID))
        data = cursor.fetchall()

        if len(data) == 0:
            print("Empty.")
        else:
            for (id, amt, desc) in data:
                print(" [ID: {}] {} - {}".format(id, amt, desc))

    # 1. Select the group IDs where the user and friend has in common
    # 2. Select all the expenses that contain those group IDs.
    #    Only select where the user or a friend is a lender or borrower.
    # 3. Select all the rows in "expense_owed" that contain these expense IDs.
    #    It combines with the user table to get the names.
        print("\n == Expenses where you and your friend is part of a group ==")
        cursor.execute("""
            select c.details, c.expense_id, c.group_id, borrow.username as Borrower, lend.username as Lender, c.amount_owed from (user lend, user borrow)
            JOIN (
                    (
                    select details, expense_id, a.group_id, user_id, a.lender_user_id, amount_owed from expense_owed NATURAL JOIN expense a 
                    WHERE expense_id IN (
                        select expense_id from expense NATURAL JOIN (   
                                SELECT self.group_id
                                from group_member self,
                                group_member friend 
                                where self.group_id = friend.group_id AND self.user_id = %s AND friend.user_id = %s
                                ) as b
                    ) 
                    and (a.lender_user_id = %s AND expense_owed.user_id = %s) XOR (a.lender_user_id = %s AND expense_owed.user_id = %s) 
                ) as c 
            ) ON lend.user_id = c.lender_user_id AND borrow.user_id = c.user_id;
        """, (currentUserID, inputID, currentUserID, inputID, inputID, currentUserID))
        data = cursor.fetchall()

    # Display the data from the query
        if len(data) == 0:
            print("Empty.")
        else:
            prev = -1
            for (desc, id, grp, borrow, lend, amt) in data:
                if (prev != id):
                    prev = id
                    print(
                        " [ID: {}] [GROUP ID: {}] {} - {} ".format(id, grp, amt, desc))
                    print(" > Lender: {}".format(lend))
                    print(" > Borrower/s: ")
                    print("   > {}".format(borrow))
                else:
                    print("   > {}".format(borrow))

    # [3] View all expenses made with a group
    elif choice == "3":
        cursor.execute(
            "select * from grouping where group_id in (select group_id from group_member where user_id = %s);", (currentUserID,))
        results = cursor.fetchall()
        if results is not None and len(results) != 0:
            print("\n=== GROUPS ===")
            for group in results:
                print(group[0], ": ", group[1])
        else:
            print("No groups.")
            return

        while True:
            groupInput = input("Enter group ID: ")
            if not groupInput.isdigit():
                print("Thats not a valid number.")
                return False
            break

    # 1. Select expense IDs where the user is a lender and contains the group ID.
    # 2. Display the expense ID's, group ID, and username which comes from the user table.
        print("\nShowing expenses where user lends for a group: ")
        cursor.execute("""
        SELECT c.expense_id, c.group_id, username, c.amount FROM user JOIN
        (SELECT expense_id, group_id, lender_user_id, amount from expense WHERE group_id = %s AND lender_user_id = %s) as c
        ON user.user_id = c.lender_user_id;
        """, (groupInput, currentUserID))
        data = cursor.fetchall()

        if len(data) != 0:
            for (id, gr, lend, amt) in data:
                print(
                    "[ID: {}] [GROUP ID: {}] - Group owes you {}".format(id, gr, amt))
                print(" > Lender: {}".format(lend))
        else:
            print("None.")

        print("\nShowing expenses where user owes a group: ")

    # 1. Select rows in expense_owed where the user and the group is concerned with
    # 2. Select the username from the user table.
        cursor.execute("""
        SELECT c.expense_id, c.group_id, username as Lender, c.amount_owed FROM user JOIN
        (SELECT expense_id, group_id, lender_user_id, amount_owed from expense_owed NATURAL JOIN expense
        WHERE expense.group_id = %s AND expense_owed.user_id = %s) as c
        ON user.user_id = c.lender_user_id;
        """, (groupInput, currentUserID))

        data = cursor.fetchall()
        if len(data) != 0:
            for (id, gr, lend, amt) in data:
                print("[ID: {}] [GROUP ID: {}] - You owe {}".format(id, gr, amt))
                print(" > Lender: {}".format(lend))
        else:
            print("None.")

    elif choice == "4":
        print("\n=== Balance from all expenses ===")
        cursor.execute(
            "select expense.expense_id, username, amount_owed from expense, expense_owed, user where expense.expense_id = expense_owed.expense_id and expense.lender_user_id = user.user_id and expense_owed.user_id = %s and amount_owed > 0;", (currentUserID,))
        dataGroup = cursor.fetchall()

        cursor.execute(
            " select expense_id, amount, username from expense join user on expense.lender_user_id = user.user_id where borrower_user_id = %s and amount > 0;", (currentUserID,))
        dataFriend = cursor.fetchall()

        for expense in dataGroup:
            print("Expense ID:", expense[0], "| Lender:",
                  expense[1], "| Amount:", expense[2])
        for expense in dataFriend:
            print("Expense ID:", expense[0], "| Lender:",
                  expense[2], "| Amount:", expense[1])

        cursor.execute(
            "SELECT SUM(amount_owed) FROM expense_owed WHERE user_id = %s;", (currentUserID, ))
        groupTotal = cursor.fetchall()[0][0]
        if (groupTotal is None):
            groupTotal = 0

        cursor.execute(
            "SELECT SUM(amount) FROM expense WHERE borrower_user_id = %s;", (currentUserID, ))
        friendTotal = cursor.fetchall()[0][0]
        if (friendTotal is None):
            friendTotal = 0

        print("\nTotal balance for all expenses: ", groupTotal+friendTotal)

    elif choice == "5":
        print(
            "\n=== Friends with an outstanding balance to you (from group and friend expenses) ===")
        cursor.execute("""
        select user_id, username, sum(remaining_amount) from 
        (select user.user_id, username, case when borrower_user_id is null then expense_owed.user_id else borrower_user_id end as `borrower`,
        case when amount_owed is null then amount else amount_owed end as `remaining_amount`
        from expense left join expense_owed on expense.expense_id = expense_owed.expense_id join user on expense_owed.user_id = user.user_id or borrower_user_id = user.user_id where lender_user_id = %s) temp group by borrower having sum(remaining_amount) > 0;
                        """, (currentUserID,))
        data = cursor.fetchall()
        if (len(data) > 0):
            for i in data:
                print("Friend ID:", i[0], "| Friend Name:",
                      i[1], "| Balance:", i[2])
        else:
            print("None")

    elif choice == "6":
        cursor.execute(
            "SELECT group_id, group_name FROM grouping WHERE group_id IN (SELECT group_id FROM group_member WHERE user_id = %s)", (currentUserID,))
        groups = cursor.fetchall()

        if groups is not None and len(groups) != 0:
            print("\n=== GROUP LIST ===")
            for i in range(len(groups)):
                print("|-[", i, "]", groups[i][1])
                cursor.execute(
                    "SELECT u.user_id, u.username FROM user u, group_member m WHERE u.user_id = m.user_id AND m.group_id = %s", (groups[i][0],))
                members = cursor.fetchall()

                for j in range(len(members)):
                    print("|        ∟", members[j][1])
        else:
            print("No groups.")

    elif choice == "7":
        print(
            "\n=== Groups with an outstanding balance to you ===")
        cursor.execute("""select group_id, group_name, sum(amount) as "Balance" from
(select * from expense natural join grouping where lender_user_id = %s and borrower_user_id is null and amount > 0) temp group by group_id;""", (currentUserID,))
        data = cursor.fetchall()

        if (len(data) > 0):
            for i in data:
                print("Group ID:", i[0], "| Group Name: ",
                      i[1], "| Balance to you:", i[2])
        else:
            print("None")

    elif choice == 0:
        return False
    else:
        print("Unknown command")

    return True


def create_database(cursor):  # for root only

    # create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS project")
    cursor.execute("USE project")
    cursor.execute("""CREATE TABLE IF NOT EXISTS user(
                    user_id INT(8) NOT NULL AUTO_INCREMENT,
                    username VARCHAR(20) NOT NULL,
                    password VARCHAR(20) NOT NULL,
                    
                    CONSTRAINT user_username_uk UNIQUE KEY (username),
                    CONSTRAINT user_user_id_pk PRIMARY KEY (user_id)
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS friend(
                    user_id INT(8) NOT NULL,
                    friend_id INT(8) NOT NULL,

                    CONSTRAINT user_id_fk FOREIGN KEY(user_id) REFERENCES user(user_id),
                    CONSTRAINT friend_id_fk FOREIGN KEY(friend_id) REFERENCES user(user_id) 
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS grouping(
                    group_id INT(8) NOT NULL AUTO_INCREMENT,
                    group_name VARCHAR(20) NOT NULL,

                    CONSTRAINT grouping_name_uk UNIQUE KEY (group_name),
                    CONSTRAINT grouping_group_id_pk PRIMARY KEY (group_id)
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS group_member(
                    group_id INT(8) NOT NULL,
                    user_id INT(8) NOT NULL,
                    CONSTRAINT group_id_fk_group_member FOREIGN KEY(group_id) REFERENCES grouping(group_id),
                    CONSTRAINT user_id_fk_group_member FOREIGN KEY(user_id) REFERENCES user(user_id)  
                    )
                    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS expense (
                    expense_id INT (8) NOT NULL AUTO_INCREMENT,
                    amount DECIMAL (8, 2) NOT NULL,
                    details VARCHAR (50),
                    date DATE DEFAULT CURDATE(),
                    group_id INT(8),
                    lender_user_id INT(8),
                    borrower_user_id INT(8),

                    CONSTRAINT expense_expense_id_pk PRIMARY KEY (expense_id),
                    CONSTRAINT group_id_fk_expense FOREIGN KEY(group_id) REFERENCES grouping(group_id),
                    CONSTRAINT lender_id_fk FOREIGN KEY(lender_user_id) REFERENCES user(user_id),
                    CONSTRAINT borrower_id_fk FOREIGN KEY(borrower_user_id) REFERENCES user(user_id)
                    )
                    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS expense_owed(
                    expense_id INT(8) NOT NULL,
                    user_id INT(8) NOT NULL,
                    amount_owed DECIMAL (15,2) NOT NULL,
                    CONSTRAINT expense_id_pk_expense_owed PRIMARY KEY(expense_id, user_id)
                    )
                    """)


def grant_privilege(cursor, username):
    # grant select privileges
    cursor.execute("GRANT SELECT ON project.* TO %s", (username,))
    # grant insert privilege
    cursor.execute("GRANT INSERT ON project.friend TO %s", (username,))
    cursor.execute("GRANT INSERT ON project.grouping TO %s", (username,))
    cursor.execute("GRANT INSERT ON project.group_member TO %s", (username,))
    cursor.execute("GRANT INSERT ON project.expense TO %s", (username,))
    cursor.execute("GRANT INSERT ON project.expense_owed TO %s", (username,))
    # grant update privilege
    cursor.execute("GRANT UPDATE ON project.friend TO %s", (username,))
    cursor.execute("GRANT UPDATE ON project.grouping TO %s", (username,))
    cursor.execute("GRANT UPDATE ON project.group_member TO %s", (username,))
    cursor.execute("GRANT UPDATE ON project.expense TO %s", (username,))
    cursor.execute("GRANT UPDATE ON project.expense_owed TO %s", (username,))
    # grant delete privilege
    cursor.execute("GRANT DELETE ON project.friend TO %s", (username,))
    cursor.execute("GRANT DELETE ON project.grouping TO %s", (username,))
    cursor.execute("GRANT DELETE ON project.group_member TO %s", (username,))
    cursor.execute("GRANT DELETE ON project.expense TO %s", (username,))
    cursor.execute("GRANT DELETE ON project.expense_owed TO %s", (username,))


def log_in(root, cursor, username, password):
    try:
        # grant privileges if not yet granted
        grant_privilege(cursor, username)

        root.commit()
        root.close()

        user = db.connect(
            host="localhost",
            user=username,
            password=password,
        )

        cursor = user.cursor()
        cursor.execute("USE project")
        cursor.execute(
            "SELECT user_id FROM user WHERE username = %s and password =  %s", (username, password))
        currentUserID = cursor.fetchone()
        return user, currentUserID[0], False
    except Exception as e:
        print("Error: wrong credentials or account does not exist")
        return '', '', True


def sign_up(cursor, username, password):

    # create user

    # need try catch for wrong password
    cursor.execute(
        "CREATE USER IF NOT EXISTS %s IDENTIFIED BY %s", (username, password))
    try:
        # add user to user table
        cursor.execute(
            "INSERT INTO user (username,password) VALUES (%s,%s)", (username, password))
    except:
        print("The user ", username, " already exists. Proceeding to Log In.\n")

# log in and sign up menu
def startup():
    global username
    global password
    loop = True

    while loop:
        # connect to root user
        root = db.connect(
            host="localhost",
            user="root",
            password="password",  # TODO: edit root password
        )

        cursor = root.cursor()

        create_database(cursor)  # create database if not exists

        # sign in prompt
        print("\n[1] Sign Up")
        print("[2] Log In")
        print("[0] Exit")

        choice = input("Input: ")

        if choice == "1":
            username = input("\nEnter username: ")
            password = input("Enter password: ")
            if username != "" and password != "":
                sign_up(cursor, username, password)

            user, currentUserID, loop = log_in(
                root, cursor, username, password)
            
            isRunning = True
            while isRunning:
                # main menu
                isRunning = show_menu(user, currentUserID)
            return True

        # user must exist
        elif choice == "2":
            username = input("\nEnter username: ")
            password = input("Enter password: ")
            user, currentUserID, loop = log_in(
                root, cursor, username, password)
            
            isRunning = True
            while isRunning:
                # main menu
                isRunning = show_menu(user, currentUserID)
            return True

        elif choice == "0":
            print("Goodbye!")
            return False
        else:
            print("Unknown command.Try again.")

   

    user.commit()
    user.close()


def show_menu(user, currentUserID):

    cursor = user.cursor()
    cursor.execute("USE project")
    print("\n=======================================")
    print("               MAIN MENU                ")
    print("=======================================")
    print("\n          [1] Expense Menu")
    print("          [2] Friend Menu")
    print("          [3] Group Menu")
    print("          [4] Generate Report")
    print("          [0] Log Out")
    print("\n=======================================")

    choice = input("Input: ")
    if choice == "1":
        expense.expense_function(cursor, currentUserID)
    elif choice == "2":
        friend.friend_function(cursor, currentUserID)
    elif choice == "3":
        group.group_function(cursor, currentUserID)
    elif choice == "4":
        print("Generating a report: ")
        generate_report(cursor, currentUserID)
    elif choice == "0":
        return False
    else:
        print("Unknown command")

    """
    1. View all expenses made within a month;
    2. View all expenses made with a friend;
    3. View all expenses made with a group;
    4. View current balance from all expenses;
    5. View all friends with outstanding balance;
    6. View all groups;
    7. View all groups with an outstanding balance
    0. Exit
    :return:
    """

    user.commit()
    return True


def detailsDisplayer(cursor, currentUserID):
    details = input(
        "Type \"details _ID_\" to get more details about an expense. ")

    try:
        # If the user inputs "details [ID]"
        if details.split(" ")[0] == "details" and details.split(" ")[1].isdigit() and len(details.split(" ")) == 2:
            # This query only checks whether the group ID is NULL or not.
            # It also returns only the expenses the user is involved with.
            cursor.execute("""
                    select group_id from expense 
                            where (lender_user_id = %s
                            or borrower_user_id = %s
                            or (group_id in (select group_id from group_member where user_id = %s) and lender_user_id != %s))
                            and expense_id = %s
                    """, (currentUserID, currentUserID, currentUserID, currentUserID, int(details.split(" ")[1]),))
            results = cursor.fetchall()
            # If the group_id is NULL:
            # Also check whether there is permission to view this expense

            if len(results) != 0 and results[0][0] is None:
                # The expense is treated as a friend-to-friend expense.
                # It also makes sure that the user has access to this expense.
                cursor.execute("""
                            select e.expense_id as eid,
                            uA.username as borrower,
                            uB.username as lender,
                            e.amount as amount
                            from expense e, user uA, user uB
                            where
                            uA.user_id = e.borrower_user_id
                            and uB.user_id = e.lender_user_id
                            and e.expense_id = %s
                            and e.expense_id in
                            (select expense_id from expense 
                            where lender_user_id = %s
                            or borrower_user_id = %s
                            or (group_id in (select group_id from group_member where user_id = %s) and lender_user_id != %s))     
                            """, (
                    details.split(" ")[1], currentUserID, currentUserID, currentUserID, int(details.split(" ")[1]),))
                details = cursor.fetchall()
                print("\n=== EXPENSE ID {} ===".format(details.split(" ")[1]))
                print("Amount yet to be paid: {}".format(details[0][3]))
                print("Lender: {}".format(details[0][2]))
                print("Borrower: {} - {}".format(details[0][1], details[0][3]))
                print("=== =========== ===")

            # If the group ID is NOT NULL:
            elif len(results) != 0 and results[0][0] is not None:
                # Get the lender, borrower, amount on the same expense row.
                # Also makes sure that the expense ID is concerned with the user.
                print(details.split(" ")[1])
                print(currentUserID)

                # All this does is that it joins "expense, expense_owed" and "group_member, user"
                # This converts the expense and expense_owed's user IDs into usernames
                # The query will return a table which contains the same expense IDs, total amounts, and
                # lender name, but different borrower usernames and amounts
                cursor.execute("""
                            select 
                            expense.expense_id as eid, 
                            A.username as borrower,
                            B.username as lender,
                            expense_owed.amount_owed as amount,
                            expense.amount as totalAmount
                            from expense, expense_owed, group_member, 
                            user A, user B
                            where expense.expense_id = expense_owed.expense_id
                            and expense.group_id = group_member.group_id
                            and group_member.user_id = expense_owed.user_id
                            and expense_owed.user_id = A.user_id
                            and expense.lender_user_id = B.user_id
                            and group_member.user_id = A.user_id
                            and expense.expense_id = %s
                            and expense.expense_id in
                            (select expense_id from expense 
                            where lender_user_id = %s
                            or borrower_user_id = %s
                            or (group_id in (select group_id from group_member where user_id = %s) and lender_user_id != %s)) 
                            """, (
                    int(details.split(" ")[1]), currentUserID, currentUserID, currentUserID, currentUserID,))
                results = cursor.fetchall()
                print(results)
                print("\n=== EXPENSE ID {} ===".format(details.split(" ")[1]))
                print("Amount yet to be paid: {}".format(results[0][4]))
                print("Lender: {}".format(results[0][2]))
                print("Borrowers: ")
                for (eid, borrower, lender, amount, totalAmount) in results:
                    print("> {} - {}".format(borrower, amount))
                print("=== =========== ===")
                return True
            else:
                print(
                    "There is no expense using this ID, or you have no permissions to view this expense.")

        else:
            print("Returning to main menu")
            return False

    except Exception as e:
        print("Returning to main menu")
        return False


if __name__ == '__main__':
    start = True
    while start:
        # log in sign up
        start = startup()
