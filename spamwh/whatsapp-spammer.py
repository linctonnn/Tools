from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

class WhatsAppSpammer:
    def __init__(self, target_name, messages, jumlah_pesan):
        self.target_name = target_name
        self.messages = messages
        self.jumlah_pesan = jumlah_pesan
        self.driver = None
        self.INPUT_BOX_XPATH = '/html/body/div[1]/div/div/div[3]/div/div[4]/div/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]'
        self.SEARCH_BOX_XPATH = '/html/body/div[1]/div/div/div[3]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]'
        
    def setup_driver(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.get("https://web.whatsapp.com")
        print("Buka WhatsApp Web...")
    
    def handle_login(self):
        print("Silakan scan QR code dulu...")
        WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located((By.XPATH, self.SEARCH_BOX_XPATH))
        )
        print("Login Success ygy")
        
        try:
            continue_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div[2]/div/button'))
            )
            continue_btn.click()
            print("Tombol 'Continue' diklik.")
        except Exception:
            print("Tombol 'Continue' tidak ditemukan, melanjutkan...")
    
    def search_contact(self):
        print(f"Mencari kontak: {self.target_name}")
        search_box = self.driver.find_element(By.XPATH, self.SEARCH_BOX_XPATH)
        search_box.click()
        search_box.send_keys(self.target_name)
        time.sleep(2)
        search_box.send_keys(Keys.ENTER)
    
    def send_messages(self):
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, self.INPUT_BOX_XPATH))
        )
        
        print(f"Mengirim {self.jumlah_pesan} pesan ke {self.target_name}...\n")
        for i in range(self.jumlah_pesan):
            msg = random.choice(self.messages)
            input_box = self.driver.find_element(By.XPATH, self.INPUT_BOX_XPATH)
            input_box.click()
            input_box.send_keys(msg)
            input_box.send_keys(Keys.ENTER)
            print(f"[{i+1}] Kirim: {msg}")
            time.sleep(0.5)
    
    def run(self):
        try:
            self.setup_driver()
            self.handle_login()
            self.search_contact()
            self.send_messages()
            print("\n✅ Selesai ngisengin 😎")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

# =============== KONFIGURASI ===============
if __name__ == "__main__":
    target_name = input("Masukkan nama kontak atau grub : ")
    messages = [
        "Halo bang",
        "Jangan ngambek ya",
        "Yok ngopi",
        "Virus detected... jk",
        "Waduh kamu nge-hack aku ya?",
        "Test test... 1 2 3"
    ]
    jumlah_pesan = 100  # bisa diubah

    # Jalankan spammer
    spammer = WhatsAppSpammer(target_name, messages, jumlah_pesan)
    spammer.run()