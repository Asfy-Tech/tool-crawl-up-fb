
from selenium.webdriver.common.by import By
from sql.pages import Page
from sql.errors import Error
from facebook.type import types,push
from base.browser import Browser
from multiprocessing import Process
from sql.account_cookies import AccountCookies
from sql.accounts import Account
from sql.history_crawl_page_posts import HistoryCrawlPagePost
import json
from selenium.webdriver.common.action_chains import ActionChains
from helpers.modal import closeModal
from facebook.helpers import login,updateStatusAcount,handleCrawlNewFeed
from urllib.parse import urlparse, parse_qs
from time import sleep

class CrawlId:
    def __init__(self, browser, account):
        self.browser = browser
        self.account = account
        self.page_instance = Page()
        self.error_instance = Error()
        self.account_cookies = AccountCookies()
        self.account_instance = Account()
        self.history_crawl_page_posts = HistoryCrawlPagePost()

    def handle(self):
        while True:
            try:
                account = self.account_instance.find(self.account['id'])
                if not account['id']:
                    raise ValueError('Không tìm thấy tài khoản')
                self.account = account
                # cookie = login(self.browser,self.account)
                cookie = account['latest_cookie']
                updateStatusAcount(self.account['id'],3) # Đang lấy
                if account['newfeed'] == 1:
                    print('Lấy bài viết new feed')
                    self.crawlNewFeed(account)                    
                else:
                    self.crawl(cookie) # Bắt đầu quá trình crawl
            except Exception as e:
                print(f"Lỗi khi xử lý lấy dữ liệu!: {e}")
                updateStatusAcount(self.account['id'],1)
                self.error_instance.insertContent(e)
                print("Thử lại sau 3 phút...")
                sleep(180)
          
    def crawl(self, cookie):
        while True:
            try:
                listPages = self.getListPage()
                for page in listPages:
                    try:
                        print(f"Chuyển hướng tới page: {page['name']}")
                        link = page['link']
                        self.browser.get(link)
                        self.crawlIdFanpage(page, cookie)
                        self.page_instance.update_time(page['id'])
                    except Exception as e:
                        print(f"Lỗi khi xử lý page {page['name']}: {e}")
                        self.error_instance.insertContent(e)
            except Exception as e:
                print(f"Lỗi trong quá trình crawl: {e}")
                raise e
        
    def crawlIdFanpage(self, page, cookie):
        closeModal(0, self.browser)
        self.browser.execute_script("document.body.style.zoom='0.2';")
        sleep(10)
        name = self.updateInfoFanpage(page)
        
        pageLinkPost = f"{page['link']}/posts/"
        pageLinkStory = "https://www.facebook.com/permalink.php"
        
        listPosts = self.browser.find_elements(By.XPATH, types['list_posts']) # Lấy danh sách bài viết
        print(f"Lấy được {len(listPosts)} bài viết")
        
        post_links = []
        try:
            actions = ActionChains(self.browser)
            for p in listPosts:
                links = p.find_elements(By.XPATH, ".//a")
                for link in links:
                    if link.size['width'] > 0 and link.size['height'] > 0:
                        actions.move_to_element(link).perform() # Hover vào danh sách thẻ a
                        href = link.get_attribute('href')
                        if any(substring in href for substring in [pageLinkPost, pageLinkStory]):
                            post_links.append(href) # Lấy những href cần thiết
        except:
            pass
        
        if(len(post_links) == 0):
            print('Không lấy được đường dẫn bài viết nào!')
            return
        
        post_data = []
        for link in post_links:
            if pageLinkPost in link:
                post_id = link.replace(pageLinkPost, '').split('?')[0]
                if post_id not in [data['id'] for data in post_data]:
                    post_data.append({'id': post_id, 'link': link})
            elif pageLinkStory in link:
                parsed_url = urlparse(link)
                query_params = parse_qs(parsed_url.query)
                story_fbid = query_params.get('story_fbid', [None])[0]
                if story_fbid and story_fbid not in [data['id'] for data in post_data]:
                    post_data.append({'id': story_fbid, 'link': link})
        if post_data:
            print(json.dumps(post_data,indent=4))
            for post in post_data:
                data = {
                    'post_fb_id': post['id'],
                    'post_fb_link': post['link'],
                    'status': 1,
                    'page_id': page['id'],
                    'cookie_id': cookie['id'],
                    'account_id': cookie['account_id'],
                }
                self.history_crawl_page_posts.insert(data)
                self.account_cookies.updateCount(cookie['id'],'counts')

    def updateInfoFanpage(self, page):
        dataUpdatePage = {}
        try:
            name_pages = self.browser.find_elements(By.XPATH, '//h1')
            name_page = name_pages[-1]
            name = name_page.text.strip()
            dataUpdatePage['name'] = name
            
            try:
                verified_elements = name_page.find_elements(By.XPATH, types['verify_account'])
                # Kiểm tra tích xanh
                if verified_elements:
                    dataUpdatePage['verified'] = 1
                else:
                    dataUpdatePage['verified'] = 0
            except:
                dataUpdatePage['verified'] = 0
                pass
            
            try: # Lấy lượt like
                likes = self.browser.find_element(By.CSS_SELECTOR, types['friends_likes'])
                dataUpdatePage['like_counts'] = likes.text
            except:
                pass
            
            try: # Lấy follows
                follows = self.browser.find_element(By.CSS_SELECTOR, types['followers'])
                dataUpdatePage['follow_counts'] = follows.text
            except:
                pass
            
            try: # Lấy followning
                following = self.browser.find_element(By.CSS_SELECTOR, types['following'])
                dataUpdatePage['following_counts'] = following.text
            except:
                pass
            
            self.page_instance.update_page(page['id'],dataUpdatePage)
            return name
        except Exception as e:
            raise ValueError('Không tìm thấy tên fanpage!')
        
    def getListPage(self):
        retry_interval = 5 * 60  # Thời gian chờ giữa các lần thử (5p)
        while True:
            try:
                listPages = self.page_instance.get_pages({
                    'type_page': 1,
                    'user_id': self.account["id"],
                    'order': 'updated_at',
                    'sort': 'asc',
                })['data']

                if listPages: 
                    print(f"Lấy được danh sách trang: {len(listPages)} trang.")
                    return listPages
                else:
                    print("Không có dữ liệu. Đợi 5 phút trước khi thử lại...")
            except Exception as e:
                print(f"Lỗi khi lấy danh sách trang: {e}")

            sleep(retry_interval)

    def crawlNewFeed(self,account):
        print(f"Chuyển hướng tới trang chủ!")
        self.browser.get('https://facebook.com')
        
        # Mở trang cá nhân
        try:
            profile_button = self.browser.find_element(By.XPATH, push['openProfile'])
            profile_button.click()
            
        except: 
            raise ValueError('Không thể mở trang cá nhân!')
        
        sleep(5)
        
        try:
            allPages = self.browser.find_elements(By.XPATH, '//div[contains(@aria-label, "Switch to")]')
            print(f'Số fanpage để lướt: {len(allPages)}')
            processes = []
            for page in allPages:
                name = page.text.strip()
                process = Process(target=handleCrawlNewFeed, args=(account,name))
                processes.append(process)
                process.start()
            
            for process in processes:
                process.join()
            print("Tất cả fanpage đã được xử lý.")
            
        except Exception as e: 
            raise ValueError(e)
    