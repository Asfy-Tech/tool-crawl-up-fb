import signal
import multiprocessing
import os
import shutil
from selenium.common.exceptions import WebDriverException
from accounts import idAccounts
from base.browser import Browser
from facebook.crawl import Crawl
from facebook.crawlid import CrawlId
from sql.accounts import Account
from helpers.inp import get_user_input

account_instance = Account()
processes = []  # Lưu danh sách các tiến trình


def terminate_processes():
    """
    Hàm để dừng tất cả các tiến trình con đang chạy.
    """
    for process in processes:
        if process.is_alive():
            process.terminate()
            process.join()
    print("Tất cả tiến trình con đã được dừng.")


def signal_handler(sig, frame):
    """
    Xử lý tín hiệu Ctrl+C.
    """
    print("\nNhận tín hiệu Ctrl+C. Đang dừng...")
    terminate_processes()
    exit(0)


def process_crawl(account):
    """
    Hàm xử lý Crawl trong một tiến trình riêng.
    """
    browser = None
    browserStart = None
    try:
        print(f"Bắt đầu Crawl cho tài khoản: {account['name']}")
        browserStart = Browser(str(account['id']) + "_crawl")
        browser = browserStart.start()
        browser.get("https://facebook.com")
        crawl = Crawl(browser, account)
        crawl.handle()
    except Exception as e:
        print(f"Lỗi trong Crawl: {e}")
    finally:
        if browser:
            browser.quit()
        if browserStart and os.path.exists(browserStart.profile_dir):
            shutil.rmtree(browserStart.profile_dir)


def process_crawlId(account):
    """
    Hàm xử lý CrawlId trong một tiến trình riêng.
    """
    browser = None
    browserStart = None
    try:
        print(f"Bắt đầu CrawlId cho tài khoản: {account['name']}")
        browserStart = Browser(str(account['id']) + "_crawlId")
        browser = browserStart.start()
        browser.get("https://facebook.com")
        crawlId = CrawlId(browser, account)
        crawlId.handle()
    except Exception as e:
        print(f"Lỗi trong CrawlId: {e}")
    finally:
        if browser:
            browser.quit()
        if browserStart and os.path.exists(browserStart.profile_dir):
            shutil.rmtree(browserStart.profile_dir)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Đăng ký tín hiệu Ctrl+C
    try:
        id_list = get_user_input()
        accounts = account_instance.get_accounts({'in[]': id_list})['data']

        if not accounts:
            print("Không còn tài khoản nào để xử lý.")
        else:
            for account in accounts:
                # Tạo tiến trình xử lý Crawl
                crawl_process = multiprocessing.Process(target=process_crawl, args=(account,))
                crawlId_process = multiprocessing.Process(target=process_crawlId, args=(account,))

                processes.extend([crawl_process, crawlId_process])  # Thêm tiến trình vào danh sách

                crawl_process.start()
                crawlId_process.start()

            for process in processes:
                process.join()

            print("Tất cả các tài khoản đã được xử lý.")
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
    finally:
        terminate_processes()
