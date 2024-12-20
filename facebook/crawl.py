
from facebook.type import types,removeString,removeDyamic,selectDyamic,removeComment
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from time import sleep
import json
from helpers.modal import closeModal
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sql.posts import Post
from sql.pages import Page
from sql.errors import Error
from sql.history_crawl_page_posts import HistoryCrawlPagePost
from sql.history import HistoryCrawlPage
from sql.accounts import Account
from sql.account_cookies import AccountCookies
from urllib.parse import urlparse, parse_qs
from sql.comment import Comment 

class Crawl:
    def __init__(self, browser, account):
        self.browser = browser
        self.account = account
        self.page_instance = Page()
        self.history_instance = HistoryCrawlPage()
        self.post_instance = Post()
        self.comment_instance = Comment()
        self.error_instance = Error()
        self.account_instance = Account()
        self.account_cookies = AccountCookies()
        self.history_crawl_page_post_instance = HistoryCrawlPagePost()

    
    def handle(self):
        while True:
            try:
                cookie = self.login() # Xử lý login
                self.updateStatusAcount(3) # Đang lấy
                self.crawl(cookie) # Bắt đầu quá trình crawl
            except Exception as e:
                print(f"Lỗi khi xử lý lấy dữ liệu!: {e}")
                self.updateStatusAcount(1)
                self.error_instance.insertContent(e)
                print("Thử lại sau 3 phút...")
                sleep(180)
          
    def crawl(self, cookie):
        while True:
            try:
                listCrawl = self.getListCrawl()
                for crawl in listCrawl:
                    try:
                        print(f"Chuyển hướng tới: {crawl['id']}")
                        link = crawl['post_fb_link']
                        self.updateStatusHistory(crawl['id'],2) # Đang lấy
                        self.browser.get(link)
                        self.crawlContentPost(crawl, cookie)
                        self.updateStatusHistory(crawl['id'],3) # Đã lấy
                    except Exception as e:
                        self.updateStatusHistory(crawl['id'],4) # Gặp lỗi
                        print(f"Lỗi khi xử lý lấy {crawl['id']}: {e}")
                        self.error_instance.insertContent(e)
            except Exception as e:
                print(f"Lỗi trong quá trình crawl: {e}")
                raise e
            
    def getListCrawl(self):
        retry_interval = 60
        while True:
            try:
                listCrawl = self.history_crawl_page_post_instance.get_list({
                    'status': 1,
                    'account_id': self.account["id"],
                    'sort': 'asc',
                })['data']
                if listCrawl: 
                    print(f"Lấy được bài viết cần lấy: {len(listCrawl)} trang.")
                    return listCrawl
                else:
                    print("Không có dữ liệu. Đợi 1 phút trước khi thử lại...")
            except Exception as e:
                print(f"Lỗi khi lấy danh sách trang: {e}")

            sleep(retry_interval)

    def crawlContentPost(self, crawl, cookie):
        data = {
            'account_id': cookie['account_id'],
            'cookie_id': cookie['id'],
            'post_id': crawl["post_fb_id"],
            'page_id': crawl['page_id'],
            'link_facebook': crawl['post_fb_link'],
            'media' : {
                'images': [],
                'videos': []
            },
            'up': 0,
        }
        dataComment = []
        sleep(5)
        
        print(f"Bắt đầu lấy dữ liệu bài viết: {crawl['post_fb_id']}")
        
        modal = None # Xử lý lấy ô bài viết
        for modalXPath in types['modal']:
            try:
                # Chờ cho modal xuất hiện
                modal = self.browser.find_element(By.XPATH, modalXPath)
                break
            except Exception as e:
                continue
        if not modal:
            print('Không lấy được thấy bài viết!')    
        else:
            aria_posinset = modal.get_attribute("aria-posinset")
            if aria_posinset is not None:
                closeModal(0, self.browser)
            else:
                closeModal(1, self.browser)
                
        try:
            content = modal.find_element(By.XPATH, types['content'])
            contentText = content.text
            for string in removeString:
                contentText = contentText.replace(string, '')
            data['content'] = contentText.strip()
        except:
            print(f'Bài viết k có content')
            data['content'] = ''
            pass

        # Lấy ảnh và video
        try:
            media = modal.find_element(By.XPATH,types['media'])
        except NoSuchElementException:
            media = modal
        
        try:
            images = media.find_elements(By.CSS_SELECTOR,'img')
            for img in images:
                src = img.get_attribute('src')
                if src and src.startswith('http') and "emoji.php" not in src:
                    data['media']['images'].append(img.get_attribute('src'))
                
            videos = media.find_elements(By.CSS_SELECTOR,'video')
            for video in videos:
                data['media']['videos'].append(video.get_attribute('src'))
        except:
            print(f'Bài viết k có ảnh hoặc video')
        
        # Lấy lượng like, chia sẻ
        try:
            like_share_element = modal.find_element(By.XPATH, types['dyamic'])
            listCount = like_share_element.text
            for string in removeDyamic:
                listCount = listCount.replace(string, '')

            listCount = listCount.split('\n')
            
            if listCount:
                data['like'] = listCount[1] if len(listCount) > 1 else 0
                for dyamic in listCount:
                    if selectDyamic['comment'] in dyamic:
                        data['comment'] = dyamic
                    if selectDyamic['share'] in dyamic:
                        data['share'] = dyamic
        except Exception as e:
            print(f"Không lấy được like, comment, share: {e}")

        sleep(2)
        # Lấy comment
        try:
            scroll = modal.find_element(By.XPATH,types['scroll'])
            self.browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll)
        except: 
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        
        try:
            comments = modal.find_elements(By.XPATH, types['comments'])
            print(f"Lấy được: {len(comments)} bình luận!")
            
            # Click vào các từ xem thêm
            for cm in comments:
                countRemoveImage = 0
                # Xóa ảnh trùng trong danh sách data['media']['images']
                try:
                    imgs_in_comment = cm.find_elements(By.CSS_SELECTOR, 'img')
                    for img in imgs_in_comment:
                        src = img.get_attribute('src')
                        if src in data['media']['images']:
                            data['media']['images'].remove(src)
                            countRemoveImage = countRemoveImage + 1
                except:
                    pass
                
                if countRemoveImage > 0:
                    print(f"Xoá được: {countRemoveImage} ảnh ở comment!")
                
                try:
                    xem_them = cm.find_element(By.XPATH, types['hasMore'])
                    if xem_them:
                        self.browser.execute_script("arguments[0].click();", xem_them)
                except:
                    pass
            countComment = 0
            for cm in comments:
                if countComment >= 10:
                    break
                textComment = ''
                link_comment = []
                try:
                    div_elements = cm.find_elements(By.XPATH, './div')[1]
                    div_2 = div_elements.find_elements(By.XPATH, './div')
                    
                    
                    if not div_2 or not div_2[0]: 
                        continue
                    textComment = div_2[0].text
                    
                    try:
                        if len(div_2) > 1:
                            a_tags = div_2[1].find_elements(By.XPATH, './/a') 
                            if not a_tags:
                                a_tags = div_2[0].find_elements(By.XPATH, './/a')  
                        elif len(div_2) > 0:
                            a_tags = div_2[0].find_elements(By.XPATH, './/a')
                        else:
                            a_tags = []
                        for a in a_tags:
                            try:
                                img_element = None
                                try:
                                    img_element = a.find_element(By.XPATH, 'preceding-sibling::img') 
                                except:
                                    pass
                                
                                if img_element:
                                    print("Thẻ <a> có thẻ <img> phía trước, không lấy href.")
                                else:
                                    href = a.get_attribute('href')
                                    if crawl['post_fb_id'] not in href and 'https://www.facebook.com' not in href:
                                        link_comment.append(href)
                            except Exception as e:
                                print(f"Lỗi khi lấy href: {e}")
                    except IndexError as ie:
                        print(f"Lỗi chỉ mục: {ie}")
                    except Exception as e:
                        print(f"Lỗi không xác định: {e}")
                        
                except:
                    countComment += 1
                    pass
                    
                for text in removeComment:
                    textComment = textComment.replace(text,'')

                textComment = textComment.strip()
                textArray = textComment.split('\n')

                if 'Top fan' in textComment:
                    user_name = textArray[1]
                    textContentComment = ' '.join(textArray[2:])
                else:
                    user_name = textArray[0]
                    textContentComment = ' '.join(textArray[1:])

                if user_name == '' or textContentComment == '':
                    continue

                countComment += 1
                dataComment.append({
                    'user_name': user_name,
                    'content': textContentComment,
                    'link_comment': link_comment,
                })
            print(f"=> Lưu được {len(dataComment)} bình luận!")
        except Exception as e:
            print(e)
            print("Không lấy được bình luận!")

        self.insertPostAndComment(data,dataComment, crawl)
        
    def insertPostAndComment(self, data, dataComment, crawl):
        # print(json.dumps(data, indent=4))
        # print(json.dumps(dataComment, indent=4))
        print("Đang lưu bài viết và bình luận vào database...")
        res = self.post_instance.insert_post({
            'post' : data,
            'comments': dataComment
        })
        print(f"Response: {res}")
        if res['post_id']:
            self.history_crawl_page_post_instance.update(crawl['id'],res['post_id'])
        else:
            self.updateStatusHistory(crawl['id'],4)

        print("=> Đã lưu thành công!")
        print("\n-----------------------------------------------------\n")


   
    # Copy
    def login(self):
        try:
            if not self.account['latest_cookie']:
                raise ValueError("Không có cookie để đăng nhập.")

            last_cookie = self.account['latest_cookie']    
            cookies = json.loads(last_cookie['cookies'])
            for cookie in cookies:
                self.browser.add_cookie(cookie)
            sleep(1)
            self.browser.get('https://facebook.com')
            sleep(1)
            
            try:
                self.browser.find_element(By.XPATH, types['form-logout'])
            except Exception as e:
                self.updateStatusAcountCookie(last_cookie['id'],1)
                raise ValueError("Cookie không đăng nhập được.")
            print(f"Login {self.account['name']} thành công")
            return last_cookie
        except Exception as e:
            print(f"Lỗi khi login với cookie: {e}")
            raise  # Ném lỗi ra ngoài để catch trong hàm handle()
    
    def updateStatusAcount(self,status):
        # 1: Lỗi cookie,
        # 2: Đang hoạt động,
        # 3: Đang lấy dữ liệu...,
        # 4: Đang đăng bài...
        self.account_instance.update_account(self.account['id'], {'status_login': status})
        
    def updateStatusAcountCookie(self,cookie_id, status):
        # 1: Chết cookie
        # 2: Cookie đang sống
        self.account_cookies.update(cookie_id,{'status': status})
        
    def updateStatusHistory(self, history_id, status):
        return self.history_crawl_page_post_instance.update(history_id, {'status': status})