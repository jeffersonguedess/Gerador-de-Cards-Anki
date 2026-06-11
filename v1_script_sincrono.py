from builtins import print

import requests
import json
from openai import OpenAI

# ================= CONFIGURAÇÕES =================
OPENROUTER_API_KEY = "SUA_CHAVE_OPENROUTER_AQUI"
ANKI_CONNECT_URL = "http://localhost:8765"
DECK_NAME = "Linux::Comandos"
# =================================================

# Ajustado para minúsculo para alinhar com o resto do script
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

def criar_baralho_se_nao_existir():
    """ Garante que o baralho Linux::Comandos exista no Anki """
    payload = {
        "action": "createDeck",
        "version": 6,
        "params": {"deck": DECK_NAME}
    }
    try:
        requests.post(ANKI_CONNECT_URL, json=payload)
    except:
        pass

def gerar_cards_com_openrouter(texto_estudo):
    """ Envia o seu resumo para o DeepSeek via OpenRouter e extrai os cards """
    prompt_sistema = """
    Você é um assistente especialista em concursos de TI e criação de flashcards para o Anki.
    Seu objetivo é receber anotações de estudo e transformá-las em flashcards no formato de Omissão de Palavras (Cloze Deletion).
    
    Regras estritas:
    1. Esconda apenas comandos, parâmetros, diretórios ou termos técnicos cruciais usando {{c1::termo}}.
    2. Seja extremamente curto, direto e textual. Não use decorações ou explicações longas.
    3. Você DEVE responder obrigatoriamente com um OBJETO JSON válido contendo uma chave chamada "cards".
    
    Exemplo de saída esperada:
    {
        "cards": [
            {"texto": "O comando {{c1::grep -i}} realiza buscas ignorando maiúsculas e minúsculas."},
            {"texto": "As tentativas de login fracassadas são salvas no arquivo {{c1::btmp}}."}
        ]
    }
    """

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat", 
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Transforme estas notas em cards Anki:\n\n{texto_estudo}"}
            ],
            temperature=0.2,
            response_format={'type': 'json_object'}
        )
        resultado_json = json.loads(response.choices[0].message.content)
        return resultado_json.get("cards", [])
    except Exception as e:
        print(f"❌ Erro na API do OpenRouter: {e}")
        return []

def enviar_para_o_anki(card_texto):
    """ Injeta o card formatado em português direto no Anki """
    criar_baralho_se_nao_existir()
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": DECK_NAME,
                "modelName": "Omissão de palavras",
                "fields": {
                    "Texto": card_texto
                },
                "tags": ["linux", "openrouter_manual"]
            }
        }
    }
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload)
        resultado = response.json()
        if resultado.get("error"):
            print(f"❌ Erro no AnkiConnect: {resultado['error']}")
        else:
            print(f"✅ Card injetado com sucesso! ID: {resultado['result']}")
    except requests.exceptions.ConnectionError:
        print("❌ Erro: O Anki não está aberto.")

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    
    suas_anotacoes = """
    O comando cd /var/log entra na pasta de logs.
    Ao utilizar o pwd confirmo que estou na pasta correta.
    O ls vai mostrar os arquivos wtmp (logins de sucesso) e btmp (tentativas falhas).
    O comando tail -f monitora arquivos em tempo real.
    O comando grep -i faz buscas case-insensitive.
    """
    
    print("🤖 Chamando OpenRouter (DeepSeek) para processar seu resumo...")
    lista_de_cards = gerar_cards_com_openrouter(suas_anotacoes)
    
    if lista_de_cards:
        print(f"📥 Foram gerados {len(lista_de_cards)} cards pela IA. Injetando no Anki...")
        for card in lista_de_cards:
            if "texto" in card:
                enviar_para_o_anki(card["texto"])
    else:
        print("⚠ Nenhum card pôde ser gerado.")