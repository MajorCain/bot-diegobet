import requests
import datetime
import asyncio
import telegram
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import pytz

# === CONFIGURAÇÃO ===
TELEGRAM_TOKEN = '7516769955:AAGGmyqQ5-jNtxuzVNXU3iSQrzS8p5adzTo'
TELEGRAM_CHAT_ID = '1306578324'
API_KEY = 'b391de2d45cf4c54a36d7ed7d6461dee'  # Football-Data.org
BASE_URL = 'https://api.football-data.org/v4/'
LIGAS = ['BSA', 'PD', 'BL1', 'SA', 'FL1', 'CL']
HEADERS = {'X-Auth-Token': API_KEY}

# === FUNÇÕES ===
def get_jogos_hoje(liga):
    hoje = datetime.datetime.now(pytz.timezone('Europe/Lisbon')).date()
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

def gerar_sugestao(gols1, gols2):
    total = gols1 + gols2
    if total >= 2.5:
        return "Mais de 2.5 gols"
    elif total >= 2.0:
        return "Mais de 1.5 gols"
    else:
        return "Menos de 2.5 gols"

def criar_imagem(jogos):
    largura, altura = 800, 100 + 100 * len(jogos)
    imagem = Image.new("RGB", (largura, altura), color=(30, 30, 30))
    draw = ImageDraw.Draw(imagem)
    try:
        fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
    except:
        fonte = ImageFont.load_default()
    draw.text((20, 20), "Sugestões de Aposta - Hoje", font=fonte, fill="white")
    y = 80
    for jogo in jogos:
        texto = f"{jogo['time1']} x {jogo['time2']} | {jogo['sugestao']}"
        draw.text((20, y), texto, font=fonte, fill="white")
        y += 100
    caminho = "sugestoes_apostas.png"
    imagem.save(caminho)
    return caminho

def criar_audio(texto):
    caminho = "sugestoes_apostas.mp3"
    tts = gTTS(texto, lang='pt')
    tts.save(caminho)
    return caminho

async def enviar_telegram(mensagem, imagem_path, audio_path):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem, parse_mode='HTML')
    await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=open(imagem_path, 'rb'))
    await bot.send_audio(chat_id=TELEGRAM_CHAT_ID, audio=open(audio_path, 'rb'))

async def main():
    texto_final = '<b>🔰 Sugestões de Apostas para Hoje</b>\n\n'
    jogos_info = []

    for liga in LIGAS:
        jogos = get_jogos_hoje(liga)
        for jogo in jogos:
            time1 = jogo["homeTeam"]
            time2 = jogo["awayTeam"]
            data = jogo["utcDate"][:16].replace("T", " ")
            media1 = get_estatisticas_time(time1["id"])
            media2 = get_estatisticas_time(time2["id"])
            if media1 is None or media2 is None:
                continue
            sugestao = gerar_sugestao(media1, media2)
            texto_final += f"<b>{time1['name']} vs {time2['name']}</b>\n"
            texto_final += f"📓 {data} | 🎽 Médias: {media1:.1f} x {media2:.1f}\n"
            texto_final += f"✨ Sugestão: {sugestao}\n\n"
            jogos_info.append({"time1": time1["name"], "time2": time2["name"], "sugestao": sugestao})

    if not jogos_info:
        texto_final += "⚠️ Nenhuma sugestão gerada."

    imagem = criar_imagem(jogos_info)
    texto_audio = "Sugestões de apostas do dia: " + ". ".join([f"{j['time1']} contra {j['time2']}, {j['sugestao']}" for j in jogos_info])
    audio = criar_audio(texto_audio)
    await enviar_telegram(texto_final, imagem, audio)

if __name__ == '__main__':
    asyncio.run(main())
