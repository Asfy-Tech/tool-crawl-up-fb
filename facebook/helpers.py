import json
from time import sleep
from selenium.webdriver.common.by import By
from sql.account_cookies import AccountCookies
from sql.history_crawl_page_posts import HistoryCrawlPagePost
from selenium.webdriver.common.action_chains import ActionChains
from facebook.type import types,push
from helpers.modal import closeModal
from sql.accounts import Account
from base.browser import Browser
from sql.account_cookies import AccountCookies
from urllib.parse import urlparse, parse_qs

def login(browser, account):
    try:
        if not account['latest_cookie']:
            raise ValueError("Không có cookie để đăng nhập.")

        last_cookie = account['latest_cookie']    
        cookies = json.loads(last_cookie['cookies'])
        for cookie in cookies:
            browser.add_cookie(cookie)
        sleep(1)
        browser.get('https://facebook.com')
        sleep(1)
        
        try:
            browser.find_element(By.XPATH, types['form-logout'])
        except Exception as e:
            updateStatusAcountCookie(last_cookie['id'],1)
            raise ValueError("Cookie không đăng nhập được.")
        print(f"Login {account['name']} thành công")
        return last_cookie
    except Exception as e:
        print(f"Lỗi khi login với cookie: {e}")
        raise  # Ném lỗi ra ngoài để catch trong hàm handle()
    
    
def updateStatusAcountCookie(cookie_id, status):
        # 1: Chết cookie
        # 2: Cookie đang sống
        account_cookies = AccountCookies()
        account_cookies.update(cookie_id,{'status': status})
        
def updateStatusAcount(account_id, status):
        # 1: Lỗi cookie,
        # 2: Đang hoạt động,
        # 3: Đang lấy dữ liệu...,
        # 4: Đang đăng bài...
        account_instance = Account()
        account_instance.update_account(account_id, {'status_login': status})
        
def handleCrawlNewFeed(account, name):
    account_cookies = AccountCookies()
    history_crawl_page_posts = HistoryCrawlPagePost()
    browserStart = Browser(account['id'])
    browser = browserStart.start()
    browser.get("https://facebook.com")
    sleep(2)
    print(f'Chuyển hướng tới fanpage: {name}')
    cookie = login(browser,account)
    profile_button = browser.find_element(By.XPATH, push['openProfile'])
    profile_button.click()
    sleep(2)
    switchPage = browser.find_element(By.XPATH, push['switchPage'](name))
    switchPage.click()
    sleep(2)
    closeModal(1,browser)
    pageLinkPost = f"/posts/"
    pageLinkStory = "https://www.facebook.com/permalink.php"
    
    browser.execute_script("document.body.style.zoom='0.2';")
    sleep(3)
    
    listId = set() 
    while True:  # Lặp vô hạn cho đến khi có điều kiện dừng
        listPosts = browser.find_elements(By.XPATH, types['list_posts'])  # Lấy lại danh sách các bài viết
        actions = ActionChains(browser)
        
        for p in listPosts:
            idAreaPost = p.get_attribute('aria-posinset')
            if idAreaPost not in listId:
                listId.add(idAreaPost)
                links = p.find_elements(By.XPATH, ".//a")
                for link in links:
                    if link.size['width'] > 0 and link.size['height'] > 0:
                        actions.move_to_element(link).perform()
                        href = link.get_attribute('href')
                        post_id = ''
                        if any(substring in href for substring in [pageLinkPost, pageLinkStory]):
                            if pageLinkPost in href:
                                post_id = href.replace(pageLinkPost, '').split('?')[0]
                                post_id = post_id.split('/')[-1]
                            elif pageLinkStory in href:
                                parsed_url = urlparse(href)
                                query_params = parse_qs(parsed_url.query)
                                post_id = query_params.get('story_fbid', [None])[0]
                            if post_id == '': continue

                            data = {
                                'post_fb_id': post_id,
                                'post_fb_link': href,
                                'status': 1,
                                'newfeed': 1,
                                'cookie_id': cookie['id'],
                                'account_id': cookie['account_id'],
                            }
                            history_crawl_page_posts.insert(data)
                            account_cookies.updateCount(cookie['id'],'counts')
                            print(f'Đã lấy được 1 bài viết từ page: {name}')
    

        if len(listId) >= 20:
            browser.refresh() 
            sleep(2)  
            listId.clear() 
            browser.execute_script("document.body.style.zoom='0.2';")
            sleep(3)
            print('Load lại trang!')
        else:
            browser.execute_script("window.scrollBy(0, 500);")
        sleep(5)
    