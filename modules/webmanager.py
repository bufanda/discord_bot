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
    driver = webdriver.Chrome()
    driver.get("https://gamepanel.pingperfect.com/Login")
    assert "Pingperfect-Login" in driver.title
    username = driver.find_element(By.NAME, 'UserName')
    username.clear()
    username.send_keys(bot_username)
    username = driver.find_element(By.NAME, 'Password')
    username.clear()
    username.send_keys(bot_password)
    username.send_keys(Keys.RETURN)
    assert f"{bot_username} Home" in driver.page_source
    driver.close() 
