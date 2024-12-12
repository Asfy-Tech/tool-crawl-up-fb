from sql.model import Model
import traceback
class Error(Model):
    def __init__(self):
        super().__init__()

    def insert(self, data):
        return self.post("errors", data=data)
    
    def insertContent(self, e):
        content = {
            "error_message": str(e),  # Lấy thông báo lỗi dạng chuỗi
            "error_type": type(e).__name__,  # Lấy tên loại lỗi (vd: TypeError)
            "traceback": traceback.format_exc()  # Ngữ cảnh lỗi đầy đủ (tuỳ chọn)
        }
        # Insert vào database
        self.insert({
            'content': str(content)  # Lưu dạng chuỗi
        })
        return str(content)
    
    def update(self, history_id, data):
        return self.put(f"errors/{history_id}", data=data)