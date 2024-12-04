from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from time import sleep
from facebook.type import types,push
from facebook.push import Push
from selenium.webdriver.common.by import By
import json
from sql.pages import Page
from sql.accounts import Account
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
pagePosts_instance = PagePosts()

def getData():
    while True:  
        try:
            accounts = account_instance.get_accounts({'in[]': [11]})['data']
            for user in accounts:
                try:
                    browser = webdriver.Chrome(service=service, options=chrome_options) # Mở trình duyệt
                    browser.get("https://facebook.com") # Mở facebook
                    
                    listPages = page_instance.get_pages({
                        'type_page': 2,
                        'user_id': user["id"],
                        'order': 'updated_at',
                        'sort': 'asc',
                    })['data']
                    if not listPages:
                        print(f"Tài khoản {user['name']} không quản lý page nào")
                        continue
                    
                    print(f"Lấy được: {len(listPages)} fanpage từ database")
                    for page in listPages:
                        listUp = pagePosts_instance.get_list({
                            'page_id': page['id'],
                            'status': 1,
                            'show_all': True,
                        })['data']
                        if len(listUp) <= 0:
                            print(f"=>Page {page['name']} không có bài nào cần đăng")
                            continue
                        
                        print(f"=>Page {page['name']} có {len(listUp)} bài cần đăng")
                        
                        print(f"Đăng nhập vào tài khoản: {user['name']}")
                        cookies = json.loads(user['cookie'])
                        account_instance.update_account(user['id'], {'status_login': 4}) # Chuyển trạng thái thành đang lấy dữ liệu
                        try:
                            # Thêm từng cookie vào trình duyệt
                            for cookie in cookies:
                                browser.add_cookie(cookie)
                            sleep(1)
                            browser.get('https://facebook.com')
                            sleep(1)
                        except Exception as e: 
                            account_instance.update_account(user['id'], {'status_login': 1})  # Chuyển trạng thái chết cookie
                            print(f"Lỗi khi set cookie: {str(e)}")
                            browser.close()
                            continue                        
                        try:
                            browser.find_element(By.XPATH, types['form-logout'])
                            print(f"=> Đăng nhập thành công!")
                            
                            link = page['link']
                            print(f"Chuyển hướng tới: {link}")
                            browser.get(link)
                            
                            try:
                                name_page = browser.find_element(By.XPATH, '//h1')
                                page_instance.update_page(page['id'],{'name': name_page.text})
                            except: 
                                print('-> Không tìm thấy tên trang!')
                                continue
                            
                            sleep(1)
                            
                            print('-> Mở popup thông tin cá nhân!')
                            profile_button = browser.find_element(By.XPATH, push['openProfile'])
                            profile_button.click()
                            
                            sleep(1)
                            
                            try:
                                switchPage = browser.find_element(By.XPATH, push['switchPage'](name_page.text.strip()))
                                switchPage.click()
                            except Exception as e:
                                print("-> Không tìm thấy nút chuyển hướng tới trang quản trị!")
                            
                            sleep(1)
                            if not listUp:
                                print(f"Page này không có bài viết nào cần đăng!")
                                continue
                            
                            for up in listUp:
                                push_instance = Push(browser, page)
                                push_instance.up(up)
                                sleep(2)   
                            sleep(10)
                        except Exception as e:
                            print(f"=> Đăng nhập thất bại!")
                            account_instance.update_account(user['id'], {'status_login': 1})  # Chuyển trạng thái chết cookie
                            print("=> Chờ 60s để xử lý tiếp...")
                            browser.close()
                            sleep(60)  # Tạm dừng trước khi tiếp tục kiểm tra lại
                            continue
                    browser.close()
                except KeyboardInterrupt:
                    account_instance.update_account(user['id'], {'status_login': 2})
                    print(f'Chương trình đã bị dừng!')
                    browser.close()
                account_instance.update_account(user['id'], {'status_login': 2})
                # browser.execute_cdp_cmd("Network.clearBrowserCache", {}) # Xoá cache
            print('Đã duyệt qua danh sách tài khoản, chờ 5 phút để tiếp tục...')
            sleep(300)
        except Exception as e:
            print(f"Lỗi không mong muốn xảy ra: {str(e)}")
            break
getData()

