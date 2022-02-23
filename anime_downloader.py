import requests 
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
import time
import shutil
import threading
from selenium.webdriver.common.keys import Keys

save_dir = "Y:\Anime"
URL = 'https://123animes.mobi'
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
            titles = soup.select(".item > .inner")

            if "No Results Found" not in titles.__str__():

                for title in titles:
                    searched_anime_lists.append({'href' : title.select(".name")[0]['href'], 'name' : title.select(".name")[0].text, 'ep' : title.select(".ep")[0].text})




                for idx, searched_anime_list in enumerate(searched_anime_lists):
                    print(idx+1, " : ",searched_anime_list['name'],searched_anime_list['href'])


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

                anime_name = searched_anime_lists[ani_sel-1]['name'] + ' ' + searched_anime_lists[ani_sel-1]['href']
                print()
                print("Your choice : " + anime_name)
                print()

                ani_page = URL+searched_anime_lists[ani_sel-1]['href']
                return ani_page

def get_anime_pages(driver, ani_page):
    print("anime page loding...")

    ## Chrome의 경우 | 아까 받은 chromedriver의 위치를 지정해준다.
    driver.get(ani_page)

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
    return ani_ep_list

def get_anime_down_url(driver, ani_ep_list):
    #해당 애니메이션이 시즌2 같은게 나오면 애니제목이 그전 시즌과 그대로이기때문에, 시즌을 구별하기 위해 다시 애니제목을 지정
    global anime_name
    anime_name = ''

    print("anime info loding...")
    
    for idx, ani_ep in enumerate(ani_ep_list):

                
        #가끔 페이지 안뜰떄가 잇음 그럴땐 새로고침
        i = 0
        while i >= 0:
            i = 0
            driver.get(ani_ep['page'])

            while i < 5:
                i = i + 1
                try:
                    driver.find_element_by_xpath('//*[@id="player"]/iframe')
                    i = -1
                    break
                except:
                    time.sleep(1)

        
        if anime_name == '':
            anime_name = driver.find_element_by_xpath('//*[@id="main"]/div/div[7]/div/div[1]/div[2]/div[1]/div/h2').text
        
        #blob로 된 다운로드 주소는 어차피 사용불가이기때문에 m3u8을 찾는다
        while True:
            try:
                driver.switch_to.frame(driver.find_elements_by_tag_name('iframe')[0])
                driver.find_element_by_tag_name('video').send_keys(Keys.ENTER)
                mp4 = driver.find_element_by_tag_name('video').get_attribute('src')
                JS_get_network_requests = "var performance = window.performance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
                network_requests = driver.execute_script(JS_get_network_requests)
                referer = network_requests[0]['name']
                ani_ep['referer'] = referer
                
                if 'blob' in mp4:
                    for n in network_requests:
                        if ".m3u8" in n["name"]: 
                            #if "360" in n["name"] or "720" in n["name"] or "1080" in n["name"]:
                            mp4 = n["name"]
                            ani_ep['mp4'] = mp4
                            break
                elif '.mp4' in mp4:
                    ani_ep['mp4'] = mp4
                    break
                """    
                if 'referer' in ani_ep:
                    break
                """
                    
            except:
                #에러났으면 초점을 iframe 에서 다시 원래대로 복원해야함
                driver.switch_to.default_content()   
                
            #재생버튼 누르면 가끔 광고탭으로 이동함 그래서 1번쨰 탭으로 이동시킴
            driver.switch_to.window(driver.window_handles[0]) 

        print("레퍼런스:" + ani_ep['referer'])
        print("주소:" + ani_ep['mp4'])
        driver.switch_to.default_content()   
        print("anime info loding " + str(idx+1) + "/" + str(len(ani_ep_list)))


    print("anime info load clear")
    print()

def download_anime(_ani_ep_list):
    global anime_name, save_dir
    
    print('anime downloading...')
    
    save_anime_name = anime_name.replace(' ', '_').replace(':','').replace('?', '')
    save_dir2 = save_dir + "\\" + save_anime_name
    createFolder(save_dir2)
    
    thread_list = []
    for idx, ani_ep in enumerate(_ani_ep_list):
        t = threading.Thread(target=download_anime2, args=(idx, ani_ep, _ani_ep_list, save_anime_name, save_dir2, thread_list))
        t.daemon = True 
        t.start()
        thread_list.append(t)      
 
    for t in thread_list:
        t.join()

    print(anime_name + " all ani download complete")
    
    
def download_anime2(idx, ani_ep, _ani_ep_list, save_anime_name, save_dir2, thread_list):
    global anime_name, save_dir

    result = 1
    down_try = 0
    while result == 1 and down_try < 5:
        down_try = down_try + 1

        ep_number = str(idx+1)
        if len(ep_number) < 2:
            ep_number = '0' + ep_number
        print(anime_name, "ep"+str(idx+1) + " downloading", str(idx+1) + "/" + str(len(_ani_ep_list)))
        if ".m3u8" in ani_ep['mp4']:
            ani_save_path = save_dir2 + "/" + save_anime_name + "_ep" + ep_number + ".mp4"
            
            cmd = 'ffmpeg -y -referer \"' + ani_ep['referer'] + '\" -i \"' + ani_ep['mp4'] + '\" -bsf:a aac_adtstoasc -c copy ' + ani_save_path
            print(cmd)
            os.system(cmd)
            
            if os.path.isfile(ani_save_path):
                result = 0
        else:
            cmd = "aria2c -c -x 4 -d " + save_dir2+" -m 5 --referer=\"" + ani_ep['referer'] + "\" -o " + save_anime_name + "_ep" + ep_number + ".mp4 \"" + ''.join(ani_ep['mp4'] + "\"")
            print(cmd)
            result = os.system(cmd)
        if result == 0:
            print(anime_name, "ep"+str(idx+1) + " downloaded", str(idx+1) + "/" + str(len(_ani_ep_list)))
            print()
        else:
            print("Retry" ,anime_name, "ep"+str(idx+1) + " downloading", str(idx+1) + "/" + str(len(_ani_ep_list)))

ani_page = search_anime()
driver = driver_set()
driver.implicitly_wait(3)
ani_ep_list = get_anime_pages(driver, ani_page)
get_anime_down_url(driver, ani_ep_list)
driver.quit()
download_anime(ani_ep_list)
