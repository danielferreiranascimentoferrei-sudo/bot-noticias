import requests
import schedule
import time
import json
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = "8970558916:AAHqPrQ84zE-C_w7Ih_DfF_BWbuXfh2FdCM"

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

TEMPO_VERIFICACAO = 60

ARQUIVO_USUARIOS = "usuarios.json"
ARQUIVO_ENVIADAS = "enviadas.json"

usuarios = {}
enviadas = []
ultimo_update = None

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")

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


def carregar_enviadas():

    global enviadas

    try:

        with open(
            ARQUIVO_ENVIADAS,
            "r",
            encoding="utf-8"
        ) as f:

            enviadas = json.load(f)

    except:

        enviadas = []


def salvar_enviadas():

    with open(
        ARQUIVO_ENVIADAS,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            enviadas,
            f,
            indent=4
        )


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


def avisar_todos(texto):

    for chat_id in usuarios.keys():

        enviar_mensagem(
            chat_id,
            texto
        )

        time.sleep(0.5)


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

        "minutos": 5
    }

    salvar_usuarios()


def processar_comando(chat_id, texto):

    chat_id = str(chat_id)

    if chat_id not in usuarios:

        criar_usuario(chat_id)

    partes = texto.split()

    comando = partes[0].lower()

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

        enviar_mensagem(
            chat_id,
            mensagem
        )

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

        enviar_mensagem(
            chat_id,
            mensagem
        )

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
❌ Moeda inválida:
{moeda}

Use /list
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
                f"✅ {moeda} adicionada"
            )

        else:

            enviar_mensagem(
                chat_id,
                f"⚠️ {moeda} já está ativa."
            )

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
                f"❌ {moeda} removida"
            )

        else:

            enviar_mensagem(
                chat_id,
                f"⚠️ {moeda} não está ativa."
            )

    elif comando == "/time":

        if len(partes) < 2:

            enviar_mensagem(
                chat_id,
                "❌ Use:\n/time 5"
            )

            return

        try:

            minutos = int(partes[1])

        except:

            enviar_mensagem(
                chat_id,
                "❌ Número inválido"
            )

            return

        usuarios[chat_id]["minutos"] = minutos

        salvar_usuarios()

        enviar_mensagem(
            chat_id,
            f"""
⏰ Tempo alterado

Novo tempo:
{minutos} minutos
"""
        )

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
                "❌ Impacto inválido"
            )

            return

        salvar_usuarios()

        impactos = ", ".join(
            usuarios[chat_id]["impactos"]
        )

        enviar_mensagem(
            chat_id,
            f"""
🔥 Impactos ativos

{impactos}
"""
        )

    elif comando == "/status":

        config = usuarios[chat_id]

        mensagem = f"""
╔══════════════════╗
      📊 STATUS
╚══════════════════╝

💱 MOEDAS
{', '.join(config['moedas'])}

━━━━━━━━━━━━━━━━━━

🔥 IMPACTOS
{', '.join(config['impactos'])}

━━━━━━━━━━━━━━━━━━

⏰ ALERTA
{config['minutos']} min antes
"""

        enviar_mensagem(
            chat_id,
            mensagem
        )


def limpar_updates_antigos():

    global ultimo_update

    try:

        url = (
            f"https://api.telegram.org/bot"
            f"{TOKEN}/getUpdates"
        )

        resposta = requests.get(
            url,
            timeout=10
        ).json()

        if not resposta.get("ok"):

            print("Erro Telegram:")

            print(resposta)

            return

        resultados = resposta.get(
            "result",
            []
        )

        if resultados:

            ultimo_update = resultados[-1][
                "update_id"
            ]

        print(
            "Mensagens antigas ignoradas."
        )

    except Exception as erro:

        print(
            "Erro ao limpar mensagens:"
        )

        print(erro)


def verificar_comandos():

    global ultimo_update

    url = (
        f"https://api.telegram.org/bot"
        f"{TOKEN}/getUpdates"
    )

    try:

        params = {}

        if ultimo_update is not None:

            params["offset"] = (
                ultimo_update + 1
            )

        resposta = requests.get(
            url,
            params=params,
            timeout=10
        ).json()

        if not resposta.get("ok"):

            print("Erro Telegram:")

            print(resposta)

            return

        resultados = resposta.get(
            "result",
            []
        )

        for update in resultados:

            update_id = update[
                "update_id"
            ]

            ultimo_update = update_id

            if "message" not in update:
                continue

            mensagem = update["message"]

            chat_id = mensagem["chat"]["id"]

            texto = mensagem.get(
                "text",
                ""
            )

            if texto.startswith("/"):

                processar_comando(
                    chat_id,
                    texto
                )

    except Exception as erro:

        print("Erro comandos:")

        print(erro)


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

            print(
                resposta.status_code
            )

            return

        if not resposta.text.strip():

            print("API vazia")

            return

        try:

            noticias = resposta.json()

        except Exception as erro:

            print("Erro JSON:")

            print(erro)

            return

        print(
            f"Quantidade notícias: "
            f"{len(noticias)}"
        )

        agora = datetime.now(
            FUSO_BRASIL
        )

        for noticia in noticias:

            moeda = noticia.get(
                "country"
            )

            titulo = noticia.get(
                "title"
            )

            impacto = noticia.get(
                "impact"
            )

            data_noticia = noticia.get(
                "date"
            )

            print(
                f"{moeda} | "
                f"{impacto} | "
                f"{titulo}"
            )

            horario = datetime.fromisoformat(
                data_noticia
            )

            horario = horario.astimezone(
                FUSO_BRASIL
            )

            discurso = eh_discurso(
                titulo
            )

            for chat_id, config in usuarios.items():

                if moeda not in config[
                    "moedas"
                ]:
                    continue

                if impacto not in config[
                    "impactos"
                ]:
                    continue

                diferenca = (
                    horario - agora
                ).total_seconds() / 60

                chave = (
                    f"{chat_id}-"
                    f"{titulo}-"
                    f"{data_noticia}"
                )

                if chave in enviadas:
                    continue

                # TESTE:
                # envia qualquer notícia futura

                if diferenca > 0:

                    tipo = (
                        "🗣️ Discurso"
                        if discurso
                        else "📊 Indicador"
                    )

                    mensagem = f"""
╔══════════════════╗
   🚨 TESTE NOTÍCIA
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

⏰ HORÁRIO BRASÍLIA
{horario.strftime('%H:%M')}

⌛ FALTA
{round(diferenca)} minutos
"""

                    enviar_mensagem(
                        chat_id,
                        mensagem
                    )

                    print(
                        f"Mensagem enviada "
                        f"para {chat_id}"
                    )

                    enviadas.append(
                        chave
                    )

                    salvar_enviadas()

                    time.sleep(1)

    except Exception as erro:

        print("Erro notícias:")

        print(erro)


carregar_usuarios()

carregar_enviadas()

limpar_updates_antigos()

avisar_todos(
    "✅ BOT FUNCIONANDO"
)

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