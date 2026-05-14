import requests
import schedule
import time
import json
from datetime import datetime

# =========================================
# CONFIGURAÇÕES PRINCIPAIS
# =========================================

TOKEN = "8970558916:AAHqPrQ84zE-C_w7Ih_DfF_BWbuXfh2FdCM"

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

TEMPO_VERIFICACAO = 15

usuarios = {}

enviadas = []

ultimo_update = None

# =========================================
# BANCO LOCAL JSON
# =========================================

ARQUIVO_USUARIOS = "usuarios.json"


def carregar_usuarios():

    global usuarios

    try:

        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:

            usuarios = json.load(f)

    except:

        usuarios = {}


def salvar_usuarios():

    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:

        json.dump(usuarios, f, indent=4)


carregar_usuarios()

# =========================================
# TELEGRAM API
# =========================================


def enviar_mensagem(chat_id, texto):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    dados = {
        "chat_id": chat_id,
        "text": texto
    }

    try:

        requests.post(
            url,
            data=dados,
            timeout=10
        )

    except Exception as erro:

        print("Erro Telegram:")
        print(erro)

# =========================================
# DISCURSO
# =========================================


def eh_discurso(titulo):

    palavras = [
        "speech",
        "speaks",
        "statement",
        "testimony",
        "conference",
        "press",
        "fomc"
    ]

    titulo = titulo.lower()

    for palavra in palavras:

        if palavra in titulo:
            return True

    return False

# =========================================
# CONFIG USUÁRIO PADRÃO
# =========================================


def criar_usuario(chat_id):

    usuarios[str(chat_id)] = {
        "moedas": [
            "USD",
            "EUR",
            "GBP"
        ],
        "impactos": [
            "Medium",
            "High"
        ],
        "minutos": 5,
        "low_usd_discurso": True
    }

    salvar_usuarios()

# =========================================
# COMANDOS TELEGRAM
# =========================================


def processar_comando(chat_id, texto):

    chat_id = str(chat_id)

    if chat_id not in usuarios:
        criar_usuario(chat_id)

    partes = texto.split()

    comando = partes[0].lower()

    # =====================================
    # START
    # =====================================

    if comando == "/start":

        mensagem = """
🤖 BOT DE NOTÍCIAS ECONÔMICAS

COMANDOS:

/add USD
/remove USD

/impact high
/impact medium
/impact low

/time 5

/status

/list
"""

        enviar_mensagem(chat_id, mensagem)

    # =====================================
    # LISTAR MOEDAS
    # =====================================

    elif comando == "/list":

        enviar_mensagem(
            chat_id,
            """
MOEDAS DISPONÍVEIS:

USD
EUR
GBP
JPY
BRL
AUD
CAD
NZD
"""
        )

    # =====================================
    # ADICIONAR MOEDA
    # =====================================

    elif comando == "/add":

        if len(partes) < 2:

            enviar_mensagem(
                chat_id,
                "Use: /add USD"
            )

            return

        moeda = partes[1].upper()

        if moeda not in usuarios[chat_id]["moedas"]:

            usuarios[chat_id]["moedas"].append(moeda)

            salvar_usuarios()

            enviar_mensagem(
                chat_id,
                f"✅ {moeda} adicionada"
            )

    # =====================================
    # REMOVER MOEDA
    # =====================================

    elif comando == "/remove":

        if len(partes) < 2:

            enviar_mensagem(
                chat_id,
                "Use: /remove USD"
            )

            return

        moeda = partes[1].upper()

        if moeda in usuarios[chat_id]["moedas"]:

            usuarios[chat_id]["moedas"].remove(moeda)

            salvar_usuarios()

            enviar_mensagem(
                chat_id,
                f"❌ {moeda} removida"
            )

    # =====================================
    # TEMPO
    # =====================================

    elif comando == "/time":

        if len(partes) < 2:

            enviar_mensagem(
                chat_id,
                "Use: /time 5"
            )

            return

        minutos = int(partes[1])

        usuarios[chat_id]["minutos"] = minutos

        salvar_usuarios()

        enviar_mensagem(
            chat_id,
            f"⏰ Tempo alterado para {minutos} minutos"
        )

    # =====================================
    # IMPACTO
    # =====================================

    elif comando == "/impact":

        if len(partes) < 2:

            enviar_mensagem(
                chat_id,
                "Use: /impact high"
            )

            return

        impacto = partes[1].capitalize()

        if impacto == "High":
            usuarios[chat_id]["impactos"] = ["High"]

        elif impacto == "Medium":
            usuarios[chat_id]["impactos"] = [
                "Medium",
                "High"
            ]

        elif impacto == "Low":
            usuarios[chat_id]["impactos"] = [
                "Low",
                "Medium",
                "High"
            ]

        salvar_usuarios()

        enviar_mensagem(
            chat_id,
            f"🔥 Impactos alterados para: {usuarios[chat_id]['impactos']}"
        )

    # =====================================
    # STATUS
    # =====================================

    elif comando == "/status":

        config = usuarios[chat_id]

        mensagem = f"""
📊 SUAS CONFIGURAÇÕES

💱 Moedas:
{', '.join(config['moedas'])}

🔥 Impactos:
{', '.join(config['impactos'])}

⏰ Aviso:
{config['minutos']} minutos antes

🗣️ Low USD discurso:
{config['low_usd_discurso']}
"""

        enviar_mensagem(chat_id, mensagem)

# =========================================
# PEGAR MENSAGENS TELEGRAM
# =========================================


def verificar_comandos():

    global ultimo_update

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

    try:

        resposta = requests.get(url).json()

        for update in resposta["result"]:

            update_id = update["update_id"]

            if ultimo_update and update_id <= ultimo_update:
                continue

            ultimo_update = update_id

            if "message" not in update:
                continue

            mensagem = update["message"]

            chat_id = mensagem["chat"]["id"]

            texto = mensagem.get("text", "")

            if texto.startswith("/"):

                processar_comando(chat_id, texto)

    except Exception as erro:

        print("Erro comandos:")
        print(erro)

# =========================================
# NOTÍCIAS
# =========================================


def verificar_noticias():

    global enviadas

    print("Verificando notícias...")

    try:

        resposta = requests.get(URL)

        noticias = resposta.json()

        agora = datetime.now().astimezone()

        for noticia in noticias:

            moeda = noticia.get("country")

            titulo = noticia.get("title")

            impacto = noticia.get("impact")

            data_noticia = noticia.get("date")

            horario = datetime.fromisoformat(data_noticia)

            discurso = eh_discurso(titulo)

            for chat_id, config in usuarios.items():

                if moeda not in config["moedas"]:
                    continue

                permitido = impacto in config["impactos"]

                if (
                    impacto == "Low"
                    and moeda == "USD"
                    and discurso
                    and config["low_usd_discurso"]
                ):
                    permitido = True

                if not permitido:
                    continue

                diferenca = (
                    horario - agora
                ).total_seconds() / 60

                chave = f"{chat_id}-{titulo}-{data_noticia}"

                if (
                    0 <= diferenca <= config["minutos"]
                    and chave not in enviadas
                ):

                    tipo = "🗣️ Discurso" if discurso else "📊 Indicador"

                    mensagem = f"""
🚨 ALERTA ECONÔMICO

💱 Moeda:
{moeda}

📌 Tipo:
{tipo}

📰 Evento:
{titulo}

🔥 Impacto:
{impacto}

📅 Data:
{horario.strftime('%d/%m/%Y')}

⏰ Horário:
{horario.strftime('%H:%M')}

⌛ Começa em:
{round(diferenca)} minutos
"""

                    enviar_mensagem(chat_id, mensagem)

                    print(f"Mensagem enviada para {chat_id}")

                    enviadas.append(chave)

                    time.sleep(1)

    except Exception as erro:

        print("Erro notícias:")
        print(erro)

# =========================================
# LOOP
# =========================================

schedule.every(TEMPO_VERIFICACAO).seconds.do(
    verificar_noticias
)

schedule.every(5).seconds.do(
    verificar_comandos
)

print("BOT INICIADO")

while True:

    schedule.run_pending()

    time.sleep(0.5)