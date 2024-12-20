from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from multiprocessing import Process
import os
from selenium.common.exceptions import WebDriverException
from accounts import idAccounts
from sql.accounts import Account
from time import sleep
import tempfile
import shutil
from facebook.crawlid import CrawlId


account_instance = Account()

def process_account(account):
    """
    Hàm xử lý một tài khoản trong một tiến trình riêng.
    """
    browser = None
    try:
        print(f"Bắt đầu xử lý tài khoản: {account['name']}")
        # Tạo cấu hình trình duyệt với hồ sơ người dùng riêng
        profile_dir = tempfile.mkdtemp(prefix=f"account_{account['id']}_")
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
        # Cấu hình các tùy chọn cho Chrome
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
        chrome_options.add_argument("--disable-notifications")  # Tắt thông báo quyền cấp quyền (notifications)
        chrome_options.add_argument("--disable-geolocation")    # Tắt quyền truy cập vị trí
        chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Giả lập media stream
        chrome_options.add_argument("--disable-popup-blocking")  # Tắt chặn pop-up
        # chrome_options.add_argument("--headless")  # Chạy Chrome ở chế độ không giao diện
        # chrome_options.add_argument("--disable-gpu")  # Tắt GPU (thường cần thiết khi chạy headless trên một số hệ thống)
        # chrome_options.add_argument("--no-sandbox")  # Tắt sandbox (cần thiết trong môi trường như Docker)

        service = Service('chromedriver.exe') 
        browser = webdriver.Chrome(service=service,options=chrome_options)
        
        browser.get("https://facebook.com")
        
        crawlId = CrawlId(browser, account)
        crawlId.handle()

    except Exception as e:
        print(f"Lỗi xảy ra khi xử lý tài khoản {account['name']}: {str(e)}")
    except WebDriverException as e:
        print(f"Lỗi khi khởi tạo trình duyệt: {e}")
    finally:
        if browser:
            browser.quit()
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir)


if __name__ == "__main__":
    try:
        # Lấy danh sách tài khoản từ nguồn
        accounts = account_instance.get_accounts({'in[]': idAccounts['get']})['data']

        if not accounts:
            print("Không còn tài khoản nào để xử lý.")
        else:
            processes = []

            for account in accounts:
                # Tạo một tiến trình riêng cho mỗi tài khoản
                process = Process(target=process_account, args=(account,))
                processes.append(process)
                process.start()

            # Đợi tất cả tiến trình hoàn thành
            for process in processes:
                process.join()

            print("Tất cả các tài khoản đã được xử lý.")

    except Exception as e:
        print(f"Lỗi không mong muốn xảy ra: {str(e)}")
