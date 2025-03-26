"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: Remote control websites
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def webmanager_test() -> None:
    driver = webdriver.Chrome()
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    elem = driver.find_element(By.NAME, "q")
    elem.clear()
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
    driver.close()

def webmanager_test2(bot_username: str, bot_password: str) -> None:
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--disable-setuid-sandbox")

    chromeOptions.add_argument("--remote-debugging-port=9222")  # this

    chromeOptions.add_argument("--disable-dev-shm-using")
    chromeOptions.add_argument("--disable-extensions")
    chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_argument("--start-maximized")
    chromeOptions.add_argument("--disable-infobars")
    chromeOptions.add_argument(r"--user-data-dir=.\cookies\\test")

    driver = webdriver.Chrome(options=chromeOptions)
    try:
        driver.get("https://gamepanel.pingperfect.com/Login")
        assert "Pingperfect - Login" in driver.title
        username = driver.find_element(By.NAME, 'UserName')
        username.clear()
        username.send_keys(bot_username)
        username = driver.find_element(By.NAME, 'Password')
        username.clear()
        username.send_keys(bot_password)
        username.send_keys(Keys.RETURN)
        assert f"Game Services" in driver.page_source
        print(f"Logged in to {driver.title}")
    except AssertionError as e:
        if isinstance(e, AssertionError):
            print("Something went wrong while trying to login")
    finally:
        driver.close()
    
