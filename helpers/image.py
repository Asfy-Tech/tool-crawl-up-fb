from io import BytesIO
from PIL import Image
import requests
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
