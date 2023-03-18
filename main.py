from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data import username, password
import time
import random

def hashtag_search(username, password, hashtag):

    browser = webdriver.Chrome('../chromedriver/chromedriver')
    browser_locale = 'en'
    wait = WebDriverWait(browser, 10)

    try:
        url = 'https://www.instagram.com/'
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_argument("--lang={}".format(browser_locale))
        chrome_options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get(url)
        time.sleep(random.randrange(6, 25))

        username_input = browser.find_element(By.NAME, 'username')
        username_input.clear()
        username_input.send_keys(username)

        time.sleep(2)

        password_input = browser.find_element(By.NAME, 'password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(5)

        try:
            browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
            time.sleep(5)

            for i in range(1, 4):
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.randrange(3, 5))

            hrefs = browser.find_elements(By.TAG_NAME, 'a')
            # posts_urls = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

            posts_urls = []
            for item in hrefs:
                href = item.get_attribute('href')

                if "/p/" in href:
                    posts_urls.append(href)
                    print(href)

            for url in posts_urls:
                try:
                    browser.get(url)
                    time.sleep(5)
                    likeButton = browser.find_element(By.CSS_SELECTOR, 'section:first-child span button').click()
                    time.sleep(random.randrange(80, 100))
                    print('Liked post:', url)
                except Exception as ex:
                    print(ex)

            browser.close()
            browser.quit()

        except Exception as ex:
            print(ex)
            browser.close()
            browser.quit()

    except Exception as ex:
        print(ex)
        browser.close()
        browser.quit()


hashtag_search(username, password, 'surfing')