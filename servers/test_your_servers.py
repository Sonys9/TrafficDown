import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import urllib3
from colorama import init, Fore

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init()

# Скопируйте сюда ваш список серверов из servers.py
# Пример:
SPEED_TEST_SERVERS = {
    'your_provider': {
        'name': 'Your Provider',
        'description': 'Описание вашего провайдера',
        'urls': [
            'http://your-server.com/test1.zip',
            'http://your-server.com/test2.zip'
        ]
    }
}

class SpeedTester:
    def __init__(self):
        self.tested_urls = {}
        self.lock = threading.Lock()
        
    def test_url(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Range': 'bytes=0-1048576'  # Тестируем первый мегабайт
            }
            
            print(f"{Fore.YELLOW}[*] Тестируем {url}...{Fore.WHITE}")
            start_time = time.time()
            response = requests.get(url, headers=headers, stream=True, timeout=5, verify=False)
            
            chunk_size = 1024 * 128
            downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                downloaded += len(chunk)
                if downloaded >= 1048576:  
                    break
            
            end_time = time.time()
            duration = end_time - start_time
            speed = (downloaded / duration) / (1024 * 1024)  # MB/s
            
            with self.lock:
                self.tested_urls[url] = {
                    'speed': speed,
                    'status': response.status_code
                }
            
            print(f"{Fore.GREEN}[+] {url} - Скорость: {speed:.2f} MB/s{Fore.WHITE}")
            
        except Exception as e:
            print(f"{Fore.RED}[-] Ошибка при тестировании {url}: {e}{Fore.WHITE}")
            with self.lock:
                self.tested_urls[url] = {
                    'speed': 0,
                    'status': 0
                }

    def test_all_urls(self):
        self.tested_urls = {}
        urls = []
        for provider in SPEED_TEST_SERVERS.values():
            urls.extend(provider['urls'])
        
        print(f"{Fore.CYAN}[*] Найдено {len(urls)} URL-ов для тестирования{Fore.WHITE}")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.test_url, urls)
        
        sorted_urls = sorted(
            [(url, data) for url, data in self.tested_urls.items()],
            key=lambda x: x[1]['speed'],
            reverse=True
        )
        
        working_urls = [
            url for url, data in sorted_urls 
            if data['status'] in (200, 206) and data['speed'] > 0
        ]
        
        return working_urls

def main():
    print(f"{Fore.CYAN}=== Тестирование серверов ==={Fore.WHITE}")
    print(f"{Fore.YELLOW}Копируем результаты в буфер обмена...{Fore.WHITE}")
    
    tester = SpeedTester()
    working_urls = tester.test_all_urls()
    
    if not working_urls:
        print(f"{Fore.RED}[-] Нет рабочих серверов!{Fore.WHITE}")
        return
    
    print(f"\n{Fore.GREEN}=== Результаты тестирования ==={Fore.WHITE}")
    print(f"{Fore.GREEN}Найдено {len(working_urls)} рабочих серверов:{Fore.WHITE}")
    
    # Формируем текст для копирования
    copy_text = "SPEED_TEST_SERVERS = {\n"
    for provider_name, provider_data in SPEED_TEST_SERVERS.items():
        copy_text += f"    '{provider_name}': {{\n"
        copy_text += f"        'name': '{provider_data['name']}',\n"
        copy_text += f"        'description': '{provider_data['description']}',\n"
        copy_text += "        'urls': [\n"
        
        # Фильтруем только рабочие URL для этого провайдера
        working_provider_urls = [url for url in working_urls if url in provider_data['urls']]
        
        for url in working_provider_urls:
            copy_text += f"            '{url}',\n"
        
        copy_text += "        ]\n"
        copy_text += "    },\n"
    copy_text += "}"
    
    print("\n" + copy_text)
    print(f"\n{Fore.GREEN}Скопируйте ваш список серверов в servers.py{Fore.WHITE}")

if __name__ == "__main__":
    main() 