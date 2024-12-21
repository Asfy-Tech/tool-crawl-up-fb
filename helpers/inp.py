def get_user_input():
    ids = input("Nhập danh sách ID (cách nhau bởi dấu phẩy): ")
    
    id_list = ids.split(',')
    id_list = [id.strip() for id in id_list] 
    
    return id_list

def show_confirm_continue(id_list):
    print("\nDanh sách ID bạn đã nhập:")
    for idx, user_id in enumerate(id_list, 1):
        print(f"{idx}. {user_id}")
    
    while True:
        continue_input = input("\nBạn có muốn tiếp tục (y/n)? ").lower()
        if continue_input == 'y':
            return True
        elif continue_input == 'n':
            return False
        else:
            print("Vui lòng nhập 'y' để tiếp tục hoặc 'n' để thoát.")
