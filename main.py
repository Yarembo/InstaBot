import sqlite3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from data import users_settings_dict
import time
import random
import requests
import os
from db import Database

class InstagramBot():


    def __init__(self, username, password, window_size):
        self.username = username
        self.password = password
        options = Options()
        options.add_argument(f"--window-size={window_size}")
        self.browser = webdriver.Chrome('../chromedriver/chromedriver', options=options)


    def close_browser(self):
        self.browser.close()
        self.browser.quit()


    def login(self):
        browser = self.browser
        browser.get('https://www.instagram.com/')
        time.sleep(random.randrange(5, 10))
        username_input = browser.find_element(By.NAME, 'username')
        username_input.clear()
        username_input.send_keys(username)
        time.sleep(2)
        password_input = browser.find_element(By.NAME, 'password')
        password_input.clear()
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(15)


    #Лайки по хештэгу
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


    # Проверяем по xpath существует ли элемент на странице
    def xpath_exists(self, url):

        browser = self.browser
        try:
            browser.find_element(By.XPATH, url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist


    # Ставим лайк на пост по прямой ссылке
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


    # Метод собирает ссылки на все посты пользователя
    def get_all_posts_urls(self, userpage):
        browser = self.browser
        browser.get(userpage)
        time.sleep(4)

        wrong_userpage = "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div/h2"
        if self.xpath_exists(wrong_userpage):
            print("Такого пользователя не существует, проверьте URL")
            self.close_browser()
        else:
            print("Пользователь успешно найден, собираем ссылки на посты!")
            time.sleep(2)

            posts_number = browser.find_element(By.XPATH,
                                                   "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]"
                                                   "/section/main/div/header/section/ul/li[1]/span/span/span").text
            posts_count = str(posts_number.replace("\x20", ""))
            posts_count = int(posts_count)

            print(f"Количество постов: {posts_count}")

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

            file_name = userpage.split("/")[-2]

            with open(f'{file_name}.txt', 'a') as file:
                for post_url in posts_urls:
                    file.write(post_url + "\n")

            set_posts_urls = set(posts_urls)
            set_posts_urls = list(set_posts_urls)

            with open(f'{file_name}_set.txt', 'a') as file:
                for post_url in set_posts_urls:
                    file.write(post_url + '\n')


    # Метод ставит лайки по ссылке на аккаунт пользователя
    def put_many_likes(self, userpage):

        browser = self.browser
        self.get_all_posts_urls(userpage)
        file_name = userpage.split("/")[-2]
        time.sleep(4)
        browser.get(userpage)
        time.sleep(4)

        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            for post_url in urls_list[0:20]:
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


    # Метод скачивает контент со страницы пользователя
    def download_userpage_content(self, userpage):

        browser = self.browser
        self.get_all_posts_urls(userpage)
        file_name = userpage.split("/")[-2]
        time.sleep(4)
        browser.get(userpage)
        time.sleep(4)

        # создаём папку с именем пользователя для чистоты проекта
        if os.path.exists(f"{file_name}"):
            print("Папка уже существует!")
        else:
            os.mkdir(file_name)

        img_and_video_src_urls = []
        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            for post_url in urls_list[0:]:
                try:
                    browser.get(post_url)
                    time.sleep(5)

                    img_src = "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/" \
                              "div[1]/div[1]/article/div/div[1]/div/div/div/div[1]/img"
                    video_src = "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/" \
                                "div[1]/div[1]/article/div/div[1]/div/div/div/div/div/div/div/video"
                    img_many_src = "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/" \
                                   "main/div[1]/div[1]/article/div/div[1]/div/div[1]/div[2]/div/div/div/ul/li[2]/" \
                                   "div/div/div/div/div[1]/img"

                    post_id = post_url.split("/")[-2]
                    print(post_id)

                    if self.xpath_exists(img_src):
                        img_src_url = browser.find_element(By.XPATH, img_src).get_attribute("src")
                        img_and_video_src_urls.append(img_src_url)
                        time.sleep(5)

                        # сохраняем изображение
                        get_img = requests.get(img_src_url)
                        with open(f"{file_name}/{file_name}_{post_id}_img.jpg", "wb") as img_file:
                            img_file.write(get_img.content)

                    elif self.xpath_exists(video_src):
                        video_src_url = browser.find_element(By.XPATH, video_src).get_attribute("src")
                        img_and_video_src_urls.append(video_src_url)

                        # сохраняем видео
                        get_video = requests.get(video_src_url, stream=True)
                        with open(f"{file_name}/{file_name}_{post_id}_video.mp4", "wb") as video_file:
                            for chunk in get_video.iter_content(chunk_size=1024 * 1024):
                                if chunk:
                                    video_file.write(chunk)

                    elif self.xpath_exists(img_many_src):
                        img_many_src_url = browser.find_element(By.XPATH, img_many_src).get_attribute("src")
                        img_and_video_src_urls.append(img_many_src_url)

                        get_many_img = requests.get(img_many_src_url)
                        with open(f"{post_id}_img.jpg", "wb") as img_many_file:
                            img_many_file.write(get_many_img.content)

                    else:
                        print("Упс! Что-то пошло не так!")
                        img_and_video_src_urls.append(f"{post_url}, нет ссылки!")
                    print(f"Контент из поста {post_url} успешно скачан!")

                except Exception as ex:
                    print(ex)
                    self.close_browser()

            self.close_browser()

        with open(f'{file_name}/{file_name}_img_and_video_src_urls.txt', 'a') as file:
            for i in img_and_video_src_urls:
                file.write(i + "\n")


    # Метод подписки на всех подписчиков переданного аккаунта
    def get_all_followers(self, userpage):

        browser = self.browser
        browser.get(userpage)
        time.sleep(4)
        file_name = userpage.split("/")[-2]

        # создаём папку с именем пользователя для чистоты проекта
        if os.path.exists(f"{file_name}"):
            print(f"Папка {file_name} уже существует!")
        else:
            print(f"Создаём папку пользователя {file_name}.")
            os.mkdir(file_name)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.xpath_exists(wrong_userpage):
            print(f"Пользователя {file_name} не существует, проверьте URL")
            self.close_browser()
        else:
            print(f"Пользователь {file_name} успешно найден, начинаем скачивать ссылки на подписчиков!")
            time.sleep(2)

            followers_button = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/"
                                                              "div[1]/div[2]/section/main/div/header/section/ul/li[2]"
                                                              "/a/span/span/span")
            followers_count = followers_button.text
            followers_count = int(followers_count.split(' ')[0])
            print(f"Количество подписчиков: {followers_count}")
            time.sleep(2)

            loops_count = int(followers_count / 12)
            print(f"Число итераций: {loops_count}")
            time.sleep(4)

            followers_button.click()
            time.sleep(4)

            followers_ul = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/"
                                                          "div[2]/div/div/div/div/div[2]/div/div/div[2]")

            try:
                self.get_followers(userpage)

                with open(f"{file_name}/{file_name}.txt") as text_file:
                    users_urls = text_file.readlines()

                    for user in users_urls[0:20]:
                        try:
                            try:
                                with open(f'{file_name}/{file_name}_subscribe_list.txt',
                                          'r') as subscribe_list_file:
                                    lines = subscribe_list_file.readlines()
                                    if user in lines:
                                        print(f'Мы уже подписаны на {user}, переходим к следующему пользователю!')
                                        continue

                            except Exception as ex:
                                print('Файл со ссылками ещё не создан!')
                                # print(ex)

                            browser = self.browser
                            browser.get(user)
                            page_owner = user.split("/")[-2]

                            if self.xpath_exists("/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]"
                                                 "/section/main/div/header/section/div[1]/div[1]/div/div/a"):

                                print("Это наш профиль, уже подписан, пропускаем итерацию!")
                            elif self.xpath_exists(
                                    "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main"
                                    "/div/header/section/div[1]/div[1]/div/div[1]/button/div/div[1]"):
                                print(f"Уже подписаны, на {page_owner} пропускаем итерацию!")
                            else:
                                time.sleep(random.randrange(4, 8))

                                if self.xpath_exists(
                                        "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section"
                                        "/main/div/div/article/div[1]/div/h2"):
                                    try:
                                        follow_button = browser.find_element(By.XPATH,
                                            "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]"
                                            "/section/main/div/header/section/div[1]/div[1]/div/div/button").click()
                                        print(f'Запросили подписку на пользователя {page_owner}. Закрытый аккаунт!')
                                    except Exception as ex:
                                        print(ex)
                                else:
                                    try:
                                        if self.xpath_exists("/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/"
                                                             "div[1]/div[2]/section/main/div/header/section/div[1]/"
                                                             "div[1]/div/div/button"):
                                            follow_button = browser.find_element(By.XPATH, "/html/body/div[2]/div/"
                                                                                           "div/div[1]/div/div/div/"
                                                                                           "div[1]/div[1]/div[2]/"
                                                                                           "section/main/div/header/"
                                                                                           "section/div[1]/div[1]/div"
                                                                                           "/div/button").click()
                                            print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')
                                        else:
                                            follow_button = browser.find_element(By.XPATH, "/html/body/div[1]/section"
                                                                                           "/main/div/header/section/"
                                                                                           "div[1]/div[1]/div/span/"
                                                                                           "span[1]/button").click()
                                            print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')
                                    except Exception as ex:
                                        print(ex)

                                # записываем данные в файл для ссылок всех подписок, если файла нет, создаём,
                                # если есть - дополняем
                                with open(f'{file_name}/{file_name}_subscribe_list.txt',
                                          'a') as subscribe_list_file:
                                    subscribe_list_file.write(user)

                                time.sleep(random.randrange(120, 180))

                        except Exception as ex:
                            print(ex)
                            self.close_browser()

            except Exception as ex:
                print(ex)
                self.close_browser()

        self.close_browser()


    # Метод собираем ссылки на аккаунты подписчиков
    def get_followers(self, userpage):

        browser = self.browser
        browser.get(userpage)
        time.sleep(4)
        file_name = userpage.split("/")[-2]
        db = Database('InstaBotDataBase.db')

        # создаём папку с именем пользователя для чистоты проекта
        if os.path.exists(f"{file_name}"):
            print(f"Папка {file_name} уже существует!")
        else:
            print(f"Создаём папку пользователя {file_name}.")
            os.mkdir(file_name)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.xpath_exists(wrong_userpage):
            print(f"Пользователя {file_name} не существует, проверьте URL")
            self.close_browser()
        else:
            print(f"Пользователь {file_name} успешно найден, начинаем скачивать ссылки на подписчиков!")
            time.sleep(2)

            followers_button = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/"
                                                              "div[1]/div[2]/section/main/div/header/section/ul/li[2]"
                                                              "/a/span/span")
            followers_count = followers_button.text
            followers_count = int(followers_count.replace("\x20", ""))
            # followers_count = followers_button.get_attribute('title').replace("\xa0", "")
            # followers_count = int(followers_count)
            print(f"Количество подписчиков: {followers_count}")
            time.sleep(2)

            loops_count = int(followers_count / 12)
            print(f"Число итераций: {loops_count}")
            time.sleep(4)

            followers_button.click()
            time.sleep(4)

            followers_ul = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/"
                                                          "div/div/div/div/div[2]/div/div/div[2]")

            followers_urls = []
            for i in range(1, int(followers_count)):
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_ul)
                time.sleep(random.randrange(2, 4))
                print(f"Итерация #{i}")
                all_urls_div = followers_ul.find_elements(By.XPATH, f"/html/body/div[2]/div/div/div[2]/div/div/div[1]/"
                                                                    f"div/div[2]/div/div/div/div/div[2]/div/div/div[2]/"
                                                                    f"div/div/div[{i}]")
                for user_url in all_urls_div:
                    user_url = user_url.find_element(By.TAG_NAME, "a").get_attribute("href")
                    db.add_users(user_url)
                    followers_urls.append(user_url)
            with open(f"{file_name}/{file_name}.txt", "a") as text_file:
                for link in followers_urls:
                    text_file.write(link + "\n")


    # Метод собираем ссылки на аккаунты подписчиков
    def get_subs(self, userpage):

        browser = self.browser
        browser.get(userpage)
        time.sleep(4)
        file_name = userpage.split("/")[-2]

        # создаём папку с именем пользователя для чистоты проекта
        if os.path.exists(f"{file_name}"):
            print(f"Папка {file_name} уже существует!")
        else:
            print(f"Создаём папку пользователя {file_name}.")
            os.mkdir(file_name)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.xpath_exists(wrong_userpage):
            print(f"Пользователя {file_name} не существует, проверьте URL")
            self.close_browser()
        else:
            print(f"Пользователь {file_name} успешно найден, начинаем скачивать ссылки на подписчиков!")
            time.sleep(2)

            subscribe_button = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/"
                                                              "div[1]/div[2]/section/main/div/header/section/ul/li[3]"
                                                              "/a/span/span/span")
            followers_count = subscribe_button.text
            followers_count = int(followers_count.replace("\x20", ""))

            print(f"Количество подписчиков: {followers_count}")
            time.sleep(2)

            loops_count = int(followers_count / 12)
            print(f"Число итераций: {loops_count}")
            time.sleep(4)

            subscribe_button.click()
            time.sleep(4)

            followers_ul = browser.find_element(By.XPATH,
                                                    "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/div"
                                                    "/div/div/div/div[2]/div/div/div[3]")

            followers_urls = []
            for i in range(1, int(followers_count)):
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_ul)
                time.sleep(random.randrange(2, 4))
                print(f"Итерация #{i}")
                all_urls_div = followers_ul.find_elements(By.XPATH, f"/html/body/div[2]/div/div/div[2]/div/div/"
                                                                    f"div[1]/div/div[2]/div/div/div/div/div[2]/div"
                                                                    f"/div/div[3]/div[1]/div/div[{i}]")
                for url in all_urls_div:
                    url = url.find_element(By.TAG_NAME, "a").get_attribute("href")
                    followers_urls.append(url)
            with open(f"{file_name}/{file_name}.txt", "a") as text_file:
                for link in followers_urls:
                    text_file.write(link + "\n")


    # Метод для отправки сообщений в директ
    def send_direct_message(self, usernames="", message="", img_path=''):

        browser = self.browser
        time.sleep(random.randrange(2, 4))

        direct_message_button = "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[1]/div/" \
                                "div/div/div/div[2]/div[5]"

        if not self.xpath_exists(direct_message_button):
            print("Кнопка отправки сообщений не найдена!")
            self.close_browser()
        else:
            print("Отправляем сообщение...")
            direct_message = browser.find_element(By.XPATH, direct_message_button).click()
            time.sleep(random.randrange(2, 5))

        # отключаем всплывающее окно
        if self.xpath_exists("/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/"
                             "div/div/div[2]/span"):
            browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/"
                                           "div/div[2]/div/div/div[3]/button[2]").click()
        time.sleep(random.randrange(2, 4))

        send_message_button = browser.find_element(By.XPATH,
            "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div/div[2]/div/section/div/div/div/div/div[2]/"
            "div/div[3]/div/button").click()
        time.sleep(random.randrange(2, 4))

        to_input = browser.find_element(By.XPATH,
                                        "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/"
                                        "div[2]/div/div[2]/div[1]/div/div[2]/input")
        to_input.send_keys(usernames)
        time.sleep(random.randrange(2, 4))

        # выбираем получателя из списка
        users_list = browser.find_element(By.XPATH,
            "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div[2]"
            "/div[1]/div[1]/div/div/div[3]/div/button").click()
        time.sleep(random.randrange(2, 4))

        # # отправка сообщения нескольким пользователям
        # # for user in usernames:
        #     # вводим получателя
        #     to_input = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/
        #     div/div/div/div/div[2]/div/div[2]/div[1]/div/div[2]/input")
        #     to_input.send_keys(user)
        #     time.sleep(random.randrange(2, 4))

            # # выбираем получателя из списка
            # users_list = browser.find_element(By.XPATH,
            #     "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[2]/
        #     div[2]/div[1]/div[1]/div/div/div[3]/div/button").click()
            # time.sleep(random.randrange(10, 15))

        next_button = browser.find_element(By.XPATH,
            "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[1]/div/"
            "div[3]/div/button/div").click()
        time.sleep(random.randrange(2, 4))

        # отправка текстового сообщения
        if message:
            text_message_area_activate = browser.find_element(By.XPATH,
                "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div/div[2]/div/section/div/div/div/"
                "div/div[2]/div[2]/div/div[2]/div/div/div[2]").click()
            text_message_area = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[1]/div/div/div/"
                                                               "div[1]/div[1]/div/div[2]/div/section/div/div/div/"
                                                               "div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea")
            text_message_area.clear()
            text_message_area.send_keys(message)
            time.sleep(random.randrange(2, 4))
            text_message_area.send_keys(Keys.ENTER)
            print(f"Сообщение для {usernames} успешно отправлено!")
            time.sleep(random.randrange(2, 4))

        # отправка изображения
        if img_path:
            send_img_input = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/"
                                                            "div[1]/div/div[2]/div/section/div/div/div/div/div[2]/"
                                                            "div[2]/div/div[2]/div/div/button[1]")
            send_img_input.send_keys(img_path)
            print(f"Изображение для {usernames} успешно отправлено!")
            time.sleep(random.randrange(2, 4))

        self.close_browser()


    # Метод отписки от всех пользователей
    def unsubscribe_for_all_users(self, userpage):

        browser = self.browser
        browser.get(f"https://www.instagram.com/{username}/")
        time.sleep(random.randrange(3, 6))

        following_button = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/"
                                                          "div[1]/div[2]/section/main/div/header/section/ul/li[3]/a")
        following_count = following_button.find_element(By.TAG_NAME, "span").text

        # если количество подписчиков больше 999, убираем из числа запятые
        if '\xa0' in following_count:
            following_count = int(''.join(following_count.split('\xa0')))
        else:
            following_count = int(following_count)

        print(f"Количество подписок: {following_count}")

        time.sleep(random.randrange(2, 4))

        loops_count = int(following_count / 10) + 1
        print(f"Количество перезагрузок страницы: {loops_count}")

        following_users_dict = {}

        for loop in range(1, loops_count + 1):

            count = 10
            browser.get(f"https://www.instagram.com/{username}/")
            time.sleep(random.randrange(3, 6))

            # кликаем/вызываем меню подписок
            following_button = browser.find_element(By.XPATH, "/html/body/div[1]/section/main/div/header/section/"
                                                              "ul/li[3]/a")

            following_button.click()
            time.sleep(random.randrange(3, 6))

            # забираем все li из ul, в них хранится кнопка отписки и ссылки на подписки
            following_div_block = browser.find_element(By.XPATH, "/html/body/div[4]/div/div/div[2]/ul/div")
            following_users = following_div_block.find_elements(By.TAG_NAME, "li")
            time.sleep(random.randrange(3, 6))

            for user in following_users:

                if not count:
                    break

                user_url = user.find_element(By.TAG_NAME, "a").get_attribute("href")
                user_name = user_url.split("/")[-2]

                # добавляем в словарь пару имя_пользователя: ссылка на аккаунт, на всякий, просто полезно сохранять информацию
                following_users_dict[user_name] = user_url

                following_button = user.find_element(By.TAG_NAME, "button").click()
                time.sleep(random.randrange(3, 6))
                unfollow_button = browser.find_element(By.XPATH, "/html/body/div[5]/div/div/div/div[3]/"
                                                                 "button[1]").click()

                print(f"Итерация #{count} >>> Отписался от пользователя {user_name}")
                count -= 1

                # time.sleep(random.randrange(120, 130))
                time.sleep(random.randrange(2, 4))

        with open("following_users_dict.txt", "w", encoding="utf-8") as file:
            json.dump(following_users_dict, file)

        self.close_browser()


    # метод отписки, отписываемся от всех кто не подписан на нас
    def smart_unsubscribe(self, username):

        browser = self.browser
        browser.get(f"https://www.instagram.com/{username}/")
        time.sleep(random.randrange(3, 6))

        followers_button = browser.find_element(By.XPATH, "/html/body/div[1]/section/main/div/header/section/"
                                                          "ul/li[2]/a/span")
        followers_count = followers_button.get_attribute("title")

        following_button = browser.find_element(By.XPATH, "/html/body/div[1]/section/main/div/header/section/"
                                                          "ul/li[3]/a")
        following_count = following_button.find_element(By.TAG_NAME, "span").text

        time.sleep(random.randrange(3, 6))

        # если количество подписчиков больше 999, убираем из числа запятые
        if ',' in followers_count or following_count:
            followers_count, following_count = int(''.join(followers_count.split(','))), int(''.join(following_count.split(',')))
        else:
            followers_count, following_count = int(followers_count), int(following_count)

        print(f"Количество подписчиков: {followers_count}")
        followers_loops_count = int(followers_count / 12) + 1
        print(f"Число итераций для сбора подписчиков: {followers_loops_count}")

        print(f"Количество подписок: {following_count}")
        following_loops_count = int(following_count / 12) + 1
        print(f"Число итераций для сбора подписок: {following_loops_count}")

        # собираем список подписчиков
        followers_button.click()
        time.sleep(4)

        followers_ul = browser.find_element(By.XPATH, "/html/body/div[4]/div/div/div[2]")

        try:
            followers_urls = []
            print("Запускаем сбор подписчиков...")
            for i in range(1, followers_loops_count + 1):
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_ul)
                time.sleep(random.randrange(2, 4))
                print(f"Итерация #{i}")

            all_urls_div = followers_ul.find_elements(By.TAG_NAME, "li")

            for url in all_urls_div:
                url = url.find_element(By.TAG_NAME, "a").get_attribute("href")
                followers_urls.append(url)

            # сохраняем всех подписчиков пользователя в файл
            with open(f"{username}_followers_list.txt", "a") as followers_file:
                for link in followers_urls:
                    followers_file.write(link + "\n")
        except Exception as ex:
            print(ex)
            self.close_browser()

        time.sleep(random.randrange(4, 6))
        browser.get(f"https://www.instagram.com/{username}/")
        time.sleep(random.randrange(3, 6))

        # собираем список подписок
        following_button = browser.find_element(By.XPATH, "/html/body/div[1]/section/main/div/header/section/ul/li[3]/a")
        following_button.click()
        time.sleep(random.randrange(3, 5))

        following_ul = browser.find_element(By.XPATH, "/html/body/div[4]/div/div/div[2]")

        try:
            following_urls = []
            print("Запускаем сбор подписок")

            for i in range(1, following_loops_count + 1):
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", following_ul)
                time.sleep(random.randrange(2, 4))
                print(f"Итерация #{i}")

            all_urls_div = following_ul.find_elements(By.TAG_NAME, "li")

            for url in all_urls_div:
                url = url.find_element(By.TAG_NAME, "a").get_attribute("href")
                following_urls.append(url)

            # сохраняем всех подписок пользователя в файл
            with open(f"{username}_following_list.txt", "a") as following_file:
                for link in following_urls:
                    following_file.write(link + "\n")

            """Сравниваем два списка, если пользователь есть в подписках, но его нет в подписчиках,
            заносим его в отдельный список"""

            count = 0
            unfollow_list = []
            for user in following_urls:
                if user not in followers_urls:
                    count += 1
                    unfollow_list.append(user)
            print(f"Нужно отписаться от {count} пользователей")

            # сохраняем всех от кого нужно отписаться в файл
            with open(f"{username}_unfollow_list.txt", "a") as unfollow_file:
                for user in unfollow_list:
                    unfollow_file.write(user + "\n")

            print("Запускаем отписку...")
            time.sleep(2)

            # заходим к каждому пользователю на страницу и отписываемся
            with open(f"{username}_unfollow_list.txt") as unfollow_file:
                unfollow_users_list = unfollow_file.readlines()
                unfollow_users_list = [row.strip() for row in unfollow_users_list]

            try:
                count = len(unfollow_users_list)
                for user_url in unfollow_users_list:
                    browser.get(user_url)
                    time.sleep(random.randrange(4, 6))

                    # кнопка отписки
                    unfollow_button = browser.find_element(By.XPATH, "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button")
                    unfollow_button.click()

                    time.sleep(random.randrange(4, 6))

                    # подтверждение отписки
                    unfollow_button_confirm = browser.find_element(By.XPATH, "/html/body/div[4]/div/div/div/div[3]/button[1]")
                    unfollow_button_confirm.click()

                    print(f"Отписались от {user_url}")
                    count -= 1
                    print(f"Осталось отписаться от: {count} пользователей")

                    # time.sleep(random.randrange(120, 130))
                    time.sleep(random.randrange(4, 6))

            except Exception as ex:
                print(ex)
                self.close_browser()

        except Exception as ex:
            print(ex)
            self.close_browser()

        time.sleep(random.randrange(4, 6))
        self.close_browser()

    #Метод сбора информации о пользователе
    # def get_user_info(self):
    #     browser = self.browser
    #     try:
    #         db = Database('InstaBotDataBase.db')
    #         userpages = db.get_db_userpage()
    #
    #         for i in userpages:
    #             userpage = str(i)
    #             file_name = userpage.split("/")[-2]
    #             browser.get(f'https://www.instagram.com/{file_name}/')
    #
    #             wrong_userpage = "/html/body/div[1]/section/main/div/h2"
    #             if self.xpath_exists(wrong_userpage):
    #                 print(f"Пользователя {file_name} не существует, проверьте URL")
    #                 self.close_browser()
    #             else:
    #                 print(f"Пользователь {file_name} успешно найден, начинаем скачивать инфо!")
    #                 time.sleep(2)
    #
    #                 followers = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/"
    #                                                            "div[1]/div[2]/section/main/div/header/section/ul/li[2]"
    #                                                            "/a/span/span")
    #                 followers_count = followers.text
    #                 followers_count = int(followers_count.replace("\x20", ""))
    #
    #                 time.sleep(5)
    #
    #                 subscribe = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]"
    #                                                         "/div[2]/section/main/div/header/section/ul/li[3]/a/span/span")
    #                 print(subscribe)
    #                 subscribe_count = subscribe.text
    #                 subscribe_count = int(subscribe_count.replace("\x20", ""))
    #                 print(subscribe_count)
    #
    #                 FIO = browser.find_element(By.XPATH, "/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]"
    #                                                         "/div[2]/section/main/div/header/section/div[3]/span")
    #                 FIO = FIO.text
    #                 print(FIO)
    #
    #                 status_close = ("/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div/"
    #                           "article/div[1]/div/h2")
    #                 if self.xpath_exists(status_close):
    #                     status = "Закрытый аккаунт!"
    #                 else:
    #                     status = "Открытый аккаунт!"
    #
    #                 db.add_user_info(FIO, status, followers_count, subscribe_count)
    #                 time.sleep(2)
    #     except sqlite3.Error as error:
    #          print("Ошибка при работе с БД")

for users, user_data in users_settings_dict.items():
    username = user_data['login']
    password = user_data['password']
    windows_size = user_data['window_size']

    my_bot = InstagramBot(username, password, windows_size)
    my_bot.login()
    my_bot.get_user_info()
    my_bot.close_browser()
    time.sleep(random.randrange(4, 10))