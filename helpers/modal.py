from selenium.webdriver.common.by import By

def closeModal(index, browser):
    try:
        closeModels = browser.find_elements(By.XPATH, '//*[@aria-label="Đóng"]') # Đóng thông báo nếu có
        if len(closeModels) > index:
            closeModel = closeModels[index]  # Lấy phần tử thứ hai
            if closeModel.is_displayed() and closeModel.is_enabled():  # Kiểm tra hiển thị
                closeModel.click()
            else:
                print("Phần tử không sẵn sàng để nhấp.")
    except Exception as e:
        pass