from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from data import username, password
import time
import random
from selenium.common.exceptions import NoSuchElementException

class InstagramBot():

    def __init__(self, username, password):

        self.username = username
        self.password = password
        self.browser = webdriver.Chrome('../chromedriver/chromedriver')

    def close_browser(self):

        self.browser.close()
        self.browser.quit()

    def login(self):

        browser = self.browser
        # browser_locale = 'en'
        browser.get('https://www.instagram.com/')
        time.sleep(random.randrange(10, 20))
        # chrome_options = webdriver.ChromeOptions()
        # prefs = {"profile.default_content_setting_values.notifications": 2}
        # chrome_options.add_argument("--lang={}".format(browser_locale))
        # chrome_options.add_experimental_option("prefs", prefs)
        # browser = webdriver.Chrome(chrome_options=chrome_options)

        username_input = browser.find_element(By.NAME, 'username')
        username_input.clear()
        username_input.send_keys(username)

        time.sleep(2)

        password_input = browser.find_element(By.NAME, 'password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(5)

    def like_photo_by_hashtag(self, hashtag):

        browser = self.browser
        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        time.sleep(5)

        for i in range(1, 4):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randrange(3, 5))
        hrefs = browser.find_elements(By.TAG_NAME, 'a')
        posts_urls = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

        for url in posts_urls:
            try:
                browser.get(url)
                time.sleep(3)
                likeButton = browser.find_element(By.CSS_SELECTOR, 'section:first-child span button').click()
                time.sleep(random.randrange(80, 100))
                print('Liked post:', url)
            except Exception as ex:
                print(ex)
                self.close_browser()

    #проверяем по xpath существует ли элемент на странице
    def xpath_exists(self, url):
        browser = self.browser
        try:
            browser.find_element(By.XPATH, url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    # ставим лайк на пост по прямой ссылке
    def put_exactly_like(self, userpost):
        browser = self.browser
        browser.get(userpost)
        time.sleep(4)

        wrong_userpage = "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div/h2"
        if self.xpath_exists(wrong_userpage):
            print("Такого поста не существует, проверьте URL")
            self.close_browser()
        else:
            print("Пост успешно найден, ставим лайк!")
            time.sleep(2)

            likeButton = browser.find_element(By.CSS_SELECTOR, 'section:first-child span button').click()
            time.sleep(2)

            print(f"Лайк на пост: {userpost} поставлен!")
            self.close_browser()

    # метод ставит лайки по ссылке на аккаунт пользователя
    def put_many_likes(self, userpage):

        browser = self.browser
        browser.get(userpage)
        time.sleep(4)

        wrong_userpage = "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div/h2"
        if self.xpath_exists(wrong_userpage):
            print("Такого пользователя не существует, проверьте URL")
            self.close_browser()
        else:
            print("Пользователь успешно найден, ставим лайки!")
            time.sleep(2)

            posts_count = int(browser.find_element(By.XPATH,
                "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/ul/li[1]/div/span/span").text)

            loops_count = int(posts_count / 12 + 1)
            print(loops_count)

            posts_urls = []
            for i in range(0, loops_count):
                hrefs = browser.find_elements(By.TAG_NAME, 'a')
                hrefs = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

                for href in hrefs:
                    posts_urls.append(href)

                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.randrange(2, 4))
                print(f"Итерация #{i}")
    #
            file_name = userpage.split("/")[-2]
    #
            with open(f'{file_name}.txt', 'a') as file:
                for post_url in posts_urls:
                    file.write(post_url + "\n")

            set_posts_urls = set(posts_urls)
            set_posts_urls = list(set_posts_urls)

            with open(f'{file_name}_set.txt', 'a') as file:
                for post_url in set_posts_urls:
                    file.write(post_url + '\n')

            with open(f'{file_name}_set.txt') as file:
                urls_list = file.readlines()

                for post_url in urls_list[0:]:
                    try:
                        browser.get(post_url)
                        time.sleep(2)

                        likeButton = browser.find_element(By.CSS_SELECTOR, 'section:first-child span button').click()
                        time.sleep(random.randrange(80, 100))
                        time.sleep(2)

                        print(f"Лайк на пост: {post_url} успешно поставлен!")
                    except Exception as ex:
                        print(ex)
                        self.close_browser()

            self.close_browser()

my_bot = InstagramBot(username, password)
my_bot.login()
# my_bot.put_exactly_like('put url on post')
# my_bot.put_many_likes('put url on userpage')
# my_bot.xpath_exists('put url in xpath')
# my_bot.like_photo_by_hashtag('put hashtag')