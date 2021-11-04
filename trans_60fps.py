import os
import pathlib
import shutil
import threading
import time


"""
이 코드는 사용하지 않는다.. 걍만들었으니 둔다
A's Video Converter 라는 더 좋은 툴이 있기때문에..

このコードはもう使わない
理由はもっといい性能を持ってるA's Video Converterというツールがあるので。。
"""

"""
애니는 평균 24fps로 제작되어있다.
그걸 60fps까지 올리면 애니가 훨씬 부드러워 지기에 그 작업을 한다.

アニメは平均２４fpsで制作されている
それを６０fpsまで上げれば動きがはっきり見えるようになる
なのでその作業をするコード
"""

anime_path = os.path.dirname("Y:/Anime/")
ffmpeg_path = 'Z:/python/anime_downloder_thuban/4/'
thread_list = []

def trans_to_60fps(cmd):
    os.system(cmd)
    print(cmd)


for path, dirs, files in os.walk(anime_path):
    for file in files:
        file_path = os.path.join(path, file)
        path2 = pathlib.Path(file_path)

        change_name = str(path2.parent) + '/60FPS_' + file
        
        if os.path.isfile(change_name) == False and '60FPS' not in path2.name:
        
            if path2.suffix == '.mp4':
                cmd = ffmpeg_path + 'ffmpeg.exe -i \"' + file_path +\
                '\"  -filter:v  \"minterpolate=\'mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=60:me=ds\'\" ' + change_name
                t = threading.Thread(target=trans_to_60fps, args=(cmd,))
                t.daemon = True 
                t.start()
                thread_list.append(t)
                
            elif path2.suffix == '.srt':
                shutil.copyfile(str(file_path), change_name)
                print('cp:' + str(file_path) + '->' + change_name)
                
                
            #동시에 최대 n개까지만 인코딩 가능하게.
            if len(thread_list) >= 5:
                for t in thread_list:
                    t.join()
                #쓰레드 배열 삭제
                thread_list.clear()

            print()
            
