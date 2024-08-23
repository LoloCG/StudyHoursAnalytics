import db_handler, hours_per_subject
def run_main_menu():
    option_list = [
        'Show hours per subject',
        'Show studied hours per week'
    ]

    while True:
        # TODO: make it into a dynamic loop...
        print("\nMain Menu")
        print("1.", option_list[0])
        print("2.", option_list[1])
        print("3. Exit")

        choice = input("Enter your choice: ")
        
        if choice == '1':
            menu_opt1()
        elif choice == '2':
            menu_opt2()
        elif choice == '3':
            print("Exiting the program.")
            return
        else:
            print("Invalid choice, please enter again.\n")

def menu_opt1():
    print()
    df = db_handler.retrieve_main_table() # TODO: make it so that dataframe does not need to be passed around so much, and instead is obtained directly from the database
    hours_per_subject.main(df)
    print("Returning to main menu...\n")

def menu_opt2():
    print()
    df = db_handler.retrieve_main_table()
    hours_per_subject.main2(df)
    print("Returning to main menu...\n")