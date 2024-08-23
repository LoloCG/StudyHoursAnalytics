import sys, os
import db_handler, hours_per_subject, main_menu

if __name__ == "__main__":
    print("\nRunning program")
    
    target_file_folder_dir = os.path.dirname(os.path.abspath(__file__)) 
    chosen_file = '3º FarmNutr TDL_Log.csv'
    db_handler.main(target_file_folder_dir, chosen_file)

    main_menu.run_main_menu()
