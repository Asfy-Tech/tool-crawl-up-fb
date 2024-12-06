from time import sleep
from sql.posts import Post
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from facebook.type import types,push
from sql.pagePosts import PagePosts
import json
from helpers.image import copy_image_to_clipboard
import requests
from io import BytesIO
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui
from PIL import Image


class Push:
    def __init__(self,browser,page):
        self.browser = browser
        self.page = page
        self.post_instance = Post()
        self.pagePosts_instance = PagePosts()
        
    def up(self, up):
        post_id = up['post_id']
        try:
            self.pagePosts_instance.update_data(up['id'],{'status': 3})
            post = self.post_instance.find_post(post_id)
            
            # Check bài viết
            if not post['id']:
                print(f'Không tìm thầy bài viết có id {post_id} trong csdl')
                return
            
            print('==> Bắt đầu đăng bài')
            # Check nút button
            createPost = None
            for create in push['createPost']:
                try:
                    createPost = self.browser.find_element(By.XPATH,f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{create}')]")
                    break
                except:
                    continue
                
            if not createPost:
                self.pagePosts_instance.update_data(up['id'],{'status': 4})
                print("Không tìm thấy nút tạo bài viết!")
                return
            
            createPost.click()
            
            sleep(1)
            input_element = self.browser.switch_to.active_element
            print('- Gán nội dung bài viết!')
            input_element.send_keys(post['content'])
            media = post['media']
            images = media['images']

            sleep(1)
            
            print('- Copy và dán hình ảnh')
            for src in images:
                
                sleep(1)
                # Copy hình ảnh vào clipboard
                copy_image_to_clipboard(src)
                sleep(2)
                
                input_element.send_keys(Keys.CONTROL, 'v')
                sleep(2)
            sleep(5)
            
            print('Đăng bài')
            parent_form = input_element.find_element(By.XPATH, "./ancestor::form")
            parent_form.submit()
            try:
                wait = WebDriverWait(self.browser, 10)
                closeModel = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@aria-label="Đóng"]')))
                closeModel.click()
            except: 
                pass
            sleep(10)
            self.afterUp(up) # Lấy link bài viết vừa đăng
            sleep(2)
            print('\n--------- Đăng bài thành công ---------\n')
        except Exception as e:
            self.pagePosts_instance.update_data(up['id'],{'status': 4}) # 4 mới đúng
            print(f'Lỗi khi đăng bài viết: {e}')
        except KeyboardInterrupt:
            self.pagePosts_instance.update_data(up['id'],{'status': 1})
            print(f'Chương trình đã bị dừng!')
    
    def afterUp(self, up):
        
        self.browser.get(self.page['link'])
        
        sleep(2)
        
        pageLinkPost = f"{self.page['link']}/posts/"
        pageLinkStory = "https://www.facebook.com/permalink.php"
        
        try:
            # Chờ modal xuất hiện
            modal = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@aria-posinset="1"]'))
            )
            
            link_up = ''
            actions = ActionChains(self.browser)
            
            # Chờ các liên kết bên trong modal
            links = WebDriverWait(self.browser, 10).until(
                lambda browser: modal.find_elements(By.XPATH, ".//a")
            )
            
            for link in links:
                # Kiểm tra nếu phần tử có kích thước hiển thị
                if link.size['width'] > 0 and link.size['height'] > 0:
                    try:
                        # Hover vào phần tử
                        actions.move_to_element(link).perform()
                        sleep(0.5)  # Đợi một chút để URL được cập nhật
                        # Lấy URL thật
                        href = link.get_attribute('href')
                        if href:  # Chỉ thêm nếu href không rỗng
                            if any(substring in href for substring in [pageLinkPost, pageLinkStory]):
                                link_up = href
                                break
                                
                    except Exception as hover_error:
                        print(f"Lỗi khi hover vào liên kết: {hover_error}")
            
            self.pagePosts_instance.update_data(up['id'], {'link_up': link_up})
        except Exception as e:
            print(f"Không tìm thấy bài viết vừa đăng! {e}")
        self.pagePosts_instance.update_data(up['id'],{'status': 2}) # Cập nhật trạng thái đã đăng
        