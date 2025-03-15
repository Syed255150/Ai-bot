import subprocess
import time
import psutil

def connect_vpn():
    vpn_command = [
        r"C:\Program Files\OpenVPN\bin\openvpn.exe",  
        "--config", "uk-lon.prod.surfshark.comsurfshark_openvpn_udp.ovpn",
        "--auth-user-pass", "auth.txt"
    ]
    vpn_process = subprocess.Popen(vpn_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("connecting to the vpn")
    time.sleep(10)  
    return vpn_process.pid  

def disconnect_vpn(vpn_pid):
  
    try:
        vpn_process = psutil.Process(vpn_pid)
        vpn_process.terminate() 
        vpn_process.wait(timeout=5)  
        print("VPN disconnected successfully.")
    except psutil.NoSuchProcess:
        print(f"No process found with PID {vpn_pid}.")
    except psutil.TimeoutExpired:
        print(f"Failed to gracefully terminate process with PID {vpn_pid}, forcing termination.")
        vpn_process.kill()  
def open_browser():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://www.google.com")
    time.sleep(10)  
    driver.quit()

if __name__ == "__main__":
    
    vpn_pid = connect_vpn()
    
   
    open_browser()
    
  
    disconnect_vpn(vpn_pid)
