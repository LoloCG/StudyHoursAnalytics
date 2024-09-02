import db_handler
import subject_time_analysis as time_anal

option_list = [
    'Show hours per subject',
    'Show studied hours per week'
]

def main_menu_sequence():
    def show_and_select_main_menu(option_list):  
        print("\nMain Menu")
        for i, item in enumerate(option_list, 1):
            print(f"{i}. {item}")
        print(f"{len(option_list) + 1}. Exit")

        # Get user choice
        choice = input("Enter your choice: ")

        try:
            # Convert choice to integer
            choice = int(choice)

            # Check if choice is a valid option
            if 1 <= choice <= len(option_list):
                print(f"Selected option {choice} ({option_list[choice - 1]})")
                return choice
            elif choice == len(option_list) + 1:
                print("Selected Exit option.")
                return None
            else:
                print("Invalid choice, please enter again.\n")
        except ValueError:
            print("Invalid choice, please enter a number.\n")

    def menu_option_caller(option_num):
            if option_num == 1:
                menu_opt1()
            elif option_num == 2:
                menu_opt2()
            elif option_num == 3:
                print("Exiting the program.")
                return True
            else:
                print("Invalid choice, please enter again.\n")
                return False

    while True:
        choice = show_and_select_main_menu(option_list)
        if choice is None or menu_option_caller(choice):
            break

        print("Returning to main menu...\n")
    
def menu_opt1():
    print()
    df = db_handler.retrieve_main_table() 
    time_anal.show_total_hours_per_subject_per_perdiod(df)
    return

def menu_opt2():
    print()
    df = db_handler.retrieve_main_table()
    time_anal.show_weekly_hours_per_subject(df)
    return