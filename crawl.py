from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from multiprocessing import Process
import os
from selenium.common.exceptions import WebDriverException
from accounts import idAccounts
from base.browser import Browser
from sql.accounts import Account
from time import sleep
import tempfile
import shutil
from facebook.crawl import Crawl


account_instance = Account()

def process_account(account):
    """
    Hàm xử lý một tài khoản trong một tiến trình riêng.
    """
    browser = None
    try:
        print(f"Bắt đầu xử lý tài khoản: {account['name']}")
        browserStart = Browser(account['id'])
        browser = browserStart.start()
        
        browser.get("https://facebook.com")
        
        crawlId = Crawl(browser, account)
        crawlId.handle()

    except Exception as e:
        print(f"Lỗi xảy ra khi xử lý tài khoản {account['name']}: {str(e)}")
    except WebDriverException as e:
        print(f"Lỗi khi khởi tạo trình duyệt: {e}")
    finally:
        if browser:
            browser.quit()
        if os.path.exists(browserStart.profile_dir):
            shutil.rmtree(browserStart.profile_dir)


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
