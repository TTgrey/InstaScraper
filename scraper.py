import selenium, time, re 
from datetime import datetime
from selenium.webdriver import Firefox


class InstaScrapper:
    """Парсер информации по постам для списка ссылок профилей.
    Используется управление браузером, т.к имеются динамические элементы на странице"""

    def __init__(self, number_of_posts):
        self.post = 'https://www.instagram.com/p/'
        self.scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
        self.post_details = []
        self.number_of_posts = number_of_posts
        self.counter = 0
        self.profiles_info = []
    def linksGenerator(self, browser, index = 0):
        """Получаем все элементы каждый раз и возвращаем поочередно (генератор),
        Чтобы обойти StaleReferenceException"""
        while True:
            all_elem = browser.find_elements_by_tag_name('a')
            if index >= len(all_elem):
                break
            yield all_elem[index]
            index += 1

    def getPostsUrls(self, browser, url):
        """Возвращает ссылки на последние 50 постов по ссылке профиля"""
        browser.get(url)
        post_links = []
        while len(post_links) < self.number_of_posts:
            try:
                #перемещаем скрол вниз
                browser.execute_script(self.scroll_down)
                #ищем кнопку внизу страницы "посмотреть больше публикаций" и нажимаем
                xpath_more = '//*[@id="react-root"]/section/main/div/div[3]/div[1]/div/button/div/div'
                browser.find_element_by_xpath(xpath_more).click()
            except:
                #обрабатываем исключение, когда кнопки после нажатия больше не будет
                pass
            #генерим элементы на странице и получаем из генератора ссылки
            for link in self.linksGenerator(browser):
                link_href = link.get_attribute('href')
                #проверяем ссылку на ссылку на пост
                if self.post in link_href and link_href not in post_links:
                    post_links.append(link_href)
            #скролим дальше вниз
            browser.execute_script(self.scroll_down)  
            #задержка для имитации человеческого поведения и прогрузки элементов 
            time.sleep(2)
        return post_links[:self.number_of_posts]

    def getProfilePostsDetails(self, profile_url):
        """Выдает информацию по сcылкам на посты профиля в виде списка из словарей для каждого поста"""
        browser = Firefox()
        post_urls = self.getPostsUrls(browser, profile_url)
        profile_details = {'datetime_of_getInfo': datetime.now(),
                           'profile_url': "", 
                           'number_of_posts': 0, 
                           'likes': 0, 
                           'comments': 0, 
                           'watches': 0 
                          }
        for url in post_urls:
            self.counter += 1
            browser.get(url)
            try:
                xpath_button_close_registration_inv = '/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div/div/button'
                browser.find_element_by_xpath(xpath_button_close_registration_inv).click()
            except:
                pass
            isVideo = False
            try:
                # получаем и приводим к определенному виду лайки и комментарии для постов с фотографией
                xpath_likes = '//*[@id="react-root"]/section/main/div/div/article/div[2]/section[2]/div/div/button/span'
                likes = int(browser.find_element_by_xpath(xpath_likes).text.replace(' ', ''))
            #ловим исключение, если у поста нет елемента лайки, тогда это видео
            except selenium.common.exceptions.NoSuchElementException:
                # получаем и приводим к определенному виду просмотры и комментарии для постов с видео, лайки получаем по клику на "просмотры"
                isVideo = True
                xpath_watches = '//*[@id="react-root"]/section/main/div/div/article/div[2]/section[2]/div/span'
                watches = int(browser.find_element_by_xpath(xpath_watches).text.replace('Просмотры: ', '').replace(' ',''))
                browser.find_element_by_xpath(xpath_watches).click()
                xpath_likes = '//*[@id="react-root"]/section/main/div/div/article/div[2]/section[2]/div/div/div[4]'
                likes = int(browser.find_element_by_xpath(xpath_likes).text.replace('Нравится: ', '').replace(' ',''))
            if  not isVideo:
                watches = 0
            xpath_datetime = '//*[@id="react-root"]/section/main/div/div/article/div[2]/div[2]/a/time'
            datetime_of_post = browser.find_element_by_xpath(xpath_datetime).get_attribute('datetime')
            #datetime_of_post = re.search('(?:"uploadDate":)(".*?")', browser.find_element_by_xpath('//script[@type="application/ld+json"]').get_attribute('innerHTML')).group(1).replace('"', '')
            try:
                comments = int(re.search('(?:"commentCount":)(".*?")', browser.find_element_by_xpath('//script[@type="application/ld+json"]').get_attribute('innerHTML')).group(1).replace('"', ''))
            except selenium.common.exceptions.NoSuchElementException:
                try:
                    xpath_comment = '//meta[@name="description"]'
                    comments = int(re.search(r'(?:,\s)(.*)(?:\sкомментариев)', browser.find_element_by_xpath(xpath_comment).get_attribute("content")).group(1).replace(',', ''))
                except:
                    comments = int(re.search('(?:"edge_media_to_parent_comment":{"count":)(.*?,)', browser.find_element_by_xpath('//script[contains(.,"edge_media_to_parent_comment")]').get_attribute('innerHTML')).group(1).replace(',', ''))
                    
            self.post_details.append(
                {
                    'datetime_of_getInfo': datetime.now(), 
                    'profile_url': profile_url,
                    'post_url': url,
                    'datetime_of_post': datetime_of_post,
                    'likes': likes, 
                    'comments': comments, 
                    'watches': watches
                }
            )
            
            profile_details['number_of_posts'] += 1
            profile_details['likes'] += likes
            profile_details['comments'] += comments
            profile_details['watches'] += watches
            time.sleep(2)
        profile_details['datetime_of_getInfo'] = datetime.now()
        profile_details['profile_url'] = profile_url
        self.profiles_info.append(profile_details)
        browser.close()
