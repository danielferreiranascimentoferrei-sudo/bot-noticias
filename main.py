import requests
import schedule
import time
import json
from datetime import datetime

# =========================================
# CONFIGURAÇÕES
# =========================================

TOKEN = "8970558916:AAHqPrQ84zE-C_w7Ih_DfF_BWbuXfh2FdCM"

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

TEMPO_VERIFICACAO = 45

ARQUIVO_USUARIOS = "usuarios.json"

usuarios = {}

enviadas = []

ultimo_update = None

# =========================================
# MOEDAS VÁLIDAS
# =========================================

MOEDAS_VALIDAS = [
    "USD",
    "EUR",
    "GBP",
    "JPY",
    "BRL",
    "AUD",
    "CAD",
    "NZD"
]

# =========================================
# CARREGAR USUÁRIOS
# =========================================

def carregar_usuarios():

    global usuarios

    try:

        with open(
            ARQUIVO_USUARIOS,
            "r",
            encoding="utf-8"
        ) as f:

            usuarios = json.load(f)

    except:

        usuarios = {}

# =========================================
# SALVAR USUÁRIOS
# =========================================

def salvar_usuarios():

    with open(
        ARQUIVO_USUARIOS,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            usuarios,
            f,
            indent=4
        )

# =========================================
# ENVIAR MENSAGEM
# =========================================

def enviar_mensagem(chat_id, texto):

    url = (
        f"https://api.telegram.org/bot"
        f"{TOKEN}/sendMessage"
    )

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
# DETECTAR DISCURSO
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
# CRIAR USUÁRIO
# =========================================

def criar_usuario(chat_id):

    usuarios[str(chat_id)] = {

        "moedas": [
            "USD",
            "EUR",
            "GBP"
        ],

        "impactos": [
            "High"
        ],

        "minutos": 5,

        "low_usd_discurso": True
    }

    salvar_usuarios()

# =========================================
# COMANDOS
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
╔══════════════════╗
      📊 BOT ECONÔMICO
╚══════════════════╝

🚨 ALERTAS AUTOMÁTICOS
⏰ Notícias em tempo real
🔥 Filtro por impacto
💱 Filtro por moedas

━━━━━━━━━━━━━━━━━━

📌 COMANDOS

➕ /add USD
➖ /remove USD

🔥 /impact high
🔥 /impact medium
🔥 /impact low
🔥 /impact mediumhigh
🔥 /impact all

⏰ /time 5

📊 /status
📋 /list
"""

        enviar_mensagem(chat_id, mensagem)

    # =====================================
    # LISTA
    # =====================================

    elif comando == "/list":

        mensagem = """
╔══════════════════╗
       💱 MOEDAS
╚══════════════════╝

🇺🇸 USD
🇪🇺 EUR
🇬🇧 GBP
🇯🇵 JPY
🇧🇷 BRL
🇦🇺 AUD
🇨🇦 CAD
🇳🇿 NZD
"""

        enviar_mensagem(chat_id, mensagem)

    # =====================================
    # ADD
    # =====================================

    elif comando == "/add":

        if len(partes) < 2:

            enviar_mensagem(
                chat_id,
                "❌ Use:\n/add USD"
            )

            return

        moeda = partes[1].upper()

        if moeda not in MOEDAS_VALIDAS:

            enviar_mensagem(
                chat_id,
                f"""
❌ MOEDA INVÁLIDA

Moeda digitada:
{moeda}

Use /list para ver as disponíveis.
"""
            )

            return

        if moeda not in usuarios[chat_id]["moedas"]:

            usuarios[chat_id]["moedas"].append(
                moeda
            )

            salvar_usuarios()

            enviar_mensagem(
                chat_id,
                f"""
✅ MOEDA ADICIONADA

💱 {moeda}

Agora você receberá
notícias desta moeda.
"""
            )

        else:

            enviar_mensagem(
                chat_id,
                f"⚠️ {moeda} já está ativa."
            )

    # =====================================
    # REMOVE
    # =====================================

    elif comando == "/remove":

        if len(partes) < 2:

            enviar_mensagem(
                chat_id,
                "❌ Use:\n/remove USD"
            )

            return

        moeda = partes[1].upper()

        if moeda in usuarios[chat_id]["moedas"]:

            usuarios[chat_id]["moedas"].remove(
                moeda
            )

            salvar_usuarios()

            enviar_mensagem(
                chat_id,
                f"""
❌ MOEDA REMOVIDA

💱 {moeda}

Você não receberá mais
alertas desta moeda.
"""
            )

        else:

            enviar_mensagem(
                chat_id,
                f"⚠️ {moeda} não está ativa."
            )

    # =====================================
    # TIME
    # =====================================

    elif comando == "/time":

        if len(partes) < 2:

            enviar_mensagem(
                chat_id,
                "❌ Use:\n/time 5"
            )

            return

        minutos = int(partes[1])

        usuarios[chat_id]["minutos"] = minutos

        salvar_usuarios()

        enviar_mensagem(
            chat_id,
            f"""
⏰ TEMPO ALTERADO

Novo alerta:
{minutos} minutos antes.
"""
        )

    # =====================================
    # IMPACT
    # =====================================

    elif comando == "/impact":

        if len(partes) < 2:

            enviar_mensagem(
                chat_id,
                """
❌ Use:

/impact high
/impact medium
/impact low
/impact mediumhigh
/impact all
"""
            )

            return

        impacto = partes[1].lower()

        if impacto == "high":

            usuarios[chat_id]["impactos"] = [
                "High"
            ]

        elif impacto == "medium":

            usuarios[chat_id]["impactos"] = [
                "Medium"
            ]

        elif impacto == "low":

            usuarios[chat_id]["impactos"] = [
                "Low"
            ]

        elif impacto == "mediumhigh":

            usuarios[chat_id]["impactos"] = [
                "Medium",
                "High"
            ]

        elif impacto == "all":

            usuarios[chat_id]["impactos"] = [
                "Low",
                "Medium",
                "High"
            ]

        else:

            enviar_mensagem(
                chat_id,
                """
❌ IMPACTO INVÁLIDO

Use:

high
medium
low
mediumhigh
all
"""
            )

            return

        salvar_usuarios()

        impactos = ", ".join(
            usuarios[chat_id]["impactos"]
        )

        enviar_mensagem(
            chat_id,
            f"""
🔥 IMPACTOS ATUALIZADOS

Ativos:
{impactos}
"""
        )

    # =====================================
    # STATUS
    # =====================================

    elif comando == "/status":

        config = usuarios[chat_id]

        moedas = ", ".join(
            config["moedas"]
        )

        impactos = ", ".join(
            config["impactos"]
        )

        mensagem = f"""
╔══════════════════╗
      📊 STATUS
╚══════════════════╝

💱 MOEDAS
{moedas}

━━━━━━━━━━━━━━━━━━

🔥 IMPACTOS
{impactos}

━━━━━━━━━━━━━━━━━━

⏰ ALERTA
{config['minutos']} min antes
"""

        enviar_mensagem(
            chat_id,
            mensagem
        )

# =========================================
# PEGAR COMANDOS TELEGRAM
# =========================================

def verificar_comandos():

    global ultimo_update

    url = (
        f"https://api.telegram.org/bot"
        f"{TOKEN}/getUpdates"
    )

    try:

        resposta = requests.get(
            url,
            timeout=10
        ).json()

        for update in resposta["result"]:

            update_id = update["update_id"]

            if (
                ultimo_update
                and update_id <= ultimo_update
            ):
                continue

            ultimo_update = update_id

            if "message" not in update:
                continue

            mensagem = update["message"]

            chat_id = mensagem["chat"]["id"]

            texto = mensagem.get("text", "")

            if texto.startswith("/"):

                processar_comando(
                    chat_id,
                    texto
                )

    except Exception as erro:

        print("Erro comandos:")
        print(erro)

# =========================================
# VERIFICAR NOTÍCIAS
# =========================================

def verificar_noticias():

    global enviadas

    print("Verificando notícias...")

    try:

        resposta = requests.get(
            URL,
            timeout=10
        )

        if resposta.status_code != 200:

            print("Erro API:")
            print(resposta.status_code)

            return

        if not resposta.text.strip():

            print("API retornou vazia")

            return

        try:

            noticias = resposta.json()

        except Exception as erro:

            print("Erro ao converter JSON:")
            print(erro)

            return

        agora = datetime.now().astimezone()

        for noticia in noticias:

            moeda = noticia.get("country")

            titulo = noticia.get("title")

            impacto = noticia.get("impact")

            data_noticia = noticia.get("date")

            horario = datetime.fromisoformat(
                data_noticia
            )

            discurso = eh_discurso(titulo)

            for chat_id, config in usuarios.items():

                if moeda not in config["moedas"]:
                    continue

                permitido = (
                    impacto in config["impactos"]
                )

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

                chave = (
                    f"{chat_id}-"
                    f"{titulo}-"
                    f"{data_noticia}"
                )

                if (
                    0 <= diferenca <= config["minutos"]
                    and chave not in enviadas
                ):

                    tipo = (
                        "🗣️ Discurso"
                        if discurso
                        else "📊 Indicador"
                    )

                    mensagem = f"""
╔══════════════════╗
   🚨 ALERTA ECONÔMICO
╚══════════════════╝

💱 ATIVO
{moeda}

📌 TIPO
{tipo}

📰 EVENTO
{titulo}

🔥 IMPACTO
{impacto}

📅 DATA
{horario.strftime('%d/%m/%Y')}

⏰ HORÁRIO
{horario.strftime('%H:%M')}

⌛ FALTA
{round(diferenca)} minutos

━━━━━━━━━━━━━━━━━━
⚠️ Prepare-se antes da notícia.
"""

                    enviar_mensagem(
                        chat_id,
                        mensagem
                    )

                    print(
                        f"Mensagem enviada "
                        f"para {chat_id}"
                    )

                    enviadas.append(chave)

                    time.sleep(1)

    except Exception as erro:

        print("Erro notícias:")
        print(erro)

# =========================================
# INICIAR
# =========================================

carregar_usuarios()

schedule.every(
    TEMPO_VERIFICACAO
).seconds.do(
    verificar_noticias
)

schedule.every(5).seconds.do(
    verificar_comandos
)

print("BOT INICIADO")

while True:

    schedule.run_pending()

    time.sleep(0.5)