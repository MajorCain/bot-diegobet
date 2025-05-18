import requests
import datetime
import asyncio
import telegram

# === CONFIGURAÇÕES ===
TELEGRAM_TOKEN = '7516769955:AAGGmyqQ5-jNtxuzVNXU3iSQrzS8p5adzTo'
TELEGRAM_CHAT_ID = '1306578324'
API_KEY_FOOTBALL_DATA = 'b391de2d45cf4c54a36d7ed7d6461dee'
API_KEY_ODDS = '22c4b502df2fa1cf1c3194223a04f724'
BASE_URL = 'https://api.football-data.org/v4/'
ODDS_URL = 'https://api.the-odds-api.com/v4/sports/soccer_epl/odds'  # Exemplo: EPL (Premier League)
HEADERS = {'X-Auth-Token': API_KEY_FOOTBALL_DATA}
LIGAS = ['PL', 'BSA', 'PD', 'BL1', 'SA', 'FL1', 'CL']

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
        if jogo["score"]["fullTime"]["home"] is None or jogo["score"]["fullTime"]["away"] is None:
            continue
        time_casa = jogo["homeTeam"]["id"]
        gols_time = jogo["score"]["fullTime"]["home"] if time_casa == codigo_time else jogo["score"]["fullTime"]["away"]
        gols += gols_time
        jogos += 1
    return gols / jogos if jogos > 0 else 0

def gerar_sugestao(gols_time1, gols_time2):
    media_total = gols_time1 + gols_time2
    sugestoes = []
    if media_total >= 2.5:
        sugestoes.append(("Mais de 2.5 gols", 2.5))
    elif media_total >= 2.0:
        sugestoes.append(("Mais de 1.5 gols", 1.5))
    else:
        sugestoes.append(("Menos de 2.5 gols", 2.5))
    return sugestoes

def get_odds(nome_time1, nome_time2, mercado_gol=2.5):
    # Aqui usaremos a Premier League como exemplo
    params = {
        'regions': 'eu',
        'markets': 'totals',
        'oddsFormat': 'decimal',
        'apiKey': API_KEY_ODDS
    }
    resp = requests.get(ODDS_URL, params=params)
    if resp.status_code != 200:
        return None

    odds_data = resp.json()
    for jogo in odds_data:
        if nome_time1.lower() in jogo['home_team'].lower() and nome_time2.lower() in jogo['away_team'].lower():
            for mercado in jogo['bookmakers'][0]['markets']:
                if mercado['key'] == 'totals':
                    for outcome in mercado['outcomes']:
                        if float(outcome['point']) == mercado_gol:
                            return outcome['price']
    return None

def calcular_valor_esperado(prob, odd):
    return (prob * odd) - 1

async def enviar_telegram(texto):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto, parse_mode='HTML')

async def main():
    texto_final = '<b>⚽ Sugestões de Apostas com Valor Esperado</b>\n\n'
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
            texto_final += f"📊 Média de Gols: {media_gols_1:.1f} x {media_gols_2:.1f}\n"

            for s, linha in sugestoes:
                prob_estimativa = (media_gols_1 + media_gols_2) / (linha + 0.1)
                prob_estimativa = min(prob_estimativa, 1.0)
                odd_real = get_odds(time1['name'], time2['name'], linha)
                if odd_real:
                    ev = calcular_valor_esperado(prob_estimativa, odd_real)
                    if ev > 0:
                        texto_final += f"💡 <b>{s}</b> @ <b>{odd_real}</b> | EV: <b>{ev:.2f}</b>\n"
                else:
                    texto_final += f"💡 <b>{s}</b> (sem odd disponível)\n"
            texto_final += "-" * 35 + "\n"

    if total_jogos == 0:
        texto_final += "⚠️ Nenhum jogo com estatísticas disponíveis encontrado."

    await enviar_telegram(texto_final)

# === EXECUTAR ===
asyncio.run(main())
