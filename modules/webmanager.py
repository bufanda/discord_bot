"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: Remote control websites
"""
import traceback

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from modules.configmanager import ConfigManager

class web_ping_perfect:    
    config: ConfigManager

    def __init__(self):
        self.config = ConfigManager()

    def webmanager_get_game_status(self, bot_username: str, bot_password: str) -> str:
        retvalue = "unkown"
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

        driver = webdriver.Remote(command_executor=f'http://{self.config.selenium_host}/wd/hub',
                                  options=chromeOptions)
        try:
            driver.get("https://gamepanel.pingperfect.com/Login")
            assert "Pingperfect - Login" in driver.title
            username = driver.find_element(By.NAME, 'UserName')
            username.clear()
            username.send_keys(bot_username)
            password = driver.find_element(By.NAME, 'Password')
            password.clear()
            password.send_keys(bot_password)
            password.send_keys(Keys.RETURN)

            if "Home" in driver.page_source:
                print(f"Logged in to {driver.title}")
                servicetable = driver.find_element(By.ID,"ServiceInformation")
                fieldnames = servicetable.find_elements(By.CLASS_NAME, "FieldName")
                fieldvalues = servicetable.find_elements(By.CLASS_NAME, "FieldValue")
                serversstatus = "unkown"
                for key,field in enumerate(fieldnames):
                    if field.text == "Status:":
                        serversstatus = fieldvalues[key].text
                print(f"Server Status: {serversstatus}")
                retvalue = serversstatus
                logout = driver.find_element(By.ID, "page_logout")
                logout.click()
        except AssertionError as e:
            if isinstance(e, AssertionError):
                print("Something went wrong while trying to login")
                traceback.print_tb(e.__traceback__)
        finally:
            driver.close()
            return retvalue

    def webmanager_get_reset_button(self, bot_username: str, bot_password: str) -> str:
        retvalue = "unkown"
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

        driver = webdriver.Remote(command_executor=f'http://{self.config.selenium_host}/wd/hub',
                                  options=chromeOptions)
        try:
            driver.get("https://gamepanel.pingperfect.com/Login")
            assert "Pingperfect - Login" in driver.title
            username = driver.find_element(By.NAME, 'UserName')
            username.clear()
            username.send_keys(bot_username)
            password = driver.find_element(By.NAME, 'Password')
            password.clear()
            password.send_keys(bot_password)
            password.send_keys(Keys.RETURN)

            if "Home" in driver.page_source:
                print(f"Logged in to {driver.title}")
                servicebuttons = driver.find_element(By.CLASS_NAME,"orange-button")
                if "Restart" in servicebuttons.text:
                    print("Restart Button found")
                #logout = driver.find_element(By.ID, "page_logout")
                #logout.send_keys(Keys.RETURN)
        except AssertionError as e:
            if isinstance(e, AssertionError):
                print("Something went wrong while trying to login")
                traceback.print_tb(e.__traceback__)
        except Exception as e:
            print(f"Unknown Exception Occured: {e}")
            traceback.print_tb(e.__traceback__)
        finally:
            driver.close()
            return retvalue
