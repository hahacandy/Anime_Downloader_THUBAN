import requests 
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
import time
import m3u8_To_MP4
import shutil

save_dir = "Y:\Anime"
URL = 'https://animebee.to'
anime_name = ''

def driver_set():
    option = webdriver.ChromeOptions()

    # Chrome v75 and lower:
    # option.add_argument("--headless") 
    # Chrome v 76 and above (v76 released July 30th 2019):
    #option.headless = True

    option.add_argument('--window-size=1024x768')
    option.add_argument('--disable-gpu')

    chrome_prefs = {}
    option.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    option.add_argument('--user-data-dir=' + os.getcwd() + '/files/dataDir')

    driver = webdriver.Chrome('./driver/chromedriver.exe', options=option)
    return driver


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
        
        
def search_anime():
    global URL, anime_name
    
    while(True):
    
        keyword = input("input anime name : ")
        response = requests.get(URL+"/search?keyword="+keyword) 

        searched_anime_lists = []

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            titles = soup.select(".flw-item")

            if len(titles) > 0:

                for title in titles:
                    searched_anime_lists.append({'href' : title.select(".film-name > .dynamic-name")[0]['href'], 'name' : title.select(".film-name > .dynamic-name")[0].text})

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
                print("Your choice : " + anime_name)
                print()

                response = requests.get(searched_anime_lists[ani_sel-1]['href']) 
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                ani_page = soup.select(".film-buttons > a")[0]['href']


                return ani_page

            else:
                print("No Results Found!")

        else : 
            print(response.status_code)


def get_ani_ep_pages_and_urls(_ani_page):
    print("anime page loding...")

    ## Chrome의 경우 | 아까 받은 chromedriver의 위치를 지정해준다.
    driver = driver_set()
    driver.implicitly_wait(3)
    driver.get(_ani_page)

    eps_els = None
    while True:
        try:
            eps_els = driver.find_element_by_id("episodes-page-1").find_elements_by_tag_name('a')
            break
        except:
            print("anime page load fail, retry")

    ani_ep_list = []
    for idx, ep_el in enumerate(eps_els):
        page = ep_el.get_attribute('href')
        ani_ep_list.append({'page': page})
        print("anime page loding " + str(idx+1) + "/" + str(len(eps_els)))

    print("anime page load clear")
    print()
    
    print("anime info loding...")
    for idx, ani_ep in enumerate(ani_ep_list):

        i = 0
        while i >= 0:
            i = 0
            driver.get(ani_ep['page'])

            while i < 5:
                i = i + 1
                try:
                    driver.switch_to.frame(driver.find_elements_by_tag_name('iframe')[0])
                    video_time = driver.find_element_by_xpath('//*[@id="player"]/div[2]/div[12]/div[4]/div/div[10]').text
                    
                    if "00:00" in video_time:
                        continue
                    
                    driver.switch_to.default_content()
                    i = -1
                    break
                except:
                    time.sleep(1)
                    
                driver.switch_to.default_content()
                    
        time.sleep(1)
        while True:
            try:
                driver.switch_to.frame(driver.find_elements_by_tag_name('iframe')[0])
                mp4 = driver.find_element_by_tag_name('video').get_attribute('src')

                if 'blob' in mp4:
                    JS_get_network_requests = "var performance = window.performance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
                    network_requests = driver.execute_script(JS_get_network_requests)
                    for n in network_requests:
                        if ".m3u8" in n["name"]: 
                            mp4 = n["name"]

                print("주소:" + mp4)

                ani_ep['mp4'] = mp4
                break
            except:
                driver.switch_to.default_content()   


        print("anime info loding " + str(idx+1) + "/" + str(len(ani_ep_list)))

    driver.quit()
    print("anime info load clear")
    print() 
    
    return ani_ep_list




def download_anime(_ani_ep_list):
    global anime_name, save_dir
    
    file = './m3u8_To_Mp4.mp4'

    if os.path.isfile(file):
        os.remove(file)
    
    print('anime downloading...')
    
    save_anime_name = anime_name.replace(' ', '_').replace(':','')
    save_dir2 = save_dir + "\\" + save_anime_name
    createFolder("ani")
    createFolder(save_dir2)
    
    for idx, ani_ep in enumerate(_ani_ep_list):
        result = 1
        down_try = 0
        while result == 1 and down_try < 5:
            down_try = down_try + 1

            ep_number = str(idx+1)
            if len(ep_number) < 2:
                ep_number = '0' + ep_number
            print(anime_name, "ep"+str(idx+1) + " downloading", str(idx+1) + "/" + str(len(_ani_ep_list)))
            if ".m3u8" in ani_ep['mp4']:
                m3u8_To_MP4.download(ani_ep['mp4'])
                
                ani_save_path = save_dir2 + "/" + save_anime_name + "_ep" + ep_number + ".mp4"
                
                shutil.move('m3u8_To_Mp4.mp4', ani_save_path)
                
                if os.path.isfile(ani_save_path):
                    result = 0
            else:
                cmd = "aria2c -c -x 4 -d " + save_dir2+" -m 5 -o " + save_anime_name + "_ep" + ep_number + ".mp4 " + ''.join(ani_ep['mp4'])
                print(cmd)
                result = os.system(cmd)
            if result == 0:
                print(anime_name, "ep"+str(idx+1) + " downloaded", str(idx+1) + "/" + str(len(_ani_ep_list)))
                print()
            else:
                print("Retry" ,anime_name, "ep"+str(idx+1) + " downloading", str(idx+1) + "/" + str(len(_ani_ep_list)))

    print(anime_name + " all ani download complete")
    
    
    
while True:

    ani_page = search_anime()

    ani_ep_list = get_ani_ep_pages_and_urls(ani_page)

    download_anime(ani_ep_list)