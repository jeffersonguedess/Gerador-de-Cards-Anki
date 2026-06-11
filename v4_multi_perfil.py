import requests
import json
import os
import hashlib
from openai import OpenAI

# Configurações Globais Fixas
ANKI_CONNECT_URL = "http://localhost:8765"

def carregar_configuracao_perfil(nome_perfil):
    """Garante as pastas e carrega o arquivo .json do perfil selecionado"""
    # 1. Garante que as pastas organizadas existem
    os.makedirs("perfis", exist_ok=True)
    os.makedirs("historicos", exist_ok=True)
    
    # 2. Define o caminho do arquivo deste perfil específico
    caminho_config = os.path.join("perfis", f"{nome_perfil}.json")
    
    # Se o perfil não existir (ex: primeira vez rodando Git), cria um modelo vazio
    if not os.path.exists(caminho_config):
        modelo_config = {
            "NOTION_TOKEN": "SEU_TOKEN_AQUI",
            "NOTION_DATABASE_ID": "SEU_ID_DO_NOTION_AQUI",
            "OPENROUTER_API_KEY": "SUA_CHAVE_OPENROUTER_AQUI",
            "AI_MODEL": "google/gemini-2.5-flash",
            "DECK_NAME": nome_perfil
        }
        with open(caminho_config, "w", encoding="utf-8") as f:
            json.dump(modelo_config, f, indent=4, ensure_ascii=False)
        print(f"⚠️ Perfil '{nome_perfil}' não encontrado. Criamos um modelo em: {caminho_config}")
        return modelo_config

    # Se já existir, apenas lê as configurações gravadas
    with open(caminho_config, "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_historico(nome_perfil) -> set:
    """Carrega o histórico específico do perfil selecionado"""
    caminho_historico = os.path.join("historicos", f"{nome_perfil}_historico.txt")
    if not os.path.exists(caminho_historico):
        return set()
    with open(caminho_historico, "r", encoding="utf-8") as f:
        return set(linha.strip() for linha in f if linha.strip())

def salvar_no_historico(nome_perfil, bloco_hash: str):
    """Salva o hash do bloco lido no arquivo de histórico do perfil correspondente"""
    caminho_historico = os.path.join("historicos", f"{nome_perfil}_historico.txt")
    with open(caminho_historico, "a", encoding="utf-8") as f:
        f.write(f"{bloco_hash}\n")

def extrair_texto_do_bloco(block: dict) -> str:
    block_type = block.get("type")
    if not block_type:
        return ""
    conteudo_bloco = block.get(block_type)
    if isinstance(conteudo_bloco, dict) and "rich_text" in conteudo_bloco:
        rich_text = conteudo_bloco["rich_text"]
        return "".join([texto.get("plain_text", "") for texto in rich_text]).strip()
    return ""

def ler_textos_novos_do_notion(nome_perfil, token, page_id) -> list:
    print(f"📖 Acessando sua página do Notion para o perfil '{nome_perfil}'...")
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    historico = carregar_historico(nome_perfil)
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
                if len(texto_puro) < 5:
                    continue
                
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

def criar_baralho_se_nao_existir(deck_name):
    payload = {"action": "createDeck", "version": 6, "params": {"deck": deck_name}}
    try: requests.post(ANKI_CONNECT_URL, json=payload)
    except: pass

def gerar_cards_com_openrouter(client, model, texto_estudo: str) -> list:
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
            model=model, 
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Transforme estas notas em cards Anki:\n\n{texto_estudo}"}
            ],
            temperature=0.2,
            max_tokens=2000, # 🌟 ADICIONE ESTA LINHA AQUI PARA LIMITAR O GASTO EMERGENCIAL
            response_format={'type': 'json_object'}
        )
        resultado_json = json.loads(response.choices[0].message.content)
        return resultado_json.get("cards", [])
    except Exception as e:
        print(f"❌ Erro na API do OpenRouter: {e}")
        return []

def enviar_para_o_anki(deck_name, card_texto: str) -> bool:
    criar_baralho_se_nao_existir(deck_name)
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": "Omissão de palavras",
                "fields": {"Texto": card_texto},
                "tags": ["perito", "automacao_notion"]
            }
        }
    }
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload)
        resultado = response.json()
        if resultado.get("error"):
            print(f"❌ Erro no AnkiConnect: {resultado['error']}")
            return False
        else:
            print(f"✅ Card injetado com sucesso! ID: {resultado['result']}")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ Erro: O Anki não está aberto no computador.")
        return False

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    print("🤖 Inicializando o Gerador de Cards...")
    
    # 🌟 DEFINA AQUI QUAL MATÉRIA QUER GERAR MANUALLY ENQUANTO NÃO TEMOS A INTENFACE 🌟
    # Pode mudar para "linux", "direito", etc.
    NOME_PERFIL = "Debian"
   
   # Carrega configurações usando a nova função dinâmica
    config = carregar_configuracao_perfil(NOME_PERFIL)
    
    client = OpenAI(
        api_key=config["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Procura novidades no Notion usando a chave correta DATABASE_ID
    conteudos_novos = ler_textos_novos_do_notion(NOME_PERFIL, config["NOTION_TOKEN"], config["NOTION_DATABASE_ID"])
    
    if not conteudos_novos:
        print("\n✨ Tudo atualizado! Não foram encontradas novas anotações no Notion.")
    else:
        print(f"\n💡 Encontradas {len(conteudos_novos)} novas linhas para processar.")
        texto_para_ia = "\n".join([item["texto"] for item in conteudos_novos])
        
        print(f"🤖 Chamando OpenRouter ({config['AI_MODEL']}) para criar os flashcards...")
        lista_de_cards = gerar_cards_com_openrouter(client, config["AI_MODEL"], texto_para_ia)
        
        if lista_de_cards:
            print(f"📥 Foram gerados {len(lista_de_cards)} cards. Injetando no Anki...")
            cards_com_sucesso = 0
            
            for card in lista_de_cards:
                if "texto" in card:
                    if enviar_para_o_anki(config["DECK_NAME"], card["texto"]):
                        cards_com_sucesso += 1
            
            if cards_com_sucesso > 0:
                # Salva no histórico apenas os blocos que foram lidos com sucesso
                for item in conteudos_novos:
                    salvar_no_historico(config["DECK_NAME"],item["hash"])
                print(f"\n💾 Processo concluído! {cards_com_sucesso} cards enviados e histórico salvo.")
            else:
                print("\n⚠ Falha: Nenhum card pôde ser injetado no Anki.")
        else:
            print("\n⚠ Não foi possível gerar cards para as novas linhas desta vez (API error/limit).")
            
    # ====================================================
    # 🛑 ESSA LINHA ABAIXO TRAVA A JANELA DO EXECUTÁVEL!
    # ====================================================
    print("\n" + "="*40)
    input(" Fim do processo. Pressione ENTER para fechar...")