import sys, os
import db_handler, main_menu

if __name__ == "__main__":
    print("\nRunning program")
    
    db_handler.main()

    main_menu.main_menu_sequence()

