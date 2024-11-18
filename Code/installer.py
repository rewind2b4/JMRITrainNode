import network
from time import sleep
import mip
import config


def connect(Ssid, Password):
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(Ssid, Password)
    while wlan.isconnected() == False:
        print('Waiting for connection to installation server...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return wlan


def main():
    while True:
        wlan = connect(config.Installation_Ssid, config.Installation_Password)
        try:
            mip.install('umqtt.simple')
            wlan.disconnect()
            break
        except Exception as e:
            print("Installation Error:", e)
            continue

if __name__ == '__main__':
    main()

