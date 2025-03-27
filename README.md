# TrafficDown

[Telegram](https://t.me/HackActivity)

Это скрипт, который позволяет съесть много трафика, понизить скорость любой сети!
Необходим Python версии выше 3.13!

## Как он работает

Как он ест трафик: скрипт получает очень много мусорной информации, которая много весит. Из-за этого можно съесть у точки доступа много трафика.
Как он понижает скорость сети: скрипт делает очень много запросов на случайный IP (8.8.8.8:443), из-за чего сеть начинает лагать.

> Как добавить свои сервера со своими файлами для этого шоу? 
> docs.md в servers вам в помощь

## Баги?

Уверенно создавайте Issue, либо же заходите в наш телеграм канал и в комментариях опишите свою проблему. Вы нам очень поможете!

## Установка

Скрипт сам установит необходимые модули. Поддерживает:

- Android (termux)
- Linux дистрибутивы
- Windows
- WSL

Почему не поддерживает pydroid? Он ужасен.

## Запуск

Как использовать на Android:
Скачайте Termux, введите команду 
cd ~ && rm -rf TrafficDown && apt update && apt upgrade -y && apt install python3 -y && apt install git -y && git clone https://github.com/Sonys9/TrafficDown && cd TrafficDown && python3 TrafficDown.py

Как пользоваться на Windows:
Скачайте Python 3.13 и выше с Microsoft Store (там легче всего, либо через python.org) и запустите скрипт

Как пользоваться на Linux дистрибутивах:
Впишите в терминале команду cd ~ && rm -rf TrafficDown && apt update && apt upgrade -y && apt install python3 -y && apt install git -y && git clone https://github.com/Sonys9/TrafficDown && cd TrafficDown && python3 TrafficDown.py

💻 HackActivity (https://t.me/HackActivity)
![image](https://github.com/user-attachments/assets/7a89c0e3-6f6e-4ce9-94c6-98a25d167778)
