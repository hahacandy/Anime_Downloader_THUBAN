import requests 
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
from tqdm import tqdm

save_dir = "Y:\Anime"

URL = 'https://123animes.mobi'
keyword = input("input anime name : ")
response = requests.get(URL+"/search?keyword="+keyword) 

searched_anime_lists = []

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    titles = soup.select(".item > .inner")
 
    if "No Results Found" not in titles.__str__():
        
        for title in titles:
            searched_anime_lists.append({'href' : title.select(".name")[0]['href'], 'name' : title.select(".name")[0].text})
            

            
            
        for idx, searched_anime_list in enumerate(searched_anime_lists):
            print(idx+1, " : ",searched_anime_list['name'])


        ani_sel = 0
        while True:
            try:
                ani_sel = int(input("select anime number : "))

                if 0 >= ani_sel or idx+1 < ani_sel:
                    print("input error!")  
                else:
                    break

            except:
                print("input error!")

        anime_name = searched_anime_lists[ani_sel-1]['name']
        print()
        print("you choice : " + anime_name)
        print()



        

        def driver_set():
            option = webdriver.ChromeOptions()

            # Chrome v75 and lower:
            # option.add_argument("--headless") 
            # Chrome v 76 and above (v76 released July 30th 2019):
            option.headless = True

            option.add_argument('--window-size=1024x768')
            option.add_argument('--disable-gpu')

            chrome_prefs = {}
            option.experimental_options["prefs"] = chrome_prefs
            chrome_prefs["profile.default_content_settings"] = {"images": 2}
            chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
            option.add_argument('--user-data-dir=' + os.getcwd() + '/files/dataDir')

            driver = webdriver.Chrome('./driver/chromedriver.exe', options=option)
            return driver


        print("anime page loding...")

        ## Chrome의 경우 | 아까 받은 chromedriver의 위치를 지정해준다.
        driver = driver_set()
        driver.implicitly_wait(3)
        driver.get(URL+searched_anime_lists[ani_sel-1]['href'])

        eps_els = None
        while True:
            try:
                eps_els = driver.find_elements_by_class_name("episodes, range")[0].find_elements_by_tag_name('li')
                break
            except:
                print("anime page load fail, retry")

        ani_ep_list = []
        for idx, ep_el in enumerate(eps_els):
            page = ep_el.find_element_by_tag_name('a').get_attribute('href')
            ani_ep_list.append({'page': page})
            print("anime page loding " + str(idx+1) + "/" + str(len(eps_els)))

        print("anime page load clear")
        print()



        
        print("anime info loding...")
        for idx, ani_ep in enumerate(ani_ep_list):
            driver.get(ani_ep['page'])

            while True:
                try:
                    url = driver.find_element_by_xpath('//*[@id="player"]/iframe').get_attribute('src')

                    mp4 = requests.get(url).text
                    mp4 = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=_]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+mp4', mp4)

                    ani_ep['url'] = url
                    ani_ep['mp4'] = mp4
                    break
                except:
                    pass
            print("anime info loding " + str(idx+1) + "/" + str(len(ani_ep_list)))

        driver.quit()
        print("anime info load clear")
        print()



        

        def createFolder(directory):
            try:
                if not os.path.exists(directory):
                    os.makedirs(directory)
            except OSError:
                print ('Error: Creating directory. ' +  directory)

        save_anime_name = anime_name.replace(' ', '_')
        save_dir = save_dir + "\\" + save_anime_name
        createFolder("ani")
        createFolder(save_dir)

        
        print('anime downloading...')
        for idx, ani_ep in enumerate(ani_ep_list):
            result = 1
            down_try = 0
            while result == 1 and down_try < 5:
                down_try = down_try + 1
            
                ep_number = str(idx+1)
                if len(ep_number) < 2:
                    ep_number = '0' + ep_number
                print(anime_name, "ep"+str(idx+1) + " downloading", str(idx+1) + "/" + str(len(ani_ep_list)))
                cmd = "aria2c -c -x 4 -d "+save_dir+" -m 5 -o " + save_anime_name + " " + ep_number + ".mp4 " + ''.join(ani_ep['mp4'])
                result = os.system(cmd)
                if result == 0:
                    print(anime_name, "ep"+str(idx+1) + " downloaded", str(idx+1) + "/" + str(len(ani_ep_list)))
                    print()
                else:
                    print("Retry" ,anime_name, "ep"+str(idx+1) + " downloading", str(idx+1) + "/" + str(len(ani_ep_list)))

        print(anime_name + " all ani download complete")
            
        
            
    else:
        print("No Results Found!")
        
else : 
    print(response.status_code)