# repost_one_run.py - GitHub Actions (usa secrets via env)
import tweepy
import time
import random
import logging
import os
from datetime import datetime
import pytz

# ===========================
# 🔧 MODO TESTE DE HORÁRIO
# ===========================
TEST_MODE = False              # ← MUDE PARA False depois
TEST_HORARIO = "23:38"        # ← ESCOLHA A HORA DE TESTE
# ===========================

# Keys via GitHub Secrets (env)
BEARER_TOKEN = os.environ['BEARER_TOKEN']
API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

# URLs por período
DAYTIME_URLS = [
    'https://x.com/lrdirdr/status/2019077171453608185',
    'https://x.com/lrdirdr/status/2017243968669442480'
]

NIGHTTIME_URLS = [
    'https://x.com/lrdirdr/status/2020189301695246359'
]

HORARIOS_POR_DIA = {
    'monday': ['01:00', '12:00', '17:00'],
    'tuesday': ['01:00', '12:00'],
    'wednesday': ['15:00', '23:00'],
    'thursday': ['13:00', '23:00'],
    'friday': ['15:00', '23:00'],
    'saturday': ['12:00', '23:00', '23:38'],
    'sunday': ['11:00', '17:00', '21:00']
}

DAYTIME_HORARIOS = {'11:00','12:00','13:00','14:00','15:00','17:00'}
NIGHTTIME_HORARIOS = {'00:00','01:00','21:00','23:00', '23:38'}

logging.basicConfig(filename='/tmp/repost_log.txt', level=logging.INFO)
TZ = pytz.timezone('America/Sao_Paulo')

client = tweepy.Client(
    bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

def log(msg):
    timestamp = datetime.now(TZ).strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")
    logging.info(msg)

def extrair_tweet_id(url):
    return url.split('/')[-1].split('?')[0]

def processar_reposts(urls):
    for i, url in enumerate(urls):
        tweet_id = extrair_tweet_id(url)
        log(f"🔄 URL {i+1}: {url}")
        try:
            client.unretweet(tweet_id)
            time.sleep(random.uniform(1, 3))
            log("✅ Unretweet OK")
        except:
            log("ℹ️ Sem repost anterior")
        time.sleep(random.uniform(5, 15))
        client.retweet(tweet_id)
        log(f"🔥 Repost: {tweet_id}")
        time.sleep(random.uniform(30, 60))

try:
    me = client.get_me()
    log(f"✅ Autenticado: @{me.data.username}")

    agora = datetime.now(TZ).strftime('%H:%M')
    dia_semana = datetime.now(TZ).strftime('%A').lower()
    horarios_real = HORARIOS_POR_DIA.get(dia_semana, [])

    # 👉 adiciona horario de teste
    if TEST_MODE:
        horarios_real = horarios_real + [TEST_HORARIO]
        log(f"🧪 TESTE: adicionando horário {TEST_HORARIO}")

    executou = False
    for horario in horarios_real:
        if agora == horario:
            log(f"🕐 Horário válido: {horario} ({dia_semana})")

            if horario in DAYTIME_HORARIOS:
                processar_reposts(DAYTIME_URLS)
                log("☀️ Diurnas concluídas")
            else:
                processar_reposts(NIGHTTIME_URLS)
                log("🌙 Noturnas concluídas")

            executou = True
            break

    if not executou:
        log(f"ℹ️ Sem horário agora: {agora}. Aguardando cron...")
except Exception as e:
    log(f"❌ Erro: {e}")




