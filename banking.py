import sqlite3
import random
import string


class System:

    def __init__(self, only_card):
        self.only_card = only_card
        self.card_number = None
        self.pin_number = None
        self.luhn_number = None

    # card_gen method generate a random number for card
    def card_gen(self):
        self.card_number = '400000' + ''.join(random.choice(string.digits) for _ in range(9))
        return self.card_number

    # pin_gen generates a 4 digits random pin
    def pin_gen(self):
        self.pin_number = ''.join(random.choice(string.digits) for _ in range(4))
        return self.pin_number

    # luhn algorithm to validate card numbers
    def luhn_checker(self):
        result = 0
        mod = 0
        self.luhn_number = self.card_gen()
        luhn_list = [int(i) for i in self.luhn_number]
        # Multiply by 2 every odd digits
        for k in range(len(luhn_list)):
            if k % 2 == 0:
                luhn_list[k] = luhn_list[k] * 2
        # if digit length is greater than 9, subtract '9' from it
        for kk in range(len(luhn_list)):
            if luhn_list[kk] > 9:
                luhn_list[kk] = luhn_list[kk] - 9
        # add all digits
        result = sum(luhn_list)
        print(result)
        # calculate mod for the sum result
        mod = result % 10
        if mod != 0:
            mod1 = 10 - mod
            self.luhn_number = self.luhn_number + str(mod1)
        else:
            self.luhn_number = self.luhn_number + str(0)
        return self.luhn_number
    # check if card is valid or not
    def validity_checker(self):
        only_list = [int(i) for i in self.only_card]
        for k in range(len(only_list)):
            if k % 2 == 0:
                only_list[k] = only_list[k] * 2

            for kk in range(len(only_list)):
                if only_list[kk] > 9:
                    only_list[kk] = only_list[kk] - 9

        only_sum = sum(only_list)
        if only_sum % 10 == 0:
            return True
        else:
            return False


# sqlite database starts here
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
# create a card table
cur.execute('''CREATE TABLE IF NOT EXISTS card 
                        (id INTEGER PRIMARY KEY,  
                        number TEXT,
                        pin TEXT,
                        balance INTEGER DEFAULT 0)''')
# ''id INTEGER PRIMARY  ''' it will add id as 1,2,3 automatically
# balance column is added with a default value zero automatically


# starting point of program...........
v2 = None
v1 = None
id = 0
while v1 != 0:
    print(" ")
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    v1 = int(input('>'))
    if v1 == 1:
        print(" ")
        print("Your card has been created")
        dummy = None
        number = System(dummy)  # calling the class with object "number"
        c_number = number.luhn_checker()
        print("Your card Number:")
        print(c_number)
        p_number = number.pin_gen()  # calling method pin_gen to generate a 4 digits random number
        print("Your card PIN: ")
        print(p_number)
        # ADD CARD NUMBERS INTO TABLE NAMED CARD
        cur.execute('INSERT INTO card (number, pin) VALUES (?,?)', (c_number, p_number,))
        conn.commit()
        print(" ")

    if v1 == 2:
        print(" ")
        cur.execute('''SELECT * FROM card''')
        db_data = cur.fetchall()
        leng = len(db_data)
        print(db_data)
        print("Enter your card number")
        card_number = input(">")
        print("Enter your PIN: ")
        pin_number = input(">")

        # NOW COMPARE THE CARD NUMBER AND PIN IN THE DATABASE TO VALIDATE
        for kk in range(leng):
            if card_number in db_data[kk] and pin_number in db_data[kk]:
                print(" ")
                print("You have successfully logged in!")
                print(card_number)
                print(" ")
                while v2 != 0:
                    print(" ")
                    print("1. Balance")
                    print("2. Add income")
                    print("3. Do transfer")
                    print("4. Close account")
                    print("5. Log out")
                    print("0. Exit")
                    v2 = int(input(">"))
                    print(kk)
                    if v2 == 1:
                        cur.execute('''SELECT * FROM card''')
                        balance_db = cur.fetchall()
                        for bal in range(len(balance_db)):
                            if card_number in balance_db[bal]:
                                print(" ")
                                print("Balance: {}".format(balance_db[bal][-1]))
                    if v2 == 2:
                        print("Enter income:")
                        income = int(input(">"))
                        cur.execute("SELECT balance FROM card WHERE number = ?;", (card_number,))
                        balance = cur.fetchone()
                        # add the income values in balance column of card database
                        # query = "UPDATE card SET balance = ? WHERE number = ?;"
                        # data = (income, card_number)
                        income = income + balance[0]
                        cur.execute("UPDATE card SET balance = ? WHERE number = ?;", (income, card_number))
                        conn.commit()
                        print("Income was added!")

                    if v2 == 3:
                        print('Transfer')
                        print('Enter card number:')
                        transfer_card_no = input('>')
                        # CHECK IF SENDER AND TRANSFER ACCOUNT ARE SAME
                        if transfer_card_no == card_number:
                            print("You can't transfer money to the same account!")
                        else:
                            cur.execute("SELECT * FROM card")
                            sender_check_card = cur.fetchall()
                            # HERE USING LUHN ALGORITHM CARD IS CHECKED IF ITS VALID OR NOT
                            follow_luhn = System(transfer_card_no)
                            luhn_check = follow_luhn.validity_checker()
                            if luhn_check:
                                # IF CARD IS VALID THAN WE CHECK IF CARD IS IN DATABASE
                                for val in range(len(sender_check_card)):
                                    if transfer_card_no not in sender_check_card[val][1] and val == len(
                                            sender_check_card) - 1:
                                        print("Such a card does not exist.")
                                    elif transfer_card_no in sender_check_card[val][1]:
                                        print("Enter how much money you want to transfer:")
                                        transfer_money = int(input(">"))
                                        transfer_money1 = transfer_money
                                        cur.execute("SELECT balance FROM card WHERE number = ?;", (card_number,))
                                        sender_balance = cur.fetchone()
                                        if sender_balance[0] >= transfer_money:
                                            print(sender_check_card[val][-1])
                                            # update balance (add the money into account)
                                            cur.execute('''SELECT balance FROM card WHERE number = ?;''',
                                                        (transfer_card_no,))
                                            transfer_account_balance = cur.fetchone()
                                            transfer_money = transfer_money + transfer_account_balance[0]
                                            cur.execute("UPDATE card SET balance = ? WHERE number = ?;",
                                                        (transfer_money, transfer_card_no))
                                            # deduct balance from sending account
                                            cur.execute('''SELECT balance FROM card WHERE number = ?;''',
                                                        (card_number,))
                                            sender_account_balance = cur.fetchone()
                                            transfer_money1 = -(transfer_money1 - sender_account_balance[0])
                                            cur.execute("UPDATE card SET balance = ? WHERE number = ?;",
                                                        (transfer_money1, card_number))
                                            conn.commit()
                                            print("Success!")
                                            break
                                        else:
                                            print("Not enough money!")
                                            break
                            else:
                                print("Probably you made a mistake in the card number. Please try again!")

                    if v2 == 4:
                        cur.execute("DELETE FROM card WHERE number = ?;", (card_number,))
                        conn.commit()
                        print('The account has been closed!')
                        print(" ")

                    if v2 == 5:
                        print(" ")
                        print("You have successfully logged out!")
                        break
                    if v2 == 0:
                        print(" ")
                        print('Bye!')
                        exit()
            elif card_number not in db_data[kk]:
                pass
                if kk == leng - 1:
                    print("Wrong card number or PIN!")
                    print("       ")
            else:
                print("Wrong card number or PIN!")
                print("       ")
                break
    if v1 == 0:
        print(" ")
        print('Bye!')
conn.close()
