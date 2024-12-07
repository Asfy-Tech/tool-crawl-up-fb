from selenium import webdriver
import json
from facebook.type import types
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep
from facebook.crawl import Crawl
from sql.pages import Page
from sql.accounts import Account
from sql.errors import Error
from sql.account_cookies import AccountCookies
from sql.history import HistoryCrawlPage
from datetime import datetime
from selenium.webdriver.common.by import By

chrome_options = Options()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--incognito")  # Chạy ở chế độ ẩn danh (không lưu cache)
chrome_options.add_argument("--disable-application-cache")  # Vô hiệu hóa cache
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox") 
# chrome_options.add_argument("--disable-dev-shm-usage")

service = Service('chromedriver.exe') 
browser = webdriver.Chrome(service=service,options=chrome_options)

page_instance = Page()
account_instance = Account()
history_instance = HistoryCrawlPage()
account_cookies = AccountCookies()
error_instance = Error()

browser.get("https://facebook.com")

def getData():
    while True:  
        try:
            accounts = account_instance.get_accounts({'in[]': [5]})['data']
            for user in accounts:
                try:
                    print(f"Đăng nhập vào tài khoản: {user['name']}")
                    if not user['latest_cookie']:
                        account_instance.update_account(user['id'], {'status_login': 1}) # Chuyển trạng thái chết cookie
                        continue
                        
                    last_cookie = user['latest_cookie']
                    cookies = json.loads(last_cookie['cookies'])
                    account_instance.update_account(user['id'], {'status_login': 3}) # Chuyển trạng thái thành đang lấy dữ liệu
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
                        print(f"Lỗi khi set cookie: {str(e)}")
                    
                    try:
                        browser.find_element(By.XPATH, types['form-logout'])
                        print(f"=> Đăng nhập thành công!")
                        if last_cookie['status'] == 1: 
                            account_cookies.update(last_cookie['id'],{'status': 2}) # Chuyển trạng thái cookie
                        
                        listPages = page_instance.get_pages({
                            'type_page': 1,
                            'user_id': user["id"],
                            'order': 'updated_at',
                            'sort': 'asc',
                        })['data']
                        if not listPages:
                            print(f"Không lấy được page nào")
                            continue
                        
                        print(f"Lấy được: {len(listPages)} fanpage từ database")
                        for page in listPages:
                            resHis = history_instance.insert_history({'page_id': page['id'],'cookie_id': last_cookie['id'],'status': 1})
                            his = resHis['data']
                            link = page['link']
                            print(f"Chuyển hướng tới: {link}")
                            browser.get(link)
                            try:
                                crawl = Crawl(browser, page, his)
                                crawl.get()
                            except KeyboardInterrupt:
                                page_instance.update_time(page['id'])
                                if his:
                                    history_instance.update_history(his['id'], {
                                        'status': 2,
                                    })
                                print(f'Chương trình đã bị dừng!')
                                
                            page_instance.update_time(page['id'])
                            if his:
                                history_instance.update_history(his['id'], {
                                    'status': 2,
                                })
                            sleep(2)
                    except Exception as e:
                        print(f"=> Đăng nhập thất bại!")
                        error_instance.insertContent(e)
                        account_cookies.update(last_cookie['id'],{'status': 1})  # Chuyển trạng thái cookie
                        account_instance.update_account(user['id'], {'status_login': 1})  # Chuyển trạng thái chết cookie
                        print("=> Chờ 60s để xử lý tiếp...")
                        sleep(60)  # Tạm dừng trước khi tiếp tục kiểm tra lại
                    continue
                except KeyboardInterrupt:
                    account_instance.update_account(user['id'], {'status_login': 2})  # Lấy xong, chuyển thành đang hoạt động
                    print(f'Chương trình đã bị dừng!')
                account_instance.update_account(user['id'], {'status_login': 2})  # Lấy xong, chuyển thành đang hoạt động
                browser.execute_cdp_cmd("Network.clearBrowserCache", {}) # Xoá cache

            if not accounts:  # Nếu không có tài khoản nào, dừng vòng lặp tạm thời
                print("Không còn tài khoản nào để xử lý. Đợi 60 giây...")
                sleep(60)  # Tạm dừng trước khi tiếp tục kiểm tra lại
        except Exception as e:
            error_instance.insertContent(e)
            print(f"Lỗi không mong muốn xảy ra: {str(e)}")
            break;  # Thoát khỏi vòng lặp nếu gặp lỗi nghiêm trọng

getData()


browser.close() 
