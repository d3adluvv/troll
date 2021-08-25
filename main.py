APP_VERSION = 0.001
from time import sleep
from vk_api import VkApi
from vk_api import longpoll
from vk_api.exceptions import Captcha, VkApiError
from vk_api.longpoll import VkEventType, VkLongPoll
from random import randint, choice
import json
from requests import get
from os import system, name

from colorama import init, Fore
init()

def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')

with open('config.json', 'r') as f:
    config = json.load(f)

def installUpdate():
    r = get('https://raw.githubusercontent.com/insan1tyyy/troll/main/main.py').text
    r = r.replace('\r', '')
    with open('comments.py', 'w', encoding='utf-8') as f:
        f.write(r)
    print(f"{Fore.CYAN}Обновление успешно установлено! Запусти скрипт заново.")
    exit()

def checkUpdates():
    r:str = get('https://raw.githubusercontent.com/insan1tyyy/troll/main/main.py').text
    r = r.split('\r\n', maxsplit=1)[0]
    app_ver = float(r.replace('APP_VERSION = ', ''))
    if APP_VERSION < app_ver:
        confirm = input("Доступно обновление. Чтобы установить - нажми ENTER, Чтобы пропустить - напиши любой символ")
        if not confirm:
            installUpdate()
        else:
            return

checkUpdates()

def login():
    while True:
        token = input("Введи токен от страницы. Если хочешь использовать несколько токенов, впиши их, разделив знаком ;\n\n>>> ")
    
        try:
            user = VkApi(token=token).get_api().users.get()[0]
            name = '{} {}'.format(user['first_name'], user['last_name'])
            print(f'{Fore.YELLOW} Успешная авторизация как {name} !')
            return token

        except VkApiError:
            print(f'{Fore.RED}Неверный токен.')
            continue

def answerTokens():
    a = input("Если хочешь вставить новые токен, введи любой символ, иначе нажми ENTER, оставив поле пустым.\n\n>>> ")
    if a:
        config['token'] = login()
        with open('config.json', 'w') as f:
            json.dump(config, f, indent = 4)
        return
    else:
        return

if not config['token']:
    config['token'] = login()
    with open('config.json', 'w') as f: 
        json.dump(config, f, indent = 4)
else:
    answerTokens()

cmdlist = f'{Fore.CYAN}[0] {Fore.GREEN} Автоответчик\n{Fore.CYAN}[1] {Fore.GREEN} Спам в чат'
vk_session = VkApi(token = config['token'])
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def start():
    clear()
    print(f"{Fore.YELLOW}БОТ УСПЕШНО ЗАПУЩЕН\nКоманды:\n{cmdlist}")
    waitCmd()
    
def waitCmd():
    cmdId = input("Введи цифру >>> ")
    if cmdId == '0':
        setupTroll()
    elif cmdId == '1':
        setupSpam()


def setupTroll():
    clear()
    print(f"{Fore.RED}АВТООТВЕТЧИК\n{Fore.CYAN}Введи id пользователя, либо ссылку на него")
    user = input(">>> ")
    if '/' in user:
        user = vk.users.get(user_ids = user.split('/')[-1], name_case='Acc')[0]
        print(f"{Fore.GREEN}Запускаю атаку на", user['first_name'], user['last_name'])
        trollAttack(user['id'])
    return

def setupSpam():
    clear()
    print(f"{Fore.RED}СПАМ В ЧАТ\n{Fore.CYAN}Введи id чата, если это беседа, id чата выглядит так: c74 (отсюда надо взять только число). Если в личку, можно отправить ссылку на пользователя, либо его id.")
    chat = input(">>> ")
    if chat.isdigit():
        if int(chat) < 10000:
            getChat = vk.messages.getChat(chat_id = int(chat))
            print(f"{Fore.GREEN}Запускаю спам на", getChat['title'])
            spamChat(chat_id = int(chat), users = getChat['users'])

    if '/' in chat:
        user = vk.users.get(user_ids = chat.split('/')[-1], name_case='Acc')[0]
        print(f"{Fore.GREEN}Запускаю спам на", user['first_name'], user['last_name'])
        spamUser(user['id'])
    return

def spamChat(chat_id, users):
    while True:
        try:
            with open('patterns.txt', 'r', encoding='utf-8') as f:
                patterns = f.read().split('\n')
            if not patterns:
                return
            peer_id = 2000000000 + chat_id
            vk.messages.send(random_id = 0, peer_id = peer_id, message = f"@id" + str(choice(users)) + "(" + choice(patterns) + ")")
            sleep(randint(1,2))
        except VkApiError:
            print(f"{Fore.RED}Ошибка АПИ.")
            pass
        except Captcha:
            print(f"{Fore.RED}Капча, пауза на 10 сек...")
            sleep(10)
            pass


def spamUser(user_id):
    while True:
        try:
            with open('patterns.txt', 'r', encoding='utf-8') as f:
                patterns = f.read().split('\n')
            if not patterns:
                return
            peer_id = user_id
            vk.messages.send(random_id = 0, peer_id = peer_id, message = f"@id" + str(user_id) + "(" + choice(patterns) + ")")
            sleep(randint(1,2))
        except VkApiError:
            print(f"{Fore.RED}Ошибка АПИ.")
            pass
        except Captcha:
            print(f"{Fore.RED}Капча, пауза на 10 сек...")
            sleep(10)
            pass




def answerTroll(event, vk):
    with open('patterns.txt', 'r', encoding='utf-8') as f:
        patterns = f.read().split('\n')
    if not patterns:
        return
    else:
        vk.messages.send(random_id = 0, peer_id = event.peer_id, message = f"@id{event.user_id}(" + choice(patterns) + ")")
    return

def trollAttack(user_id):
    
    while 1:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and not event.from_me:
                    if event.user_id == user_id:
                        answerTroll(event, vk)
        except VkApiError:
            print(f"{Fore.RED}Ошибка АПИ.")
            pass
        except Captcha:
            print(f"{Fore.RED}Капча, пауза на 10 сек...")
            sleep(10)
            pass

start()
