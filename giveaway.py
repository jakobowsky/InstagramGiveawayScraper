import os, time, random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from secrets import LOGIN, PASSWORD
import re

class Giveaway:
    def __init__(self, username, password, give_away_people):
        self.give_away_people = give_away_people
        self.username = username
        self.password = password
        self.path = f'{os.getcwd()}/chromedriver'
        mobile_emulation = {
        "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}
        chrome_options = Options()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        self.driver = webdriver.Chrome(self.path, chrome_options=chrome_options)

    def login(self):
        driver = self.driver
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(2)
        element = driver.find_element_by_name('username')
        element.send_keys(self.username)
        element = driver.find_element_by_name('password')
        element.send_keys(self.password)
        time.sleep(2)
        element.submit()
        time.sleep(5)

    def close_browser(self):
        self.driver.close()

    
    def get_comments(self):
        self.driver.get('https://www.instagram.com/p/B4NssH8iVmJ/comments/')
        time.sleep(1)
        while True:
            try:
                button = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/ul/li/div/button')
                button.click()
                time.sleep(1)
            except Exception:
                print("Got all comments!")
                break
        comments = self.driver.find_elements_by_class_name("C4VMK")
        comments_list, users_list = [], []
        for comment in comments:
            ig_comment = comment.find_element_by_css_selector('span').get_attribute('textContent')
            ig_user = comment.find_element_by_class_name('TlrDj').get_attribute('textContent')
            comments_list.append(ig_comment)
            users_list.append(ig_user)
        comments_list = comments_list[1:]
        users_list = users_list[1:]
        profiles = self.check_comments(users_list, comments_list)
        return profiles


    def good_comment(self, comment):
        users = re.findall(r'@[\w\.-]+', comment)
        if len(users) > 1:
            for user in users:
                if user in self.give_away_people:
                    return False
                return True
        return False

    def check_comments(self, users_list, comments_list):
        profiles = []
        for user, comment in zip(users_list, comments_list):
            if self.good_comment(comment):
                profiles.append(user)
        return profiles

    
    def get_people_who_liked(self):
        self.driver.get("https://www.instagram.com/p/B4NssH8iVmJ")
        link_to_likes = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[2]/section[2]/div/div/a')
        link_to_likes.click()
        time.sleep(2)
        current = len(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div[1]/div').find_elements_by_tag_name('a'))
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randint(1,2))
            new = len(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div[1]/div').find_elements_by_tag_name('a'))
            if new == current:
                print("Got all likes...")
                break
            current = new
        all_links = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div[1]/div').find_elements_by_tag_name('a')
        people = self.extract_likes(all_links)
        return people
    
    def extract_likes(self, all_links):
        people = set()
        for link in all_links:
            current = link.get_attribute('textContent')
            if current:
                people.add(current)
        return people

    def check_if_liked(self, ppl_commented, ppl_like):
        people_to_chose =set()
        for guy in ppl_commented:
            if guy in ppl_like:
                people_to_chose.add(guy)
        return people_to_chose

    def pick_winners(self, people, number_of_winners):
        people = list(people)
        random.shuffle(people)
        for number in range(1, number_of_winners+1):
            print(f'Winne number {number} is {people.pop()}')
            time.sleep(1)


if __name__ == '__main__':
    giveaway_people = ['@jakobowsky', '@someone']
    ig = Giveaway(LOGIN, PASSWORD, give_away_people)
    print("Logged in...")
    ig.login()
    print("Getting people who commented and tagged 2 friends...")
    people_who_commented = ig.get_comments()
    time.sleep(1)
    print('Getting people who liked post...')
    people_who_liked = ig.get_people_who_liked()
    time.sleep(1)
    people_to_chose = ig.check_if_liked(people_who_commented, people_who_liked)
    print(f"There is {len(people_to_chose)} people...")
    time.sleep(1)
    print(f"Picking winners...")
    ig.pick_winners(people_to_chose, 4)
    print('Congratulations!')
    ig.close_browser()