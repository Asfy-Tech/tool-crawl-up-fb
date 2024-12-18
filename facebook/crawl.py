
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
from urllib.parse import urlparse, parse_qs
from sql.comment import Comment 

class Crawl:
    def __init__(self, browser, page, his):
        self.browser = browser
        self.page = page
        self.his = his
        self.page_instance = Page()
        self.history_instance = HistoryCrawlPage()
        self.post_instance = Post()
        self.comment_instance = Comment()
        self.error_instance = Error()
        self.history_crawl_page_post_instance = HistoryCrawlPagePost()

    def get(self):
        sleep(1)
        closeModal(0, self.browser)
        self.browser.execute_script("document.body.style.zoom='0.2';")
        try:
            name_pages = self.browser.find_elements(By.XPATH, '//h1')
            name_page = name_pages[-1]
            self.page_instance.update_page(self.page['id'],{'name': name_page.text.strip()})
        except: 
            self.history_instance.update_history(self.his['id'],{
                'status': 3,
            })
            print('-> Không tìm thấy tên trang!')
            return
        
        self.getInfoPage()
        
        print("Bắt đầu lấy dữ liệu!")
        pageLinkPost = f"{self.page['link']}/posts/"
        pageLinkStory = "https://www.facebook.com/permalink.php"
        self.pageLinkPost = pageLinkPost
        self.pageLinkStory = pageLinkStory

        listPosts = self.browser.find_elements(By.XPATH, '//*[@aria-posinset]')
        if len(listPosts) > 5:
            listPosts = listPosts[:5]
        print(f"Lấy được {len(listPosts)} bài viết")
        try:
            post_links = []
            actions = ActionChains(self.browser)
            for p in listPosts:
                links = p.find_elements(By.XPATH, ".//a")
                for link in links:
                    if link.size['width'] > 0 and link.size['height'] > 0:
                        actions.move_to_element(link).perform()
                        href = link.get_attribute('href')
                        if any(substring in href for substring in [pageLinkPost, pageLinkStory]):
                            post_links.append(href)
        except Exception as e:
            print(f"Lỗi khi lấy đường dẫn: {e}")
        
        if(len(post_links) > 0):
            self.checkPost(post_links)
        sleep(1)
    
    def checkPost(self, post_links):
        post_ids = []
        for link in post_links:
            if self.pageLinkPost in link:
                id = link.replace(self.pageLinkPost, '').split('?')[0]
                if id not in post_ids:
                    post_ids.append(id)
            elif self.pageLinkStory in link:
                parsed_url = urlparse(link)
                query_params = parse_qs(parsed_url.query)
                story_fbid = query_params.get('story_fbid', [None])[0]
                if story_fbid not in post_ids:
                    post_ids.append(story_fbid)
                    
        print(f"=> Lấy ra được {len(post_ids)} đường dẫn chi tiết")
        
        self.history_instance.update_history(self.his['id'],{
            'counts': len(post_ids),
        })
        
        new_post_links = []
        seen_ids = set()
        for post_id in post_ids:
            for link in post_links:
                if post_id in link and post_id not in seen_ids:
                    new_post_links.append({
                        'id': post_id,
                        'link': link
                    })
                    seen_ids.add(post_id)
                    
        new_post_check_ids = self.post_instance.get_none_post_ids({
            'links':new_post_links,
            'his_id': self.his['id']
        })
        print(f"-> Lọc ra được {len(new_post_check_ids)} chưa tồn tại")
                    
        if new_post_check_ids:
            for postLink in new_post_check_ids:
                sleep(1)
                self.crawlPost(postLink)

    def crawlPost(self, postLink):
        # Cập nhật trạng thái đang lấy
        self.history_crawl_page_post_instance.update(postLink['id'], {
            'status':2,
        })
        data = {
            'post_id': postLink["post_fb_id"],
            'link_facebook': postLink['post_fb_link'],
            'page_id': self.page['id'],
            'content': '',
            'media' : {
                'images': [],
                'videos': []
            },
            'share': 0,
            'comment': 0,
            'like': 0,
            'up': False,
        }
        dataComment = []
        self.browser.get(f"{postLink['post_fb_link']}")
        print(f"- Chuyển hướng tới: {postLink['post_fb_link']}")
        sleep(5)
        
        print(f"Bắt đầu lấy dữ liệu bài viết: {postLink['post_fb_id']}")
        
        modal = None
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
            print(f'->Đã lấy nội dung')
        except:
            print(f'Không lấy được nội dung')
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
            print(f"Đã lấy {len(data['media']['images'])} ảnh và {len(data['media']['videos'])} video")
        except:
            print(f'Không lấy được ảnh hoặc video')
        
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
            print(f"Bài viết có: {data['like']} like, {data['comment']} comments, {data['share']} share")
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

                if 'Fan cứng' in textComment:
                    user_name = textArray[1]
                    textContentComment = ' '.join(textArray[2:])
                else:
                    user_name = textArray[0]
                    textContentComment = ' '.join(textArray[1:])

                if user_name == '' or textContentComment == '':
                    continue

                countComment += 1
                dataComment.append({
                    'post_id': postLink["post_fb_id"],
                    'user_name': user_name,
                    'content': textContentComment,
                    'link_comment': link_comment,
                })
            print(f"=> Lưu được {len(dataComment)} bình luận!")
        except Exception as e:
            print(e)
            print("Không lấy được bình luận!")

        self.insertPostAndComment(data,dataComment, postLink)
        
    def insertPostAndComment(self, data, dataComment, postLink):
        try:
            print("Đang lưu bài viết và bình luận vào database...")
            res = self.post_instance.insert_post({
                'post' : data,
                'comments': dataComment
            })
            print(f"Response: {res}")
            try:
                if res['post_id']:
                    self.history_crawl_page_post_instance.update(postLink['id'], {
                        'status':3,
                        'post_id': res['post_id']
                    })
                    res = self.history_instance.update_count(self.his['id'],{'type': 'count_get'})
            except:
                self.error_instance.insertContent(e)
            print("=> Đã lưu thành công!")
        except Exception as e:
            error = self.error_instance.insertContent(e)
            self.history_crawl_page_post_instance.update(postLink['id'], {
                'status':4,
                'error': error
            })
            self.history_instance.update_count(self.his['id'],{'type': 'count_error'})
        except KeyboardInterrupt:
            self.history_crawl_page_post_instance.update(postLink['id'], {
                'status':4,
            })
            self.history_instance.update_count(self.his['id'],{'type': 'count_error'})
        print("\n-----------------------------------------------------\n")

    def getInfoPage(self):
        dataUpdatePage = {}
        try:
            
            linkPage = self.page['link'].rstrip('/')
            try:
                # likes = self.browser.find_element(By.CSS_SELECTOR, f"a[href*='{linkPage}'][href*='friends_likes']")
                likes = self.browser.find_element(By.CSS_SELECTOR, f"a[href*='friends_likes']")
                dataUpdatePage['like_counts'] = likes.text
            except:
                pass

            try:
                follows = self.browser.find_element(By.CSS_SELECTOR, f"a[href*='followers']")
                dataUpdatePage['follow_counts'] = follows.text
            except:
                pass

            try:
                following = self.browser.find_element(By.CSS_SELECTOR, f"a[href*='following']")
                dataUpdatePage['following_counts'] = following.text
            except:
                pass
            if dataUpdatePage:
                print(f"Cập nhật (likes, followers, following) page: {self.page['id']}")
                self.page_instance.update_page(self.page['id'],dataUpdatePage)
        except Exception as e:
            self.error_instance.insertContent(e)
        except KeyboardInterrupt:
            res = self.history_instance.update_history(self.his['id'], {
                'status': 4,
            })
            print(f'Update status 4: {res}')
    