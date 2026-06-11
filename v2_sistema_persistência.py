import requests
import json
import os
import hashlib
from openai import OpenAI

# ==================== CONFIGURAÇÕES ====================
OPENROUTER_API_KEY = "SUA_CHAVE_OPENROUTER_AQUI"
NOTION_TOKEN = "SEU_SECRET_DO_NOTION_AQUI"
NOTION_PAGE_ID = "O_ID_DA_SUA_PAGINA_AQUI"

ANKI_CONNECT_URL = "http://localhost:8765"
DECK_NAME = "Linux::Comandos"
HISTORY_FILE = "historico_cards.txt"
# =======================================================

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

def carregar_historico() -> set:
    """ Carrega os hashes dos blocos já processados para evitar duplicados """
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(linha.strip() for list_item in f if (linha := list_item.strip()))

def salvar_no_historico(bloco_hash: str):
    """ Grava o hash do novo bloco processado no ficheiro de histórico """
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{bloco_hash}\n")

def extrair_texto_do_bloco(block: dict) -> str:
    """ Extrai o texto limpo de quase qualquer tipo de bloco do Notion """
    block_type = block.get("type")
    if not block_type:
        return ""
    
    conteudo_bloco = block.get(block_type)
    if isinstance(conteudo_bloco, dict) and "rich_text" in conteudo_bloco:
        rich_text = conteudo_bloco["rich_text"]
        return "".join([texto.get("plain_text", "") for texto in rich_text]).strip()
    return ""

def ler_textos_novos_do_notion() -> list:
    """ Conecta à API do Notion e traz apenas as linhas que ainda não viraram cards """
    print("📖 A aceder à sua página do Notion...")
    url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    historico = carregar_historico()
    blocos_novos = []
    has_more = True
    start_cursor = None

    try:
        while has_more:
            params = {"page_size": 100}
            if start_cursor:
                params["start_cursor"] = start_cursor
                
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"❌ Erro ao ler Notion: {response.status_code} - {response.text}")
                return []
                
            dados = response.json()
            
            for bloco in dados.get("results", []):
                texto_puro = extrair_texto_do_bloco(bloco)
                
                # Ignora linhas vazias ou muito curtas (como cabeçalhos sem conteúdo)
                if len(texto_puro) < 5:
                    continue
                
                # Gera um identificador único para esta frase
                bloco_hash = hashlib.md5(texto_puro.encode("utf-8")).hexdigest()
                
                if bloco_hash not in historico:
                    blocos_novos.append({
                        "texto": texto_puro,
                        "hash": bloco_hash
                    })
            
            has_more = dados.get("has_more", False)
            start_cursor = dados.get("next_cursor")
            
        return blocos_novos
    except Exception as e:
        print(f"❌ Erro de conexão com o Notion: {e}")
        return []

def criar_baralho_se_nao_existir():
    payload = {
        "action": "createDeck",
        "version": 6,
        "params": {"deck": DECK_NAME}
    }
    try:
        requests.post(ANKI_CONNECT_URL, json=payload)
    except:
        pass

def gerar_cards_com_openrouter(texto_estudo: str) -> list:
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

def enviar_para_o_anki(card_texto: str):
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
                "tags": ["linux", "automacao_notion"]
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

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    
    # 1. Procura novidades no Notion
    conteudos_novos = ler_textos_novos_do_notion()
    
    if not conteudos_novos:
        print("✨ Tudo atualizado! Não foram encontradas novas anotações no Notion.")
    else:
        print(f"💡 Encontradas {len(conteudos_novos)} novas linhas para processar.")
        
        # Junta os blocos novos num texto único para poupar tokens na API
        texto_para_ia = "\n".join([item["texto"] for item in conteudos_novos])
        
        print("🤖 A chamar o OpenRouter (DeepSeek) para criar os flashcards...")
        lista_de_cards = gerar_cards_com_openrouter(texto_para_ia)
        
        if lista_de_cards:
            print(f"📥 Foram gerados {len(lista_de_cards)} cards. A injetar no Anki...")
            for card in lista_de_cards:
                if "texto" in card:
                    enviar_para_o_anki(card["texto"])
            
            # 3. Só guarda no histórico local se a criação de cards correu bem
            for item in conteudos_novos:
                salvar_no_historico(item["hash"])
            print("💾 Histórico atualizado localmente para evitar repetições.")
        else:
            print("⚠ Não foi possível gerar cards para as novas linhas desta vez.")