from android_tv_rc import AndroidTVController
from datetime import datetime
from threading import Thread
import time
import os

TV_IP = "10.42.100.200"

# Checks if the TV is powered on
def is_powered() -> bool:
    command = f'adb -s {TV_IP}:5555 shell dumpsys power | grep "Display Power"'
    res = os.popen(command).read()
    return "state=ON" in res

# Connects with the tv
def get_remote() -> AndroidTVController:
    remote = AndroidTVController(TV_IP, True, True)
    remote.connect()
    if not remote.is_connected():
        raise Exception("Cannot connect with the TV...")
    return remote

# Turns on the tv if it is off and launches the kiosk browser program
def on():
    print("Turning on the TV...")
    remote = get_remote()
    if not is_powered():
        remote.press_power()
        for _ in range(20):
            if is_powered():
                break
            time.sleep(0.5)
        else:
            raise Exception('Cannot power on the TV...')
        remote.press_home()
        remote.get_adb_client().start_app('de.ozerov.fully', '.TvActivity')

# Turns off the tv if it is on and launches the kiosk browser program
def off():
    print("Turning off the TV...")
    remote = get_remote()
    if is_powered():
        remote.press_power()
        for _ in range(20):
            if not is_powered():
                break
            time.sleep(0.5)
        else:
            raise Exception('Cannot power off the TV...')
        
def schedule_onoff():
    while True:
        powered = is_powered()
        
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        weekday = now.weekday()
        
        if hour == 8 and minute == 00 and weekday >= 0 and weekday <= 4 and not powered:
            on()
        elif hour == 17 and minute == 00 and weekday >= 0 and weekday <= 4 and powered:
            off()
        time.sleep(5)
                        
if __name__ == '__main__':
    # Independent thread for the schedule on off function
    onoff_thread = Thread(target=schedule_onoff)
    onoff_thread.start()
    onoff_thread.join()