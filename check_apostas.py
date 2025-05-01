import requests
import telegram
from datetime import datetime

# === CONFIGURAÇÕES ===
API_KEY = '2d1e4a17ab7e433f2a5fa832babb0a45'
URL = 'https://v3.football.api-sports.io/fixtures?date=' + datetime.today().strftime('%Y-%m-%d')
HEADERS = {'x-apisports-key': API_KEY}
TELEGRAM_TOKEN = '7516769955:AAGGmyqQ5-jNtxuzVNXU3iSQrzS8p5adzTo'
CHAT_ID = '@DiegoBetAlertBot'

# === FUNÇÕES ===
def buscar_jogos():
    resposta = requests.get(URL, headers=HEADERS)
    return resposta.json()

def analisar_jogos(jogos):
    mensagens = []
    for jogo in jogos['response']:
        partida = jogo['teams']['home']['name'] + ' x ' + jogo['teams']['away']['name']
        liga = jogo['league']['name']
        if liga in ['Serie A', 'Copa do Brasil', 'Libertadores', 'Champions League']:
            mensagens.append(f"⚽ Oportunidade: {partida} ({liga})\nEstude o mercado de gols e escanteios!")
    return mensagens

def enviar_mensagens(mensagens):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    for msg in mensagens:
        bot.send_message(chat_id=CHAT_ID, text=msg)

# === EXECUÇÃO ===
jogos = buscar_jogos()
mensagens = analisar_jogos(jogos)
enviar_mensagens(mensagens)
