from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.options import Options

modian_url = ""


def get_modian_star() -> int:
    """
    正常返回点赞数，否则返回 -1
    """
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-gpu") 
        chrome_options.add_argument("--no-sandbox")  

        # USE THIS IN SERVER
        # driver = webdriver.Chrome(
        #     options=chrome_options
        # ) 

        driver = webdriver.Chrome()

        driver.get(modian_url)
        driver.implicitly_wait(5)

        bottom_btn = driver.find_element(By.CLASS_NAME, "bottom_btn")

        total_div = bottom_btn.find_element(By.CLASS_NAME, "total")
        star_count = int(total_div.text)

        driver.close()
        return star_count

    except Exception as e:
        print(e)
        driver.close()
        print("Fail to get modian star!")
        return -1


