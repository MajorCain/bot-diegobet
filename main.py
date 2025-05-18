import requests
import datetime
import asyncio
from telegram import Bot

# === CONFIGURAÇÃO ===
TELEGRAM_TOKEN = os.getenv('7516769955:AAGGmyqQ5-jNtxuzVNXU3iSQrzS8p5adzTo') # substitua pelo token real do seu bot
TELEGRAM_CHAT_ID = os.getenv('1306578324')    # seu chat id
API_KEY = os.getenv('b391de2d45cf4c54a36d7ed7d6461dee')  # Football-Data.org
BASE_URL = 'https://api.football-data.org/v4/'

HEADERS = {
    'X-Auth-Token': API_KEY
}

LIGAS = ['BSA', 'PD', 'BL1', 'SA', 'FL1', 'CL', 'PPL', 'DED', 'ELC']

# === FUNÇÕES ===

def get_jogos_hoje(liga):
    hoje = datetime.datetime.now().date()
    amanha = hoje + datetime.timedelta(days=1)
    url = f"{BASE_URL}competitions/{liga}/matches?dateFrom={hoje}&dateTo={amanha}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        return resp.json().get("matches", [])
    return []

def get_estatisticas_time(codigo_time):
    url = f"{BASE_URL}teams/{codigo_time}/matches?status=FINISHED&limit=5"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return None

    partidas = resp.json().get("matches", [])
    gols = 0
    jogos = 0
    for jogo in partidas:
        time_casa = jogo["homeTeam"]["id"]
        gols_time = jogo["score"]["fullTime"]["home"] if time_casa == codigo_time else jogo["score"]["fullTime"]["away"]
        gols += gols_time if gols_time is not None else 0
        jogos += 1

    return gols / jogos if jogos > 0 else 0

def gerar_sugestao(gols_time1, gols_time2):
    media_total = gols_time1 + gols_time2
    sugestoes = []
    if media_total >= 2.5:
        sugestoes.append("Mais de 2.5 gols")
    elif media_total >= 2.0:
        sugestoes.append("Mais de 1.5 gols")
    else:
        sugestoes.append("Menos de 2.5 gols")
    return sugestoes

async def enviar_telegram(texto):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto, parse_mode='HTML')

async def main():
    texto_final = '<b>🔰 Sugestões de Apostas Pré-Jogo (Próximas 24h)</b>\n\n'
    total_jogos = 0

    for liga in LIGAS:
        jogos = get_jogos_hoje(liga)
        if not jogos:
            continue

        for jogo in jogos:
            time1 = jogo["homeTeam"]
            time2 = jogo["awayTeam"]
            data = jogo["utcDate"][:16].replace("T", " ")

            media_gols_1 = get_estatisticas_time(time1["id"])
            media_gols_2 = get_estatisticas_time(time2["id"])

            if media_gols_1 is None or media_gols_2 is None:
                continue

            sugestoes = gerar_sugestao(media_gols_1, media_gols_2)
            total_jogos += 1

            texto_final += f"<b>{time1['name']} vs {time2['name']}</b>\n"
            texto_final += f"📅 {data}\n"
            texto_final += f"🏀 Média de Gols: {media_gols_1:.1f} x {media_gols_2:.1f}\n"
            texto_final += f"🔢 Sugestão: {', '.join(sugestoes)}\n"
            texto_final += "-"*32 + "\n"

    if total_jogos == 0:
        texto_final += "⚠️ Nenhum jogo com estatísticas disponíveis encontrado."

    await enviar_telegram(texto_final)

if __name__ == '__main__':
    asyncio.run(main())
