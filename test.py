from PIL import Image
import requests
from io import BytesIO
import win32clipboard 

def copy_image_to_clipboard(image_path_or_url):
    if image_path_or_url.startswith("http"):
        # Nếu là đường dẫn ảnh thì gửi request là lấy ảnh
        response = requests.get(image_path_or_url)
        img = Image.open(BytesIO(response.content))
    else:
        # Nếu là đường dẫn thư mục thì mở thư mục lấy ảnh
        img = Image.open(image_path_or_url)
    
    # Chuyển đổi ảnh sang định dạng DIB để đưa vào clipboard
    output = BytesIO()
    img.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    # Đưa ảnh vào clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

# URL của hình ảnh
image_url = 'https://scontent-fml1-1.xx.fbcdn.net/v/t39.30808-6/469184043_122192721452218503_8965209291314823777_n.jpg?stp=dst-jpg_p526x296_tt6&_nc_cat=102&ccb=1-7&_nc_sid=127cfc&_nc_ohc=eLXiD-JlQ4kQ7kNvgFar2f-&_nc_zt=23&_nc_ht=scontent-fml1-1.xx&_nc_gid=AaOSjE834FrFtmeln9tWlsB&oh=00_AYDSmu-hYHxdJCR5Jm1dHBfgJZXf-yI0qtpVc8i4dz47XA&oe=6755B2F9'

# Thực hiện sao chép ảnh vào clipboard
copy_image_to_clipboard(image_url)
