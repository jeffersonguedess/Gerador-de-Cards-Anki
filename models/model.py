# models/model.py
import os
import json
import requests
import hashlib
from openai import OpenAI

# 1. CONSTANTES GLOBAIS
ANKI_CONNECT_URL = "http://localhost:8765"

# Seus modelos customizados preservados com sucesso!
MODELOS_PRINCIPAIS = [
    "google/gemini-2.5-flash", 
    "google/gemini-2.5-pro", 
    "openai/gpt-4o-mini", 
    "Outro (Digitar manualmente)"
]

MODELOS_RESERVA = [
    "meta-llama/llama-3-8b-instruct:free", 
    "deepseek/deepseek-r1:free", 
    "qwen/qwen-2.5-7b-instruct:free", 
    "Outro (Digitar manualmente)"
]


class CardForgeModel:
    def __init__(self):
        # Cria as pastas necessárias de forma segura
        os.makedirs("perfis", exist_ok=True)
        os.makedirs("historicos", exist_ok=True)
        
        # Define o arquivo de perfis na raiz do projeto
        self.arquivo_perfis = os.path.join(os.path.dirname(__file__), "..", "perfis.json")
        if not os.path.exists(self.arquivo_perfis):
            self.salvar_todos_perfis({})
    
    # =========================================================================
    # PARTE 1: GERENCIAMENTO DE PERFIS E CONFIGURAÇÕES
    # =========================================================================
    def salvar_todos_perfis(self, dados):
        with open(self.arquivo_perfis, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
            
    def listar_perfis(self):
        if not os.path.exists(self.arquivo_perfis):
            return []
        try:
            with open(self.arquivo_perfis, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return list(dados.keys())
        except:
            return []
            
    def salvar_perfil(self, nome, dados_perfil):
        dados = {}
        if os.path.exists(self.arquivo_perfis):
            try:
                with open(self.arquivo_perfis, "r", encoding="utf-8") as f:
                    dados = json.load(f)
            except:
                dados = {}
        dados[nome] = dados_perfil
        self.salvar_todos_perfis(dados)
        
    def carregar_perfil(self, nome):
        if not os.path.exists(self.arquivo_perfis):
            return None
        try:
            with open(self.arquivo_perfis, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados.get(nome)
        except:
            return None

    def criar_novo_perfil(self, nome, tema_atual):
        modelo = {
            "NOTION_TOKEN": "", 
            "NOTION_DATABASE_ID": "",
            "OPENROUTER_API_KEY": "", 
            "DECK_NAME": nome,
            "AI_MODEL": MODELOS_PRINCIPAIS[0], 
            "AI_MODEL_FALLBACK": MODELOS_RESERVA[0],
            "THEME": tema_atual
        }
        self.salvar_perfil(nome, modelo)

    # =========================================================================
    # PARTE 2: MOTOR DE INTEGRAÇÃO COM IA (OPENROUTER) E ANKI
    # =========================================================================
    def gerar_e_enviar_cards(self, dados_perfil, texto_estudo, callback_log):
        origem = dados_perfil.get("origem", "notion")
        token = dados_perfil.get("token", "").strip()
        id_notion = dados_perfil.get("id_notion", "").strip()
        api_key_or = dados_perfil.get("api_key_or", "").strip()
        deck_name = dados_perfil.get("deck_name", "Default").strip()
        model_principal = dados_perfil.get("model_principal", "").strip()
        model_fallback = dados_perfil.get("model_fallback", "").strip()
        nome_perfil = dados_perfil.get("nome_perfil", "Log").strip()

        callback_log(f"\n🚀 [EXECUÇÃO] Iniciando motor via: {origem.upper()}")
        
        texto_para_ia = ""
        blocos_novos = []
        caminho_hist = os.path.join("historicos", f"{nome_perfil}_historico.txt")
        os.makedirs("historicos", exist_ok=True)

        if origem == "notion":
            callback_log("📖 Lendo blocos novos da página do Notion...")
            historico = set()
            if os.path.exists(caminho_hist):
                with open(caminho_hist, "r", encoding="utf-8") as f:
                    historico = set(l.strip() for l in f if l.strip())

            import requests, hashlib
            url = f"https://api.notion.com/v1/blocks/{id_notion}/children"
            headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
            
            try:
                response = requests.get(url, headers=headers, params={"page_size": 100})
                if response.status_code != 200:
                    callback_log(f"❌ Erro de API no Notion ({response.status_code}): {response.text}")
                    return False
            except Exception as e:
                callback_log(f"❌ Falha de conexão com o Notion: {e}")
                return False

            dados_notion = response.json()
            for bloco in dados_notion.get("results", []):
                b_type = bloco.get("type")
                if not b_type: continue
                conteudo_bloco = bloco.get(b_type)
                if isinstance(conteudo_bloco, dict) and "rich_text" in conteudo_bloco:
                    texto_puro = "".join([t.get("plain_text", "") for t in conteudo_bloco["rich_text"]]).strip()
                    if len(texto_puro) < 5: continue
                    bloco_hash = hashlib.md5(texto_puro.encode("utf-8")).hexdigest()
                    if bloco_hash not in historico:
                        blocos_novos.append({"texto": texto_puro, "hash": bloco_hash})

            if not blocos_novos:
                callback_log(f"✨ Tudo sincronizado! Nenhuma anotação inédita no Notion.")
                return "sincronizado"

            callback_log(f"💡 Foram localizadas {len(blocos_novos)} novas linhas estruturadas.")
            texto_para_ia = "\n".join([item["texto"] for item in blocos_novos])
        
        else:
            # Pega o texto que veio direto da tela (passado via parâmetro texto_estudo)
            texto_para_ia = texto_estudo
            if not texto_para_ia or len(texto_para_ia) < 5:
                callback_log("⚠️ O texto inserido na tela está vazio ou é muito curto.")
                return False
            callback_log("📝 Processando texto manual inserido na interface...")

        import json, requests
        from openai import OpenAI
        ANKI_CONNECT_URL = "http://localhost:8765"
        
        client = OpenAI(api_key=api_key_or, base_url="https://openrouter.ai/api/v1")
        prompt_sistema = """Você é um assistente especialista em concursos de TI e criação de flashcards para o Anki. Seu objetivo é receber anotações de estudo e transformá-las em flashcards no formato de Omissão de Palavras (Cloze Deletion). Regras: 1. Esconda apenas comandos, parâmetros ou termos técnicos usando {{c1::termo}}. 2. Seja extremamente direto. Responda obrigatoriamente com um OBJETO JSON contendo uma chave chamada "cards". Exemplo: {"cards": [{"texto": "O comando {{c1::ls -la}} lista arquivos ocultos."}]}"""
        
        lista_de_cards = []
        callback_log(f"🤖 Solicitando geração via inteligência principal ({model_principal})...")
        
        try:
            res = client.chat.completions.create(
                model=model_principal, messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_para_ia}],
                temperature=0.2, max_tokens=2000, response_format={'type': 'json_object'}
            )
            lista_de_cards = json.loads(res.choices[0].message.content).get("cards", [])
        except Exception as err_principal:
            callback_log(f"⚠️ Alerta: Modelo principal falhou/sem saldo: {err_principal}")
            callback_log(f"🔄 [CONTINGÊNCIA] Acionando rota inteligente reserva: {model_fallback}...")
            try:
                res = client.chat.completions.create(
                    model=model_fallback, messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_para_ia}],
                    temperature=0.2, max_tokens=2000, response_format={'type': 'json_object'}
                )
                lista_de_cards = json.loads(res.choices[0].message.content).get("cards", [])
                callback_log("✅ Rota reserva salvou a execução com sucesso!")
            except Exception as err_fallback:
                callback_log(f"❌ Erro Crítico: A IA de contingência também falhou: {err_fallback}")
                return False

        if not lista_de_cards:
            callback_log("⚠️ Nenhuma estrutura de card pôde ser extraída.")
            return False

        callback_log(f"📥 Processando {len(lista_de_cards)} cards gerados. Injetando no Anki Connect...")
        try: requests.post(ANKI_CONNECT_URL, json={"action": "createDeck", "version": 6, "params": {"deck": deck_name}})
        except: pass
        
        cards_com_sucesso = 0
        for card in lista_de_cards:
            if "texto" not in card: continue
            payload = {"action": "addNote", "version": 6, "params": {"note": {"deckName": deck_name, "modelName": "Omissão de palavras", "fields": {"Texto": card["texto"]}, "tags": ["concursos", "theme_forge"]}}}
            try:
                res_anki = requests.post(ANKI_CONNECT_URL, json=payload).json()
                if not res_anki.get("error"): cards_com_sucesso += 1
            except:
                callback_log("❌ Falha crítica: O Anki Connect recusou a conexão. O seu Anki está aberto?")
                return False

        if cards_com_sucesso > 0:
            if origem == "notion" and blocos_novos:
                with open(caminho_hist, "a", encoding="utf-8") as f:
                    for item in blocos_novos: f.write(f"{item['hash']}\n")
            callback_log(f"💾 Sucesso absoluto! {cards_com_sucesso} flashcards criados.")
            return cards_com_sucesso
        else:
            callback_log("⚠ Nenhum card pôde ser inserido no Anki (possível conteúdo duplicado).")
            return 0