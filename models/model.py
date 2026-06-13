import os
import json
import requests
import hashlib
from openai import OpenAI

ANKI_CONNECT_URL = "http://localhost:8765"

TEMAS = {
    "Dark Purple Edition": {
        "fundo_principal": "#0a0a0c", "fundo_card": "#16161a", "destaque": "#6d28d9",
        "destaque_hover": "#7c3aed", "texto": "#f3f4f6", "texto_muted": "#9ca3af",
        "console_bg": "#020203", "console_fg": "#a78bfa"
    },
    "Cyberpunk Terminal": {
        "fundo_principal": "#000000", "fundo_card": "#0a0f0d", "destaque": "#00ff66",
        "destaque_hover": "#33ff88", "texto": "#cbffd9", "texto_muted": "#00aa44",
        "console_bg": "#000000", "console_fg": "#00ff66"
    },
    "Steel Minimalist": {
        "fundo_principal": "#f3f4f6", "fundo_card": "#ffffff", "destaque": "#1e40af",
        "destaque_hover": "#2563eb", "texto": "#1f2937", "texto_muted": "#4b5563",
        "console_bg": "#1f2937", "console_fg": "#ffffff"
    }
}

MODELOS_PRINCIPAIS = ["google/gemini-2.5-flash", "google/gemini-2.5-pro", "openai/gpt-4o-mini", "Outro (Digitar manualmente)"]
MODELOS_RESERVA = ["meta-llama/llama-3-8b-instruct:free", "deepseek/deepseek-r1:free", "qwen/qwen-2.5-7b-instruct:free", "Outro (Digitar manualmente)"]

class CardForgeModel:
    def __init__(self):
        os.makedirs("perfis", exist_ok=True)
        os.makedirs("historicos", exist_ok=True)

    def obter_perfis(self):
        return [f.replace(".json", "") for f in os.listdir("perfis") if f.endswith(".json")]

    def carregar_perfil(self, nome):
        caminho = os.path.join("perfis", f"{nome}.json")
        if not os.path.exists(caminho): return None
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    def salvar_perfil(self, nome, dados):
        with open(os.path.join("perfis", f"{nome}.json"), "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    def criar_novo_perfil(self, nome, tema_atual):
        modelo = {
            "NOTION_TOKEN": "SEU_TOKEN_AQUI", "NOTION_DATABASE_ID": "SEU_ID_NOTION_AQUI",
            "OPENROUTER_API_KEY": "SUA_KEY_AQUI", "DECK_NAME": nome,
            "AI_MODEL": MODELOS_PRINCIPAIS[0], "AI_MODEL_FALLBACK": MODELOS_RESERVA[0],
            "THEME": tema_atual
        }
        self.salvar_perfil(nome, modelo)

    def fluxo_geracao_core(self, nome_perfil, dados, log_callback):
        # Lógica assíncrona do motor de busca e geração de cartões
        token, id_notion = dados["token"], dados["id_notion"]
        api_key_or, deck_name = dados["api_key_or"], dados["deck_name"]
        model_principal, model_fallback = dados["model_principal"], dados["model_fallback"]

        log_callback(f"\n🚀 [EXECUÇÃO] Iniciando varredura para o perfil: {nome_perfil}")
        
        caminho_hist = os.path.join("historicos", f"{nome_perfil}_historico.txt")
        historico = set()
        if os.path.exists(caminho_hist):
            with open(caminho_hist, "r", encoding="utf-8") as f:
                historico = set(l.strip() for l in f if l.strip())

        log_callback("📖 Lendo blocos novos da página do Notion...")
        url = f"https://api.notion.com/v1/blocks/{id_notion}/children"
        headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
        
        try:
            response = requests.get(url, headers=headers, params={"page_size": 100})
            if response.status_code != 200:
                log_callback(f"❌ Erro de API no Notion ({response.status_code}): {response.text}")
                return False
        except Exception as e:
            log_callback(f"❌ Falha de conexão com o Notion: {e}")
            return False

        dados_notion = response.json()
        blocos_novos = []
        for bloco in dados_notion.get("results", []):
            b_type = bloco.get("type")
            if not b_type: continue
            conteudo = bloco.get(b_type)
            if isinstance(conteudo, dict) and "rich_text" in conteudo:
                texto_puro = "".join([t.get("plain_text", "") for t in conteudo["rich_text"]]).strip()
                if len(texto_puro) < 5: continue
                bloco_hash = hashlib.md5(texto_puro.encode("utf-8")).hexdigest()
                if bloco_hash not in historico:
                    blocos_novos.append({"texto": texto_puro, "hash": bloco_hash})

        if not blocos_novos:
            log_callback(f"✨ Tudo sincronizado! Nenhuma anotação inédita no perfil '{nome_perfil}'.")
            return "sincronizado"

        log_callback(f"💡 Foram localizadas {len(blocos_novos)} novas linhas estruturadas.")
        texto_para_ia = "\n".join([item["texto"] for item in blocos_novos])
        
        client = OpenAI(api_key=api_key_or, base_url="https://openrouter.ai/api/v1")
        prompt_sistema = """Você é um assistente especialista em concursos de TI e criação de flashcards para o Anki. Seu objetivo é receber anotações de estudo e transformá-las em flashcards no formato de Omissão de Palavras (Cloze Deletion). Regras: 1. Esconda apenas comandos, parâmetros ou termos técnicos usando {{c1::termo}}. 2. Seja extremamente direto. Responda obrigatoriamente com um OBJETO JSON contendo uma chave chamada "cards". Exemplo: {"cards": [{"texto": "O comando {{c1::ls -la}} lista arquivos ocultos."}]}"""
        
        lista_de_cards = []
        log_callback(f"🤖 Solicitando geração via inteligência principal ({model_principal})...")
        
        try:
            res = client.chat.completions.create(
                model=model_principal, messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_para_ia}],
                temperature=0.2, max_tokens=2000, response_format={'type': 'json_object'}
            )
            lista_de_cards = json.loads(res.choices[0].message.content).get("cards", [])
        except Exception as err_principal:
            log_callback(f"⚠️ Alerta: Modelo principal falhou/sem saldo: {err_principal}")
            log_callback(f"🔄 [CONTINGÊNCIA] Acionando rota inteligente reserva: {model_fallback}...")
            try:
                res = client.chat.completions.create(
                    model=model_fallback, messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_para_ia}],
                    temperature=0.2, max_tokens=2000, response_format={'type': 'json_object'}
                )
                lista_de_cards = json.loads(res.choices[0].message.content).get("cards", [])
                log_callback("✅ Rota reserva salvou a execução com sucesso!")
            except Exception as err_fallback:
                log_callback(f"❌ Erro Crítico: A IA de contingência também falhou: {err_fallback}")
                return False

        if not lista_de_cards:
            log_callback("⚠️ Nenhuma estrutura de card pôde ser extraída.")
            return False

        log_callback(f"📥 Processando {len(lista_de_cards)} cards gerados. Injetando no Anki Connect...")
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
                log_callback("❌ Falha crítica: O Anki Connect recusou a conexão. O seu Anki está aberto?")
                return False

        if cards_com_sucesso > 0:
            with open(caminho_hist, "a", encoding="utf-8") as f:
                for item in blocos_novos: f.write(f"{item['hash']}\n")
            log_callback(f"💾 Sucesso absoluto! {cards_com_sucesso} flashcards criados.")
            return cards_com_sucesso
        else:
            log_callback("⚠ Nenhum card pôde ser inserido no Anki (possível conteúdo duplicado).")
            return 0