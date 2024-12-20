from selenium.webdriver.common.by import By

def closeModal(index, browser):
    try:
        closeModels = browser.find_elements(By.XPATH, '//*[@aria-label="Close"]')
        if len(closeModels) > index:
            closeModel = closeModels[index]
            if closeModel.is_displayed() and closeModel.is_enabled(): 
                closeModel.click()
            else:
                print("Phần tử không sẵn sàng để nhấp.")
    except Exception as e:
        pass