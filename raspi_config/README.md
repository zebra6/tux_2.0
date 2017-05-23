Use these tools to setup the wifi capabilities of the Pi:

rc.local should replace /etc/rc.local 

wifi_connect should be used to connect to the available wifi (WIP: cannot
connect to WPA2/Enterprise)

An example wpa_supplicant.conf has been added to this folder. You will need
to modify the wpa_supplicant.conf under /etc/wpa_supplicant/wpa_supplicant.conf
(with sudo privileges) to add a new wifi network.
