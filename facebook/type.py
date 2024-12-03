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
    'modal': [
        '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[2]/div/div/div/div',
        '//*[@aria-posinset="1"]'
    ],
    'scroll': './div/div/div/div[2]',
    'content': './/*[@data-ad-rendering-role="story_message"]',
    'media': './/*[@data-ad-rendering-role="story_message"]/parent::div/following-sibling::div',
    'dyamic': './/*[@data-visualcompletion="ignore-dynamic"]/div/div/div/div',
    'hasMore': ".//div[text()='Xem thêm']",
    'comments': ".//*[contains(@aria-label, 'Bình luận')]",
    'form-logout': "//meta[@name='viewport']"
}


# Xoá chữ k cần thiết khi lấy content bài viết
removeString = [
    '\n',
    '·',
    '  ',
    'Xem bản dịch',
    'Xem bản gốc',
    'Xếp hạng bản dịch này'
]

# Xoá chữ k cần thiết khi lấy comment bài viết
removeComment = [
    '·',
    'Tác giả\n',
    '  ',
    'Fan cứngt'
    'Theo dõi',
]


# Xoá thông tin k cần thiết khi lấy lượt like, chia sẻ, comment
removeDyamic = [
    'Tất cả cảm xúc:',
    '',
]

# Lấy bình luận, chia sẻ dựa vào chữ này
selectDyamic = {
    'comment': 'bình luận',
    'share': 'lượt chia sẻ'
}



push = {
    'openProfile': '//*[@aria-label="Trang cá nhân của bạn"]',
    'createPost': ["bạn viết gì","bạn đang nghĩ gì"],
    'switchPage': lambda name: f'//*[contains(@aria-label, "Chuyển sang") and contains(@aria-label, "{name}")]'
}

