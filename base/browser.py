from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import tempfile

class Browser:
    def __init__(self,account = 'hung'):
        self.profile_dir = tempfile.mkdtemp(prefix=f"account_{account}_")
        
    def start(self):
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={self.profile_dir}")
        # Cấu hình các tùy chọn cho Chrome
        chrome_options.add_argument(f"--user-data-dir={self.profile_dir}")
        chrome_options.add_argument("--disable-notifications")  # Tắt thông báo quyền cấp quyền (notifications)
        chrome_options.add_argument("--disable-geolocation")    # Tắt quyền truy cập vị trí
        chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Giả lập media stream
        chrome_options.add_argument("--disable-popup-blocking")  # Tắt chặn pop-up
        chrome_options.add_argument("--incognito") # Chạy ẩn dánh
        # chrome_options.add_argument("--headless")  # Chạy Chrome ở chế độ không giao diện
        # chrome_options.add_argument("--disable-gpu")  # Tắt GPU (thường cần thiết khi chạy headless trên một số hệ thống)
        # chrome_options.add_argument("--no-sandbox")  # Tắt sandbox (cần thiết trong môi trường như Docker)

        service = Service('chromedriver.exe') 
        browser = webdriver.Chrome(service=service,options=chrome_options)
        return browser