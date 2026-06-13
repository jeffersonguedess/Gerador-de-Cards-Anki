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
        """
        Gera os flashcards via OpenRouter (com fallback) e envia para o Anki Connect.
        Fix: Erro de variáveis 'log_callback' sincronizadas para 'callback_log'.
        """
        try:
            callback_log("🤖 Inicializando motor de inteligência artificial...")
            
            if not dados_perfil.get("OPENROUTER_API_KEY"):
                callback_log("❌ Chave API do OpenRouter não configurada neste perfil!")
                return False
                
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1", 
                api_key=dados_perfil["OPENROUTER_API_KEY"]
            )
            
            # Construção do Prompt estruturado para Omissão de Palavras (Cloze)
            prompt_sistema = (
                "Você é um especialista em extrair conceitos de engenharia, programação e TI, "
                "transformando-os em flashcards eficazes para o Anki no formato de Omissão de Palavras (Cloze Deletion).\n"
                "Regra crucial: Retorne estritamente um objeto JSON com uma lista contendo os cards gerados. "
                "Cada item deve ser um dicionário com a chave 'texto'.\n"
                "Exemplo de formato de saída esperado:\n"
                '{"cards": [{"texto": "O comando {{c1::pwd}} serve para mostrar o diretório atual no Linux."}]}'
            )
            
            prompt_usuario = f"Gere flashcards com base no seguinte material de estudo:\n\n{texto_estudo}"
            
            conteudo_resposta = None
            modelo_tentativa = dados_perfil.get("AI_MODEL", MODELOS_PRINCIPAIS[0])
            
            try:
                callback_log(f"🧠 Enviando requisição para o Modelo Principal: {modelo_tentativa}...")
                response = client.chat.completions.create(
                    model=modelo_tentativa,
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": prompt_usuario}
                    ]
                )
                conteudo_resposta = response.choices[0].message.content
            except Exception as error_principal:
                modelo_fallback = dados_perfil.get("AI_MODEL_FALLBACK", MODELOS_RESERVA[0])
                callback_log(f"⚠ Modelo principal falhou: {error_principal}")
                callback_log(f"🔄 Acionando Modelo de Reserva imediatamente: {modelo_fallback}...")
                
                response = client.chat.completions.create(
                    model=modelo_fallback,
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": prompt_usuario}
                    ]
                )
                conteudo_resposta = response.choices[0].message.content

            if not conteudo_resposta:
                callback_log("❌ Nenhuma resposta foi obtida das Inteligências Artificiais.")
                return False
                
            # Limpeza e Parsing do JSON retornado pela IA
            try:
                # Remove possíveis marcações de markdown de bloco de código json, se houverem
                if "```json" in conteudo_resposta:
                    conteudo_resposta = conteudo_resposta.split("```json")[1].split("```")[0].strip()
                elif "```" in conteudo_resposta:
                    conteudo_resposta = conteudo_resposta.split("```")[1].split("```")[0].strip()
                
                dados_cards = json.loads(conteudo_resposta.strip())
                lista_cards = dados_cards.get("cards", [])
            except Exception as e_json:
                callback_log("⚠ Falha ao parsear JSON nativo da IA. Tentando fatiamento alternativo...")
                # Fallback de segurança: Caso a IA mande texto puro separado por quebras ou traços
                lista_cards = [{"texto": bloco.strip()} for bloco in conteudo_resposta.split("---") if bloco.strip()]

            if not lista_cards:
                callback_log("⚠ Nenhum card válido estruturado foi identificado na resposta.")
                return False

            # Processamento de Histórico e Proteção de Duplicatas
            deck_name = dados_perfil.get("DECK_NAME", "CardForge_Deck")
            caminho_hist = f"historicos/{deck_name}.txt"
            
            historio_existente = set()
            if os.path.exists(caminho_hist):
                with open(caminho_hist, "r", encoding="utf-8") as f:
                    historio_existente = set(linha.strip() for linha in f if linha.strip())

            cards_com_sucesso = 0
            blocos_novos = []

            callback_log(f"🚀 Verificando duplicatas e injetando no Anki (Deck: {deck_name})...")
            
            for item in lista_cards:
                texto_card = item.get("texto", "").strip()
                if not texto_card:
                    continue
                    
                # Criação do hash md5 único do card para controle anti-duplicação
                card_hash = hashlib.md5(texto_card.encode("utf-8")).hexdigest()
                
                if card_hash in historio_existente:
                    continue
                    
                blocos_novos.append({"hash": card_hash, "texto": texto_card})
                
                # Payload oficial de comunicação com a API do Anki Connect
                payload = {
                    "action": "addNote",
                    "version": 6,
                    "params": {
                        "note": {
                            "deckName": deck_name,
                            "modelName": "Omissão de palavras",
                            "fields": {"Texto": texto_card},
                            "tags": ["concursos", "cardforge_pericia"]
                        }
                    }
                }
                
                try:
                    res_anki = requests.post(ANKI_CONNECT_URL, json=payload).json()
                    if not res_anki.get("error"):
                        cards_com_sucesso += 1
                except:
                    callback_log("❌ Falha crítica: O Anki Connect recusou a conexão. O seu Anki está aberto?")
                    return False

            # Salvando as hashes dos novos cards gerados
            if cards_com_sucesso > 0:
                with open(caminho_hist, "a", encoding="utf-8") as f:
                    for item in blocos_novos:
                        f.write(f"{item['hash']}\n")
                callback_log(f"💾 Sucesso absoluto! {cards_com_sucesso} novos flashcards sincronizados no Anki.")
                return cards_com_sucesso
            else:
                callback_log("⚠ Processo concluído: Nenhum card inédito inserido (Conteúdo já existia no histórico).")
                return 0
                
        except Exception as e:
            callback_log(f"❌ Falha crítica no motor de dados: {e}")
            return False