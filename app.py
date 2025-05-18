from flask import Flask
import datetime
import telegram
import threading

app = Flask(__name__)

TELEGRAM_TOKEN = '7516769955:AAGGmyqQ5-jNtxuzVNXU3iSQrzS8p5adzTo'
TELEGRAM_CHAT_ID = '1306578324'

bot = telegram.Bot(token=TELEGRAM_TOKEN)

ultima_execucao = None

def enviar_sugestoes():
    global ultima_execucao
    hoje = datetime.date.today()
    if ultima_execucao == hoje:
        print("Já enviou hoje, ignorando...")
        return "Já enviou hoje"
    
    texto_final = f"🔰 Mensagem de teste enviada em {datetime.datetime.now()}"
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto_final, parse_mode='HTML')
    ultima_execucao = hoje
    return "Mensagem enviada com sucesso"

@app.route('/run-bot', methods=['GET'])
def run_bot():
    thread = threading.Thread(target=enviar_sugestoes)
    thread.start()
    return "Bot executado", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
