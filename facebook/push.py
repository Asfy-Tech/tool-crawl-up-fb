from time import sleep
from sql.posts import Post
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from facebook.type import types,push
from sql.pagePosts import PagePosts
from sql.pages import Page
from helpers.modal import closeModal
from sql.errors import Error
import json
from helpers.image import copy_image_to_clipboard
import requests
from io import BytesIO
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui
from PIL import Image


class Push:
    def __init__(self,browser,listPageUps, last_cookie):
        self.browser = browser
        self.listPageUps = listPageUps
        self.last_cookie = last_cookie
        self.post_instance = Post()
        self.page_instance = Page()
        self.error_instance = Error()
        self.pagePosts_instance = PagePosts()
        
    def handle(self):
        for pageUp in self.listPageUps:
            link = pageUp['link']
            print(f"Chuyển hướng tới: {link}")
            self.browser.get(link)
            sleep(5)
            name = self.updateName(pageUp) #Cập nhật tên fanpage
            if name == '':
                continue
            print('Cập nhật tên page thành công, đợi 5s để tiếp tục....')
            sleep(5)
            self.showPage(name) # Show ra fanpage
            sleep(5)
            self.up(pageUp) # Thực hiện up dứ liệu
            print(f'Đã đăng xong page: {pageUp["id"]}, chờ 10s để tiếp tục...')
            sleep(10)
        sleep(5)
        self.browser.close()
                
    def updateName(self, pageUp):
        name = ''
        try:
            name_pages = self.browser.find_elements(By.XPATH, '//h1')
            name_page = name_pages[-1]
            self.page_instance.update_page(pageUp['id'],{'name': name_page.text.strip()})
            name  = name_page.text.strip()
        except: 
            print('-> Không tìm thấy tên trang!')
        return name
        
    def showPage(self, name):
        print('-> Mở popup thông tin cá nhân!')
        profile_button = self.browser.find_element(By.XPATH, push['openProfile'])
        profile_button.click()
        sleep(3)
            
        try:
            switchPage = self.browser.find_element(By.XPATH, push['switchPage'](name))
            switchPage.click()
        except Exception as e:
            print("-> Không tìm thấy nút chuyển hướng tới trang quản trị!")
        
        sleep(3)
                
    def up(self, listUp):
        for up in listUp['list_up']:
            self.pagePosts_instance.update_data(up['id'],{'status': 3, 'cookie_id': self.last_cookie['id']}) #Cập nhật trạng thái đang thực thi
            self.browser.get(listUp['link'])
            sleep(5)
            self.push(listUp,up)
            sleep(5)
        sleep(10)
        
    def push(self,page, up):
        post_id = up['post_id']
        try:
            post = self.post_instance.find_post(post_id) #Tìm thông tin bài viết
            # Check bài viết
            if not post['id']:
                print(f'Không tìm thầy bài viết có id {post_id} trong csdl') # Không tìm thấy bài viết
                self.pagePosts_instance.update_data(up['id'],{'status': 4}) #Cập nhật trạng thái đang thực thi
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
                self.pagePosts_instance.update_data(up['id'],{'status': 4}) # Cập nhật trạng thái đã xảy ra lỗi
                print("Không tìm thấy nút tạo bài viết!")
                return
            
            try:
                createPost.click()
            except:
                self.pagePosts_instance.update_data(up['id'],{'status': 4}) # Cập nhật trạng thái đã xảy ra lỗi
                print("Không thể click nút bài viết!")
                return
            
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
            sleep(10)
            try:
                closeModal(1,self.browser)
            except:
                pass
            sleep(10)
            self.afterUp(page,up) # Lấy link bài viết vừa đăng
            sleep(3)
            print('\n--------- Đăng bài thành công ---------\n')
        except Exception as e:
            self.error_instance.insertContent(e)
            self.pagePosts_instance.update_data(up['id'],{'status': 4}) # 4 Cập nhật trạng thái lỗi khi đăng
            print(f'Lỗi khi đăng bài viết: {e}')
        except KeyboardInterrupt:
            self.pagePosts_instance.update_data(up['id'],{'status': 4})  # 4 Cập nhật trạng thái lỗi khi đăng
            print(f'Chương trình đã bị dừng!')
    
    def afterUp(self,page, up):
        self.browser.get(page['link'])
        sleep(2)
        pageLinkPost = f"{page['link']}/posts/"
        pageLinkStory = "https://www.facebook.com/permalink.php"
        link_up = ''
        try:
            # Chờ modal xuất hiện
            modal = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@aria-posinset="1"]'))
            )
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
        except Exception as e:
            self.error_instance.insertContent(e)
            print(f"Không tìm thấy bài viết vừa đăng! {e}")
        self.pagePosts_instance.update_data(up['id'],{'status': 2,'link_up': link_up}) # Cập nhật trạng thái đã đăng
        sleep(5)
        self.browser.get('https://facebook.com')
        sleep(2)
        
    