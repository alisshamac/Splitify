def friend_function(cursor, currentUserID):
    # This will act like showMenu, except only for friends list operations.
    print("\n============= FRIEND MENU =============")
    print("\n          [1] Add a friend")
    print("          [2] Unfriend")
    print("          [3] View friends")
    print("          [0] Return")
    print("\n=======================================")

    choice = input("Input: ")
    if choice == "1":
        add_friend(cursor, currentUserID)
    elif choice == "2":
        unfriend(cursor, currentUserID)
    elif choice == "3":
        view_friend(cursor, currentUserID)
    elif choice == "0":
        return False
    else:
        print("Unknown command")
    return True


def add_friend(cursor, currentUserID):
    # view all users who are not friends
    cursor.execute("SELECT u.user_id, u.username FROM user u WHERE u.user_id NOT IN (SELECT f.friend_id FROM friend f WHERE f.user_id = %s OR f.friend_id = %s ) AND u.user_id != %s",
                   (currentUserID, currentUserID, currentUserID))
    results = cursor.fetchall()

    if results is not None and len(results) != 0:
        print("\n=== ADDING FRIEND ===")
        for i in range(len(results)):
            print(i, ": ", results[i][1])

        try:
            addNum = int(input("\nEnter index of user to add as friend: "))
            cursor.execute("INSERT INTO friend VALUES (%s,%s)",
                           (currentUserID, results[addNum][0]))
            cursor.execute("INSERT INTO friend VALUES (%s,%s)",
                           (results[addNum][0], currentUserID))
            print("User [", results[addNum][1],
                  "] successfully added as a friend!")
        except:
            print("Add friend unsuccesful.")

    else:
        print("No users to add")


def unfriend(cursor, currentUserID):
    # list of friends
    results = view_friend(cursor, currentUserID)
    if results is not None and len(results) != 0:

        try:
            unfriendNum = int(input("\nEnter index of user to unfriend: "))
            if not (unfriendNum >= 0 and unfriendNum < len(results)):
                print("Invalid index!")
                return
        except:
            print("Invalid index!")
            return

        cursor.execute(
            """select distinct user_id from group_member where group_id in (select group_id from group_member where user_id = %s);""", (currentUserID,))
        dataCommonGroup = cursor.fetchall()

        cursor.execute("""
        select lender_user_id, borrower, sum(remaining_amount) as `balance` from
    (select lender_user_id, case when borrower_user_id is null then expense_owed.user_id else borrower_user_id end as `borrower`,
    case when amount_owed is null then amount else amount_owed end as `remaining_amount`
    from expense left join expense_owed on expense.expense_id = expense_owed.expense_id join user on expense_owed.user_id = user.user_id or borrower_user_id = user.user_id where amount > 0) temp group by lender_user_id, borrower having (borrower = %s and lender_user_id = %s) or (borrower = %s and lender_user_id = %s);
        """, (currentUserID, results[unfriendNum][0], results[unfriendNum][0], currentUserID))
        dataBalance = cursor.fetchall()

        if (results[unfriendNum][0] in [data[0] for data in dataCommonGroup]):
            print("Cannot unfriend someone with a common group!")
        elif (len(dataBalance) > 0):
            print("Cannot unfriend someone with an existing expense with you!")
        else:
            try:
                cursor.execute("DELETE FROM friend WHERE user_id = %s AND friend_id = %s",
                               (currentUserID, results[unfriendNum][0],))
                cursor.execute("DELETE FROM friend WHERE user_id = %s AND friend_id = %s",
                               (results[unfriendNum][0], currentUserID))
                print("User [", results[unfriendNum]
                      [1], "] successfully unfriended!")
            except:
                print("Unfriend unsuccesful.")


def view_friend(cursor, currentUserID):
    # list of friends
    cursor.execute(
        "SELECT u.user_id, u.username FROM user u WHERE u.user_id IN (SELECT f.friend_id FROM friend f WHERE f.user_id = %s)", (currentUserID,))
    results = cursor.fetchall()
    print("\n=== FRIENDS ===")
    if results is not None and len(results) != 0:
        for i in range(len(results)):
            print(i, ": ", results[i][1])
    else:
        print("No friends.")

    return results
