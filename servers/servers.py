"""
Если кратко - модуль для добавления сюда еще всяких серверов для тестирования скорости. Можете добавлять свои, если хотите. 
"""
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import urllib3

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Список рабочих серверов для тестирования скорости
SPEED_TEST_SERVERS = {
    'selectel': {
        'name': 'Selectel',
        'description': 'Стабильные сервера с высокой скоростью',
        'urls': [
            'https://speedtest.selectel.ru/10GB',
            'https://speedtest.selectel.ru/1GB',
#            'https://speedtest.selectel.ru/100MB',
            'http://speedtest.selectel.ru/10GB',
            'http://speedtest.selectel.ru/1GB',
#            'http://speedtest.selectel.ru/100MB'
        ]
    },
    'rastrnet': {
        'name': 'Rastrnet',
        'description': 'Надежные сервера с хорошей скоростью',
        'urls': [
            'https://speedtest.rastrnet.ru/1GB.zip',
            'https://speedtest.rastrnet.ru/500MB.zip',
#            'https://speedtest.rastrnet.ru/100MB.zip',
            'http://speedtest.rastrnet.ru/1GB.zip',
            'http://speedtest.rastrnet.ru/500MB.zip',
#            'http://speedtest.rastrnet.ru/100MB.zip'
        ]
    },
    'yandex': {
        'name': 'Yandex',
        'description': 'Быстрые сервера от Яндекс',
        'urls': [
#            'https://yandex.ru/internet/download/10mb.zip',
            'https://yandex.ru/internet/download/100mb.zip',
 #           'http://yandex.ru/internet/download/10mb.zip',
            'http://yandex.ru/internet/download/100mb.zip'
        ]
    },
    'google': {
        'name': 'Google',
        'description': 'Тестовые файлы от Google',
        'urls': [
#            'https://speed.cloudflare.com/10mb.bin',
            'https://speed.cloudflare.com/100mb.bin',
#            'http://speed.cloudflare.com/10mb.bin',
            'http://speed.cloudflare.com/100mb.bin'
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
            
        except Exception as e:
            with self.lock:
                self.tested_urls[url] = {
                    'speed': 0,
                    'status': 0
                }

    def test_all_urls(self):
        self.tested_urls = {}
        urls = get_all_urls()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
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

speed_tester = SpeedTester()

def get_all_urls():
    urls = []
    for provider in SPEED_TEST_SERVERS.values():
        urls.extend(provider['urls'])
    return urls

def get_provider_urls(provider_name):
    provider = SPEED_TEST_SERVERS.get(provider_name.lower())
    return provider['urls'] if provider else []

def get_providers_list():
    return [(k, v['name'], v['description']) for k, v in SPEED_TEST_SERVERS.items()]

def get_sorted_urls():
    return speed_tester.test_all_urls() 
