"""
    modal = Modal bài viết
    content = Nội dung (chữ) bài viết
    media = Hình ảnh, video
    dyamic = lượt like, chia sẻ, comment
    hasMore = Nút xem thêm
    Comment = Danh sách comment
"""

# VN
types = {
    'form-logout': "//meta[@name='viewport']",
    'verify_account': './/*[@aria-label="Verified"]',
    'friends_likes': "a[href*='friends_likes']",
    'followers': "a[href*='followers']",
    'following': "a[href*='following']",
    'list_posts': '//*[@aria-posinset]',
    
    'modal': [
        '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[2]/div/div/div/div',
        '//*[@aria-posinset="1"]'
    ],
    'content': './/*[@data-ad-rendering-role="story_message"]',
    
    'scroll': './div/div/div/div[2]',
    'media': './/*[@data-ad-rendering-role="story_message"]/parent::div/following-sibling::div',
    'dyamic': './/*[@data-visualcompletion="ignore-dynamic"]/div/div/div/div',
    'hasMore': ".//div[text()='See more']",
    'comments': ".//*[contains(@aria-label, 'Comment')]",
}


# Xoá chữ k cần thiết khi lấy content bài viết
removeString = [
    '\n',
    '·',
    '  ',
    'See Translation',  # Xem bản dịch
    'See original',     # Xem bản gốc
    'Rate this translation'  # Xếp hạng bản dịch này
]

# Xoá chữ k cần thiết khi lấy comment bài viết
removeComment = [
    '·',
    'Author\n',
    '  ',
    'Top fan'
    'Follow',
]


# Xoá thông tin k cần thiết khi lấy lượt like, chia sẻ, comment
removeDyamic = [
    'All reactions:',
    '',
]

# Lấy bình luận, chia sẻ dựa vào chữ này
selectDyamic = {
    'comment': 'comment',
    'share': 'share'
}



push = {
    'openProfile': '//*[@aria-label="Your profile"]',
    'allPages': '//*[contains(text(), "Switch to")]',
    'createPost': ["bạn viết gì","bạn đang nghĩ gì"],
    'switchPage': lambda name: f'//*[contains(@aria-label, "Switch to") and contains(@aria-label, "{name}")]'
}

