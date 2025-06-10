import friend
import group
import main


def expense_function(cursor, currentUserID):
    # This will act like showMenu, except only  for expense operations.
    print("\n============= EXPENSE MENU =============")
    print("\n          [1] Add an expense")
    print("          [2] Settle an expense")
    print("          [3] Delete an expense")
    print("          [4] Search for an expense")
    print("          [0] Return")
    print("\n========================================")

    choice = input("Input: ")
    if choice == "1":
        add_expense(cursor, currentUserID)
    elif choice == "2":
        settle_expense(cursor, currentUserID)
    elif choice == "3":
        delete_expense(cursor, currentUserID)
    elif choice == "4":
        search_expense(cursor, currentUserID)
    elif choice == "0":
        return False
    else:
        print("Unknown command")
    return True


# Add Expense
def add_expense(cursor, currentUserID):
    # ask if with friend or with group
    print("\n=== ADDING EXPENSE ===")
    print("[1] With Friend")
    print("[2] With Group")
    choice = input("Enter choice: ")

    if choice == "1":
        add_expense_friend(cursor, currentUserID)
    elif choice == "2":
        add_expense_group(cursor, currentUserID)
    else:
        print("Unknown command. Back to Main Menu.")


def add_expense_group(cursor, currentUserID):
    # print(LENDING MONEY TO GROUP)
    groups = group.view_group(cursor, currentUserID)

    if groups is not None and len(groups) != 0:
        # choose which group to do this with
        try:
            expenseNum = int(
                input("\nEnter index of group to transact with: "))
        except:
            print("Invalid index!")
            return
        if expenseNum > len(groups) - 1 or expenseNum < 0:
            print("Invalid index!")
            return

        # might add options here to split equally to all members or custom

        print("\nLENDING MONEY TO [", groups[expenseNum][1], "]")
        # ask for amount
        try:
            amount = float(input("\nEnter amount: "))
        except:
            print("Invalid amount!")
            return
        if (amount <= 0):
            print("Invalid amount!")
            return

        cursor.execute(
            "SELECT u.user_id, u.username FROM user u, group_member m WHERE u.user_id = m.user_id AND m.group_id = %s", (groups[expenseNum][0],))
        members = cursor.fetchall()
        # how much each member owes
        memDebt = round(amount/(len(members)), 2)
        # ask for brief details
        details = input("Brief description of expense: ")

        try:
            cursor.execute("INSERT INTO expense(amount, details, lender_user_id, group_id) VALUES (%s,%s,%s,%s) RETURNING expense_id", (
                memDebt * (len(members)-1), details, currentUserID, groups[expenseNum][0]))  # amount-memDebt bc u are lender u dont haave debt
            expenseID = cursor.fetchone()

            # add to owes table for members
            for i in range(len(members)):
                if not (currentUserID == members[i][0]):  # avoid yourself
                    try:
                        cursor.execute("INSERT INTO expense_owed(expense_id, user_id, amount_owed) VALUES (%s,%s,%s)", (
                            expenseID[0], members[i][0], memDebt))
                    except:
                        print("Error: expense owed")

            print("\nTRANSACTION: You lent P", amount,
                  "to [", groups[expenseNum][1], "].")
            for i in range(len(members)):
                if not (currentUserID == members[i][0]):  # avoid yourself
                    print("   ∟ [", members[i][1], "] owes [",
                          groups[expenseNum][1], "] P", memDebt,)

        except:
            print("Unsuccessful.")
    else:
        print("No groups.")


def add_expense_friend(cursor, currentUserID):
    # print friends list
    friends = friend.view_friend(cursor, currentUserID)
    if friends is not None and len(friends) != 0:
        # choose which friend to do this with
        try:
            expenseNum = int(
                input("\nEnter index of friend to transact with: "))
        except:
            print("Invalid index!")
            return
        if expenseNum > len(friends) - 1 or expenseNum < 0:
            print("Invalid index!")
            return

        # ask if you are lender or borrower
        print("\nAre you a Lender or a Borrower?")
        print("[1] Lender")
        print("[2] Borrower")
        choice = input("Enter choice: ")
        if (choice != "1" and choice != "2"):
            print("Invalid choice!")
            return

        # ask for amount
        try:
            amount = float(input("\nEnter amount: "))
        except:
            print("Invalid amount!")
            return
        if (amount <= 0):
            print("Invalid amount!")
            return

        # ask for brief details
        details = input("Brief description of expense: ")
        try:
            if choice == "1":
                cursor.execute("INSERT INTO expense(amount, details, lender_user_id, borrower_user_id) VALUES (%s,%s,%s,%s)", (
                    round(amount/2, 2), details, currentUserID, friends[expenseNum][0]))
                print("TRANSACTION: [", friends[expenseNum]
                      [1], "] borrowed P", amount/2, "from you.")

            elif choice == "2":
                cursor.execute("INSERT INTO expense(amount, details, lender_user_id, borrower_user_id) VALUES (%s,%s,%s,%s)", (
                    amount/2, details, friends[expenseNum][0], currentUserID))
                print("TRANSACTION: you borrowed P", amount/2,
                      "from [", friends[expenseNum][1], "].")
        except:
            print("Unsuccessful.")

# Settle Expense


def settle_expense(cursor, currentUserID):
    # ask if with friend or with group
    print("\n=== SETTLE EXPENSE ===")
    print("[1] With Friend")
    print("[2] With Group")
    choice = input("Enter choice: ")

    if choice == "1":
        settle_expense_friend(cursor, currentUserID)
    elif choice == "2":
        settle_expense_group(cursor, currentUserID)
    else:
        print("Unknown command. Back to Main Menu.")


def settle_expense_friend(cursor, currentUserID):
    # list expenses with friends
    print("\n=== EXPENSES TO SETTLE ===")
    cursor.execute("SELECT e.expense_id, u.username, e.amount FROM expense e, user u WHERE e.lender_user_id=u.user_id AND borrower_user_id = %s AND e.amount>0", (currentUserID,))
    expenses = cursor.fetchall()

    if expenses is not None and len(expenses) != 0:
        for i in range(len(expenses)):
            print(i, ": P", expenses[i][2], "to", expenses[i][1])
        try:
            settleNum = int(input("\nEnter index of expense to settle: "))
            toSettle = float(expenses[settleNum][2])

            loop = True
            while loop:

                subtract = float(input("Enter amount to subtract from debt: "))
                if subtract <= toSettle and subtract > 0:

                    newAmount = toSettle - subtract
                    cursor.execute(
                        "UPDATE expense SET amount = %s WHERE expense_id = %s", (newAmount, expenses[settleNum][0]))
                    print("TRANSACTION: you payed P", subtract,
                          "(P", newAmount, ") remaining.")

                    loop = False
                else:
                    print("Invalid amount for debt.")
        except:
            print("Invalid.")

    else:
        print("NONE")


def settle_expense_group(cursor, currentUserID):
    # list expense_owed with group
    print("\n=== EXPENSES TO SETTLE ===")
    cursor.execute("SELECT e.expense_id, g.group_name, o.amount_owed, e.amount FROM expense e, grouping g, expense_owed o WHERE e.expense_id=o.expense_id AND e.group_id=g.group_id AND o.user_id = %s AND o.amount_owed>0", (currentUserID,))
    expenses = cursor.fetchall()

    if expenses is not None and len(expenses) != 0:
        for i in range(len(expenses)):
            print(i, ": P", expenses[i][2], "to", expenses[i][1])
        try:
            settleNum = int(input("\nEnter index of expense to settle: "))
            toSettleIndiv = float(expenses[settleNum][2])
            toSettleGroup = float(expenses[settleNum][3])

            loop = True
            while loop:

                subtract = float(input("Enter amount to subtract from debt: "))
                if subtract <= toSettleIndiv and subtract > 0:

                    newAmount = toSettleIndiv-subtract
                    newGroupAmount = toSettleGroup-subtract
                    cursor.execute("UPDATE expense_owed SET amount_owed = %s WHERE expense_id = %s AND user_id = %s", (
                        newAmount, expenses[settleNum][0], currentUserID))
                    cursor.execute("UPDATE expense SET amount = %s WHERE expense_id = %s",
                                   (newGroupAmount, expenses[settleNum][0]))
                    print("TRANSACTION: you payed P", subtract,
                          "(P", newAmount, ") remaining.")
                    print("Group debt: P", newGroupAmount)

                    # if subtract == toSettleIndiv:
                    #     try:
                    #         cursor.execute(
                    #             "delete from expense_owed where amount_owed = 0")
                    #     except:
                    #         pass

                    loop = False
                else:
                    print("Invalid amount for debt.")
        except:
            print("Invalid")

    else:
        print("NONE")


def delete_expense(cursor, currentUserID):
    # ask if with friend or with group
    print("\n=== DELETE EXPENSE ===")
    print("[1] With Friend")
    print("[2] With Group")
    choice = input("Enter choice: ")

    if choice == "1":
        delete_expense_friend(cursor, currentUserID)
    elif choice == "2":
        delete_expense_group(cursor, currentUserID)
    else:
        print("Unknown command. Back to Main Menu.")

    pass


def delete_expense_friend(cursor, currentUserID):
    # list expenses with friends lender or borrower
    # ask if you are lender or borrower
    print("\nDelete as Lender or Borrower?")
    print("[1] Lender")
    print("[2] Borrower")
    choice = input("Enter choice: ")

    if choice == "1":
        cursor.execute("SELECT u.username, e.expense_id, e.amount from expense e, user u where (e.borrower_user_id= u.user_id) AND (lender_user_id = %s) AND e.amount>0 AND group_id IS NULL", (currentUserID,))
        expenses = cursor.fetchall()

        print("\n=== EXPENSES YOU LENT ===")
        if expenses is not None and len(expenses) != 0:
            for i in range(len(expenses)):
                print(i, ": P", expenses[i][2], "to", expenses[i][0])
            try:
                deleteNum = int(input("\nEnter index of expense to delete: "))
                cursor.execute(
                    "DELETE FROM expense WHERE expense_id=%s", (expenses[deleteNum][1],))

                print("TRANSACTION: Successfully deleted P",
                      expenses[deleteNum][2], "debt from [", expenses[deleteNum][0], "]")
            except:
                print("Invalid.")
        else:
            print("NONE")

    elif choice == "2":
        cursor.execute("SELECT u.username, e.expense_id, e.amount from expense e, user u where (e.lender_user_id= u.user_id) AND (borrower_user_id = %s) AND e.amount>0 AND group_id IS NULL", (currentUserID,))
        expenses = cursor.fetchall()
        print("\n=== EXPENSES YOU BORROWED ===")
        if expenses is not None and len(expenses) != 0:
            for i in range(len(expenses)):
                print(i, ": P", expenses[i][2], "from [", expenses[i][0], "]")
            try:
                deleteNum = int(input("\nEnter index of expense to delete: "))
                cursor.execute(
                    "DELETE FROM expense WHERE expense_id=%s", (expenses[deleteNum][1],))

                print("TRANSACTION: Successfully deleted P",
                      expenses[deleteNum][2], "debt to [", expenses[deleteNum][0], "]")
            except:
                print("Invalid.")
        else:
            print("NONE")
    else:
        print("Invalid.")


def delete_expense_group(cursor, currentUserID):
    cursor.execute("SELECT g.group_name, e.expense_id, e.amount from expense e, grouping g WHERE e.group_id=g.group_id and e.group_id IS NOT NULL AND lender_user_id = %s and amount>0", (currentUserID,))
    expenses = cursor.fetchall()
    if expenses is not None and len(expenses) != 0:
        print("\n=== EXPENSES YOU LENT ===")
        for i in range(len(expenses)):
            print(i, ": P", expenses[i][2], "to", expenses[i][0])
        try:
            deleteNum = int(input("\nEnter index of expense to delete: "))
            cursor.execute("DELETE FROM expense WHERE expense_id=%s",
                           (expenses[deleteNum][1],))
            cursor.execute(
                "DELETE FROM expense_owed WHERE expense_id=%s", (expenses[deleteNum][1],))

            print("TRANSACTION: Successfully deleted P",
                  expenses[deleteNum][2], "debt from [", expenses[deleteNum][0], "]")
        except:
            print("Invalid")
    else:
        print("NONE")


# Search Expense
# Flow: Ask for option 1 or 2 (All expenses / Specific expenses)
# If 'All expenses':
#   Display all expenses that the user is involved with.
#   Give option to show more details
#   If user puts details [ID]:
#       Check if expense is user-to-user
#           If user-to-user:
#              display only 1 borrower
#           else if user-to-group:
#              display multiple borrowers
# else if 'Specific expenses':
#   Get input expense ID
#   Check if expense is user-to-user
#       If user-to-user:
#          display only 1 borrower
#       else if user-to-group:
#          display multiple borrowers
def search_expense(cursor, currentUserID):
    print("\nHow would you like to search for expenses?")
    print("[1] Show ALL expenses")
    print("[2] Search for a specific expense ID")
    print("[0] Return")
    choice = (input("Choice: "))

    # Show ALL expenses
    if choice == "1":
        # Get all the expenses where the user is concerned.
        # - Case A: User is a lender
        # - Case B: User is a borrower
        # - Cases C and D: User is a lender for a group, and User borrows from a group.
        # However, Case C is already in Case A. To prevent duplicate entries, it has to be subtracted from the subquery.

        # This query returns all expenses where the user is involved with.
        cursor.execute("""
                       select * from expense 
                       where lender_user_id = %s
                       or borrower_user_id = %s
                       or (group_id in (select group_id from group_member where user_id = %s) and lender_user_id != %s)
                       """, (currentUserID, currentUserID, currentUserID, currentUserID))
        results = cursor.fetchall()
        print("\n=== Showing list of ALL expenses ===")
        for (id, amt, desc, date, grp, lid, bid) in results:
            print("[ID: {}] {} - {}. Generated on {}".format(id, amt, desc, date))
        main.detailsDisplayer(cursor, currentUserID)

    # Search expense via expense ID
    elif choice == "2":
        inputId = input("Enter ID: ")

        if inputId.isdigit():
            # This query only checks whether the expense selected has a NULL group_id or not.
            # This also checks whether the user has permission to view that expense.
            cursor.execute("""
               select group_id from expense where expense_id = %s
               and expense.expense_id in         
               (select expense_id from expense 
                   where lender_user_id = %s
                   or borrower_user_id = %s
                   or (group_id in (select group_id from group_member where user_id = %s) and lender_user_id != %s))
               """, (inputId, currentUserID, currentUserID, currentUserID, inputId))
            results = cursor.fetchall()

            if len(results) == 0:
                print(
                    "There is no expense using this ID, or you have no permissions to view this expense.")

            elif results[0][0] is not None:
                # If group ID is not null, we will select "borrowers" from expense_owed instead.
                # Only return values where user is involved in this expense.

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
                    """, (inputId, currentUserID, currentUserID, currentUserID, inputId,))
                results = cursor.fetchall()
                print("\n=== EXPENSE ID {} ===".format(inputId))
                print("Amount yet to be paid: {}".format(results[0][4]))
                print("Lender: {}".format(results[0][2]))
                print("Borrowers: ")
                for (eid, borrower, lender, amount, totalAmount) in results:
                    print("> {} - {}".format(borrower, amount))
                print("===================")

            elif results[0][0] is None:
                # If group id is NULL, then simply get the amount, lender, and borrower from the expense table.
                # Only return values where user is involved in this expense.

                # Get the expense ID which concerns the user while converting the user ids to usernames
                # This will get the expense IDs where the user is a lender or a borrower for a friend
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
                    inputId, currentUserID, currentUserID, currentUserID, inputId,))
                results = cursor.fetchall()
                print("\n=== EXPENSE ID {} ===".format(inputId))
                print("Amount yet to be paid: {}".format(results[0][3]))
                print("Lender: {}".format(results[0][2]))
                print("Borrower: {} - {}".format(results[0][1], results[0][3]))
                print("=== =========== ===")

            else:
                # In case of an internal error
                print("An error occurred.")

        else:
            print("Invalid ID")

    elif choice == "0":
        return False

    else:
        print("Unknown command")

    return True
