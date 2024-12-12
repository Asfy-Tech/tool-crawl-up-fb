from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from time import sleep
from facebook.type import types,push
from facebook.push import Push
from selenium.webdriver.common.by import By
import json
from sql.pages import Page
from sql.accounts import Account
from sql.errors import Error
from sql.pagePosts import PagePosts

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--incognito")  # Chạy ở chế độ ẩn danh (không lưu cache)
chrome_options.add_argument("--disable-application-cache")  # Vô hiệu hóa cache
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox") 
# chrome_options.add_argument("--disable-dev-shm-usage")

service = Service('chromedriver.exe')


page_instance = Page()
account_instance = Account()
error_instance = Error()
pagePosts_instance = PagePosts()

def getData():
    while True:  
        try:
            accounts = account_instance.get_accounts({'in[]': [11]})['data'] # Lấy ra danh sách tài khoản từ database
            for user in accounts: # Lặp qua danh sách tài khoản
                listPageUps = []
                try:
                    listPages = page_instance.get_pages({
                        'type_page': 2,
                        'user_id': user["id"],
                        'order': 'updated_at',
                        'sort': 'asc',
                    })['data'] # Lấy ra danh sách page thuộc tài khoản đó
                    if not listPages:
                        print(f"Tài khoản {user['name']} không quản lý page nào") # Tại khoản k quản lý page nào => next
                        continue
                    
                    print(f"Lấy được: {len(listPages)} fanpage từ database")
                    for page in listPages: # Lặp qua danh sách fanpage khoản lấy được
                        listUp = pagePosts_instance.get_list({
                            'page_id': page['id'],
                            'status': 1,
                            'show_all': True,
                        })['data'] # Lấy danh sách page cần đăng của tài khoản đó
                        if len(listUp) <= 0:
                            print(f"=>Page {page['name']} không có bài nào cần đăng") # Page nào k có bài cần đăng thì next
                            continue
                        
                        print(f"=>Page {page['name']} có {len(listUp)} bài cần đăng")
                        pageUp = page
                        pageUp['list_up'] = listUp
                        listPageUps.append(pageUp)
                        page_instance.update_time(page['id'])
                        sleep(1)
                    account_instance.update_account(user['id'], {'status_login': 2})
                except KeyboardInterrupt:
                    account_instance.update_account(user['id'], {'status_login': 2})
                    print(f'Chương trình đã bị dừng!')
                    
                if len(listPageUps) <= 0:
                    print(f"Tài khoản: {user['name']} không có bài viết nào cần đăng!")    
                    sleep(3)
                    continue
            
                print(f"Lấy được: {len(listPageUps)} bài")
                sleep(1)
                print(f"Đăng nhập vào tài khoản: {user['name']}")
                if not user['latest_cookie']:
                    account_instance.update_account(user['id'], {'status_login': 1}) # Chuyển trạng thái chết cookie
                    continue
                    
                browser = webdriver.Chrome(service=service, options=chrome_options) # Mở trình duyệt
                browser.get("https://facebook.com") # Mở facebook   
                
                
                last_cookie = user['latest_cookie']
                cookies = json.loads(last_cookie['cookies'])
                account_instance.update_account(user['id'], {'status_login': 4}) # Chuyển trạng thái thành đang đăng bài
                try:
                    # Thêm từng cookie vào trình duyệt
                    for cookie in cookies:
                        browser.add_cookie(cookie)
                    sleep(1)
                    browser.get('https://facebook.com')
                    sleep(1)
                except Exception as e: 
                    error_instance.insertContent(e)
                    account_instance.update_account(user['id'], {'status_login': 1})  # Chuyển trạng thái chết cookie
                    browser.close()
                    print(f"Lỗi khi set cookie: {str(e)}")
                
                try:
                    browser.find_element(By.XPATH, types['form-logout'])
                    print(f"=> Đăng nhập thành công!, Đang xử lý đăng bài...")
                    push_instance = Push(browser, listPageUps, last_cookie)
                    push_instance.handle()
                    account_instance.update_account(user['id'], {'status_login': 2})  # Chuyển trạng thái chết cookie
                except Exception as e:
                    error_instance.insertContent(e)
                    print(f"=> Đăng nhập thất bại!")
                    account_instance.update_account(user['id'], {'status_login': 1})  # Chuyển trạng thái chết cookie
                    browser.close()
                    print("=> Chờ 60s để xử lý tiếp...")
                    sleep(60)  # Tạm dừng trước khi tiếp tục kiểm tra lại
                    continue  
            
                print(f'Đã duyệt xong tài khoản {user["name"]}, chờ 60s để tiếp tục...')
                sleep(60)     
                
            print('Đã duyệt qua danh sách tài khoản, chờ 10 phút để tiếp tục...')
            sleep(600)
        except Exception as e:
            error_instance.insertContent(e)
            print(f"Lỗi không mong muốn xảy ra: {str(e)}")
            break
getData()
