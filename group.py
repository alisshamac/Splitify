import friend


def group_function(cursor, currentUserID):
    # This will act like showMenu, except only for group operations.
    print("\n============= GROUP MENU =============")
    print("\n          [1] Add a group")
    print("          [2] Delete a group")
    print("          [3] Edit a group")
    print("          [4] View groups")
    print("          [5] Add member to a group")
    print("          [6] Leave a group")
    print("          [0] Return")
    print("\n=======================================")

    choice = input("Input: ")
    if choice == "1":
        add_group(cursor, currentUserID)
    elif choice == "2":
        delete_group(cursor, currentUserID)
    elif choice == "3":
        edit_group(cursor, currentUserID)
    elif choice == "4":
        view_group(cursor, currentUserID)
    elif choice == "5":
        add_member(cursor, currentUserID)
    elif choice == "6":
        leave_group(cursor, currentUserID)
    elif choice == "0":
        return False
    else:
        print("Unknown command")
    return True


def add_group(cursor, currentUserID):
    # get group name
    # add group
    # add group members
    print("\n=== ADDING GROUP ===")
    group_name = input("Group Name: ")

    print("\n=== ADDING MEMBERS ===")
    friend_list = friend.view_friend(cursor, currentUserID)
    if friend_list is not None and len(friend_list) != 0:
        try:
            cursor.execute(
                "INSERT INTO grouping(group_name) VALUES (%s) RETURNING group_id", (group_name,))
            groupID = cursor.fetchone()  # returns group_id of recently added group
            print("\nSuccessfully created group [", group_name, "]")
            cursor.execute("INSERT INTO group_member VALUES (%s,%s)",
                           (groupID[0], currentUserID))  # add self as member

            count = 0
            while True:
                try:
                    memNum = int(input("\nEnter index of new member: "))
                except:
                    print("Invalid index!")
                    if count > 0:
                        break
                    else:
                        continue

                try:
                    cursor.execute(
                        "SELECT * FROM group_member WHERE group_id = %s AND user_id = %s", (groupID[0], friend_list[memNum][0]))
                    memFind = cursor.fetchone()

                    if memFind is None:  # check if already member of group
                        cursor.execute(
                            "INSERT INTO group_member VALUES (%s,%s)", (groupID[0], friend_list[memNum][0]))
                        count += 1
                        print(
                            "Successfully added [", friend_list[memNum][1], "] to group [", group_name, "]")

                        again = input(
                            "\nAdd another? [1] Yes or [any key] No: ")

                        if again == "1":
                            pass
                        else:
                            break
                    else:
                        print("[", friend_list[memNum][1],
                              "] is already in [", group_name, "]")
                except:
                    print("Error: Unsuccessful add member.")
        except:
            print("Exit.")
    else:
        print("No members. No group has been made.")


def delete_group(cursor, currentUserID):
    # display groups
    cursor.execute(
        "SELECT group_id, group_name FROM grouping WHERE group_id IN (SELECT group_id FROM group_member WHERE user_id = %s)", (currentUserID,))
    groups = cursor.fetchall()

    if groups is not None and len(groups) != 0:
        print("\n=== GROUP LIST ===")
        for i in range(len(groups)):
            print(i, ": ", groups[i][1])

        try:
            delNum = int(input("\nEnter index of group to delete: "))
        except:
            print("Invalid index!")
            return

        try:
            # delete members
            cursor.execute(
                "DELETE FROM group_member WHERE group_id = %s", (groups[delNum][0],))

            # must delete all expenses in group
            cursor.execute(
                "delete from expense_owed where expense_id in (select expense_id from expense where group_id = %s)", (groups[delNum][0],))
            cursor.execute(
                "DELETE FROM expense WHERE group_id = %s", (groups[delNum][0],))

            # delete group
            cursor.execute(
                "DELETE FROM grouping WHERE group_id = %s", (groups[delNum][0],))

            print("Successfully deleted group.")

        except:
            print("Unsuccessful delete.")
    else:
        print("No groups.")


def edit_group(cursor, currentUserID):
    # display groups
    cursor.execute(
        "SELECT group_id, group_name FROM grouping WHERE group_id IN (SELECT group_id FROM group_member WHERE user_id = %s)", (currentUserID,))
    groups = cursor.fetchall()

    if groups is not None and len(groups) != 0:
        print("\n=== GROUP LIST ===")
        for i in range(len(groups)):
            print(i, ": ", groups[i][1])

        try:
            editNum = int(input("\nEnter index of group to edit: "))
            if editNum < 0 or editNum > len(groups) - 1:
                print("Invalid index!")
                return
            new_name = input("\nEnter new group name: ")
            print("\nCHANGING [", groups[editNum][1], "] TO [", new_name, "]")
        except:
            print("Invalid index!")
            return

        try:
            # update
            cursor.execute(
                "UPDATE grouping SET group_name = %s WHERE group_id = %s", (new_name, groups[editNum][0]))
        except:
            print("Unsuccessful edit.")
    else:
        print("No groups.")


def add_member(cursor, currentUserID):
    cursor.execute(
        "SELECT group_id, group_name FROM grouping WHERE group_id IN (SELECT group_id FROM group_member WHERE user_id = %s)", (currentUserID,))
    groups = cursor.fetchall()

    if groups is not None and len(groups) != 0:
        print("\n=== GROUP LIST ===")
        for i in range(len(groups)):
            print(i, ": ", groups[i][1])

        try:
            addNum = int(
                input("\nEnter index of group to add a member to: "))

            cursor.execute(
                "select * from friend join user on friend.friend_id = user.user_id where friend.user_id = %s and friend_id not in (select user_id from group_member where group_id = %s and user_id != %s);", (currentUserID, groups[addNum][0], currentUserID))
            nonMembers = cursor.fetchall()
            print("\n=== Friends that are not members of the group ===")
            if nonMembers is not None and len(nonMembers) != 0:
                for i in range(len(nonMembers)):
                    print(i, ": ", nonMembers[i][3])

            else:
                print("All friends are already in the group!")
                return

            friendToAdd = int(
                input("\nEnter index of friend to add: "))

            if friendToAdd < len(nonMembers) and friendToAdd >= 0:
                cursor.execute("insert into group_member values(%s, %s)",
                               (groups[addNum][0], nonMembers[friendToAdd][1]))
                print(
                    f"Successfully added {nonMembers[friendToAdd][3]} to group!")
            else:
                print("Invalid index!")

        except:
            print("Adding unsuccessful.")
    else:
        print("No groups.")


def leave_group(cursor, currentUserID):
    cursor.execute(
        "SELECT group_id, group_name FROM grouping WHERE group_id IN (SELECT group_id FROM group_member WHERE user_id = %s)", (currentUserID,))
    groups = cursor.fetchall()

    if groups is not None and len(groups) != 0:
        print("\n=== GROUP LIST ===")
        for i in range(len(groups)):
            print(i, ": ", groups[i][1])

        try:
            leaveNum = int(input("\nEnter index of group to leave from: "))

            cursor.execute("""
                select distinct group_id from expense left join expense_owed on expense.expense_id=expense_owed.expense_id 
where (borrower_user_id = %s or lender_user_id = %s or user_id = %s) and amount > 0 and group_id is not null;
            """, (currentUserID, currentUserID, currentUserID))
            data = cursor.fetchall()

            if (groups[leaveNum][0] not in [data[0] for data in data]):
                cursor.execute(
                    "delete from group_member where user_id = %s and group_id = %s", (currentUserID, groups[leaveNum][0],))
                print("Successfully left group.")

                cursor.execute(
                    "select user_id from group_member where group_id = %s;", (groups[leaveNum][0],))
                data2 = cursor.fetchall()
                if len(data2) == 0:
                    try:
                        cursor.execute(
                            "delete from grouping where group_id = %s;", (groups[leaveNum][0],))
                        print("Group now has no members; deleted")
                    except:
                        pass

            else:
                print("Cannot leave group with withstanding expenses!")
        except:
            print("Leave was unsuccessful.")
    else:
        print("No groups.")


def view_group(cursor, currentUserID):

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

    return groups
