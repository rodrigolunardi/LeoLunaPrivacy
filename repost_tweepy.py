# AVISO: Use por sua conta e risco. Respeite limites da API Free Tier (50 RTs/15min).
# Dependências: pip install tweepy schedule colorama pytz

import tweepy
import schedule
import time
import random
import logging
from datetime import datetime
import pytz
from colorama import Fore, Style, init

init(autoreset=True)

# CONFIGURAÇÕES - SUBSTITUA AQUI
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAF7K7QEAAAAA8lb8Ua%2BsZpW0mc0mIcfW0990d0w%3DXSBTR5qcBWFGHY9XGGkCvPtp5b7zrF4iDJWoJwegY2cCEFghuA'
API_KEY = 'oxDV2hUQ0fV3hRJ57aB4vmA66'
API_SECRET = 'AbEq7h3Qb8CH7PhvGfyAP3VDn8Nz38tvCWLKO7VeFgSywVuQOf'
ACCESS_TOKEN = '3788029636-T34HgLbursMVAPxysDpMUv71oFN0sfBJsKAIBpP'
ACCESS_TOKEN_SECRET = 'ik8maUr2X2VDRXIOHEi8bVFh4qe3T1PYtGnv9K86bctl8'

# URLs por período
DAYTIME_URLS = [  # Diurnas
    'https://x.com/lrdirdr/status/2019077171453608185',
    'https://x.com/lrdirdr/status/2017243968669442480'
]

NIGHTTIME_URLS = [  # Noturnas
    'https://x.com/lrdirdr/status/2020189301695246359'
]

HORARIOS_POR_DIA = {
    'monday': ['01:00', '12:00', '17:00'],      # Segunda
    'tuesday': ['01:00', '12:00'],              # Terça
    'wednesday': ['14:00', '23:00'],            # Quarta
    'thursday': ['13:00', '23:00'],             # Quinta
    'friday': ['00:00', '15:00'],               # Sexta
    'saturday': ['12:00', '23:00'],             # Sábado
    'sunday': ['00:00', '11:00', '17:00', '21:00']  # Domingo
}

# TESTE: Horário extra noturno (mude aqui, ex: '21:30')
TEST_MODE = False  # True pra ativar teste, False pra produção
TEST_HORARIO = '21:49'  # Hora pra testar (formato HH:MM)

# Classificação de horários
DAYTIME_HORARIOS = {'11:00', '12:00', '13:00', '14:00', '15:00', '17:00'}
NIGHTTIME_HORARIOS = {'00:00', '01:00', '21:00', '23:00'}

# Configurar logging
logging.basicConfig(filename='repost_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Fuso SP
TZ = pytz.timezone('America/Sao_Paulo')

# Cliente Tweepy v2
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

def log(msg, color=Fore.WHITE):
    timestamp = datetime.now(TZ).strftime('%H:%M:%S')
    print(f"{color}[{timestamp}] {msg}{Style.RESET_ALL}")
    logging.info(msg)

def extrair_tweet_id(url):
    return url.split('/')[-1].split('?')[0]

def processar_reposts(urls, is_test=False):
    for i, url in enumerate(urls):
        try:
            tweet_id = extrair_tweet_id(url)
            log(f"🔄 Processando URL {i+1}: {url}", Fore.CYAN)
            
            # Desfazer repost anterior
            try:
                client.unretweet(tweet_id)
                time.sleep(random.uniform(1, 3))
                log("✅ Desfeito repost anterior", Fore.GREEN)
            except tweepy.Forbidden:
                log("ℹ️ Não havia repost anterior", Fore.BLUE)
            except Exception as e:
                log(f"⚠️ Erro unretweet: {e}", Fore.RED)
            
            time.sleep(random.uniform(5, 15))
            
            # Repostar
            client.retweet(tweet_id)
            log(f"✅ Repostado: {tweet_id}", Fore.GREEN)
            
            time.sleep(random.uniform(30, 60))
            
        except tweepy.Forbidden as e:
            if "already retweeted" in str(e).lower():
                log("ℹ️ Já repostado, pulando", Fore.BLUE)
            else:
                log(f"❌ Erro Forbidden: {e}", Fore.RED)
        except tweepy.TooManyRequests:
            log("⏳ Rate limit, aguardando...", Fore.YELLOW)
            time.sleep(900)
        except Exception as e:
            log(f"❌ Erro: {e}", Fore.RED)
            for retry in range(3):
                time.sleep(10)
                try:
                    client.retweet(tweet_id)
                    log(f"✅ Retry {retry+1} OK", Fore.GREEN)
                    break
                except:
                    pass

def executar_reposts():
    agora = datetime.now(TZ).strftime('%H:%M')
    
    # TESTE EXTRA NOTURNO
    if TEST_MODE and agora == TEST_HORARIO:
        log(f"🧪 TESTE NOTURNO em {TEST_HORARIO}!", Fore.MAGENTA)
        processar_reposts(NIGHTTIME_URLS, is_test=True)
        log("🧪 Teste concluído!", Fore.MAGENTA)
        return
    
    # Horários normais por dia
    dia_semana = datetime.now(TZ).strftime('%A').lower()
    horarios = HORARIOS_POR_DIA.get(dia_semana, [])
    
    for horario in horarios:
        if agora == horario:
            log(f"🕐 Horário normal: {horario} ({dia_semana})", Fore.YELLOW)
            
            if horario in DAYTIME_HORARIOS:
                urls = DAYTIME_URLS
                log("☀️ Fotos DIURNAS", Fore.ORANGE)
            elif horario in NIGHTTIME_HORARIOS:
                urls = NIGHTTIME_URLS
                log("🌙 Fotos NOTURNAS", Fore.BLUE)
            else:
                urls = DAYTIME_URLS
                log("☀️ Fallback DIURNAS", Fore.ORANGE)
            
            processar_reposts(urls)
            log("🎉 Ciclo concluído!", Fore.MAGENTA)
            break

# Teste autenticação
try:
    me = client.get_me()
    log(f"✅ Autenticado como @{me.data.username}", Fore.GREEN)
except Exception as e:
    log(f"❌ Erro autenticação: {e}", Fore.RED)
    exit()

schedule.every(1).minutes.do(executar_reposts)

log("🚀 Script iniciado! Teste em horário definido no script ou horários normais.", Fore.CYAN)
while True:
    schedule.run_pending()
    time.sleep(1)