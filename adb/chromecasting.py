from android_tv_rc import AndroidTVController
from threading import Thread
import time
import os

TV_IP = ""

# Connects With The TV
def get_remote() -> AndroidTVController:
    remote = AndroidTVController(TV_IP, True, True)
    remote.connect()
    if not remote.is_connected():
        raise Exception("Cannot connect with the TV...")
    return remote

# Checks IF the TV is Powered ON
def is_powered() -> bool:
    command = f'adb -s {TV_IP}:5555 shell dumpsys power | grep "Display Power"'
    res = os.popen(command).read()
    return "state=ON" in res

# Checks IF it is Chromecasting
def is_chromecasting() -> bool:
    while True:
        remote = get_remote()
        
        command = f"adb -s {TV_IP}:5555 shell dumpsys activity activities"
        output = os.popen(command).read()
        is_chromecasting = 'com.google.android.apps.mediashell' in output
    
        command = f"adb -s {TV_IP}:5555 shell dumpsys activity activities | grep mResumedActivity"
        output = os.popen(command).read()
        is_running = 'de.ozerov.fully/.FullyActivity' in output
        
        command = f'adb -s {TV_IP}:5555 shell dumpsys media_session'
        output = os.popen(command).read()
        is_playing = "state=3" in output
        
        command = f"adb -s {TV_IP}:5555 shell dumpsys activity activities | grep youtube"
        output = os.popen(command).read()
        in_youtube = 'com.google.android.youtube.tv' in output
        
        condition = not is_playing and in_youtube
        
        is_on = is_powered()
    
        print(f"Chromecasting: {is_chromecasting}, Running: {is_running}, Chromecasting On Youtube: {condition}, Is playing: {is_playing}")

        if is_on and not is_chromecasting and not is_running or condition:
            print("Starting Kiosk Browser...")
            remote.press_home()
            remote.get_adb_client().start_app('de.ozerov.fully', '.TvActivity')
            
        time.sleep(10)
        
# Checks each 10 seconds if it is chromecasting
if __name__ == "__main__":
    chromecasting_thread = Thread(target=is_chromecasting)
    chromecasting_thread.start()
    chromecasting_thread.join()