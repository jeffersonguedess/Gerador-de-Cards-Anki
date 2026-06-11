import sys
import os
import json
import requests
import hashlib
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from openai import OpenAI

ANKI_CONNECT_URL = "http://localhost:8765"

# Listas de modelos pré-configurados para o Menu
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

class CardForgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CardForge v5 - Gerador Multiperfil de Flashcards")
        self.root.geometry("680x750")
        self.root.minsize(600, 650)
        
        # Garante a existência das pastas do ecossistema
        os.makedirs("perfis", exist_ok=True)
        os.makedirs("historicos", exist_ok=True)
        
        self.criar_elementos_visuais()
        self.atualizar_lista_perfis()
        
    def criar_elementos_visuais(self):
        # Estilo geral simples e limpo
        style = ttk.Style()
        style.theme_use("clam")
        
        # --- SEÇÃO 1: SELEÇÃO DE PERFIL ---
        frame_perfil = ttk.LabelFrame(self.root, text=" Gerenciamento de Perfil ", padding=10)
        frame_perfil.pack(fill="x", padx=15, pady=10)
        
        ttk.Label(frame_perfil, text="Perfil Ativo:").pack(side="left", padx=5)
        self.combo_perfis = ttk.Combobox(frame_perfil, state="readonly", width=25)
        self.combo_perfis.pack(side="left", padx=5)
        self.combo_perfis.bind("<<ComboboxSelected>>", self.evento_perfil_selecionado)
        
        ttk.Button(frame_perfil, text="Novo Perfil", command=self.janela_novo_perfil).pack(side="left", padx=5)
        
        # --- SEÇÃO 2: CREDENCIAIS E DADOS ---
        frame_dados = ttk.LabelFrame(self.root, text=" Configurações do Perfil ", padding=10)
        frame_dados.pack(fill="x", padx=15, pady=5)
        
        # Grid para alinhar labels e campos de texto
        frame_dados.columnconfigure(1, weight=1)
        
        ttk.Label(frame_dados, text="Notion Token:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.ent_notion_token = ttk.Entry(frame_dados, show="*")
        self.ent_notion_token.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        
        ttk.Label(frame_dados, text="Notion ID / DB:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.ent_notion_id = ttk.Entry(frame_dados)
        self.ent_notion_id.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        
        ttk.Label(frame_dados, text="OpenRouter Key:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.ent_openrouter_key = ttk.Entry(frame_dados, show="*")
        self.ent_openrouter_key.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        
        ttk.Label(frame_dados, text="Nome do Deck Anki:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.ent_deck_name = ttk.Entry(frame_dados)
        self.ent_deck_name.grid(row=3, column=1, sticky="ew", pady=5, padx=5)

        # --- SEÇÃO 3: SELEÇÃO DE MODELOS IA (FALLBACK) ---
        frame_ia = ttk.LabelFrame(self.root, text=" Configuração de Inteligência Artificial ", padding=10)
        frame_ia.pack(fill="x", padx=15, pady=10)
        frame_ia.columnconfigure(1, weight=1)
        
        # Modelo Principal
        ttk.Label(frame_ia, text="IA Principal:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.combo_model_principal = ttk.Combobox(frame_ia, values=MODELOS_PRINCIPAIS, state="normal")
        self.combo_model_principal.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        self.combo_model_principal.set(MODELOS_PRINCIPAIS[0])
        
        # Modelo de Backup / Fallback
        ttk.Label(frame_ia, text="IA Reserva (Plano B):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.combo_model_fallback = ttk.Combobox(frame_ia, values=MODELOS_RESERVA, state="normal")
        self.combo_model_fallback.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        self.combo_model_fallback.set(MODELOS_RESERVA[0])

        # --- SEÇÃO 4: BOTÕES DE AÇÃO ---
        frame_botoes = ttk.Frame(self.root, padding=5)
        frame_botoes.pack(fill="x", padx=15, pady=5)
        
        self.btn_salvar = ttk.Button(frame_botoes, text="💾 Salvar Configurações", command=self.salvar_configuracoes_atuais)
        self.btn_salvar.pack(side="left", expand=True, fill="x", padx=5)
        
        self.btn_gerar = ttk.Button(frame_botoes, text="🚀 Gerar Flashcards", command=self.disparar_fluxo_geracao)
        self.btn_gerar.pack(side="left", expand=True, fill="x", padx=5)
        
        # --- SEÇÃO 5: CONSOLE DE LOGS ---
        ttk.Label(self.root, text="Histórico de Execução e Logs em Tempo Real:").pack(anchor="w", padx=15, pady=(10,0))
        self.txt_log = scrolledtext.ScrolledText(self.root, height=12, bg="#1e1e1e", fg="#ffffff", insertbackground="white", font=("Consolas", 10))
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.log("🤖 CardForge inicializado com sucesso. Escolha ou crie um perfil para começar.")

    # ================= GERENCIAMENTO DE PERFIS =================
    
    def log(self, mensagem):
        """Imprime mensagens na caixa de texto preta do app"""
        self.txt_log.insert(tk.END, f"{mensagem}\n")
        self.txt_log.see(tk.END)

    def atualizar_lista_perfis(self, selecionar_nome=None):
        perfis = [f.replace(".json", "") for f in os.listdir("perfis") if f.endswith(".json")]
        self.combo_perfis["values"] = perfis
        if perfis:
            if selecionar_nome in perfis:
                self.combo_perfis.set(selecionar_nome)
            else:
                self.combo_perfis.set(perfis[0])
            self.evento_perfil_selecionado()
        else:
            self.limpar_campos()

    def evento_perfil_selecionado(self, event=None):
        nome_perfil = self.combo_perfis.get()
        if not nome_perfil:
            return
        
        caminho = os.path.join("perfis", f"{nome_perfil}.json")
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            self.ent_notion_token.delete(0, tk.END)
            self.ent_notion_token.insert(0, config.get("NOTION_TOKEN", ""))
            
            id_notion = config.get("NOTION_DATABASE_ID") or config.get("NOTION_PAGE_ID", "")
            self.ent_notion_id.delete(0, tk.END)
            self.ent_notion_id.insert(0, id_notion)
            
            self.ent_openrouter_key.delete(0, tk.END)
            self.ent_openrouter_key.insert(0, config.get("OPENROUTER_API_KEY", ""))
            
            self.ent_deck_name.delete(0, tk.END)
            self.ent_deck_name.insert(0, config.get("DECK_NAME", nome_perfil))
            
            self.combo_model_principal.set(config.get("AI_MODEL", "google/gemini-2.5-flash"))
            self.combo_model_fallback.set(config.get("AI_MODEL_FALLBACK", "meta-llama/llama-3-8b-instruct:free"))
            
            self.log(f"📁 Perfil '{nome_perfil}' carregado com sucesso.")
        except Exception as e:
            self.log(f"❌ Erro ao ler o perfil {nome_perfil}: {e}")

    def limpar_campos(self):
        self.ent_notion_token.delete(0, tk.END)
        self.ent_notion_id.delete(0, tk.END)
        self.ent_openrouter_key.delete(0, tk.END)
        self.ent_deck_name.delete(0, tk.END)

    def janela_novo_perfil(self):
        # Janela popup menor para coletar o nome do perfil novo
        janela_popup = tk.Toplevel(self.root)
        janela_popup.title("Criar Novo Perfil")
        janela_popup.geometry("300x120")
        janela_popup.resizable(False, False)
        janela_popup.grab_set() # Bloqueia a janela de trás
        
        ttk.Label(janela_popup, text="Nome da Matéria / Perfil:").pack(pady=5)
        ent_nome = ttk.Entry(janela_popup, width=30)
        ent_nome.pack(pady=5)
        ent_nome.focus()
        
        def confirmar():
            nome = ent_nome.get().strip()
            if not nome or f"{nome}.json" in os.listdir("perfis"):
                messagebox.showerror("Erro", "Nome inválido ou perfil já existente.", parent=janela_popup)
                return
            
            # Cria esqueleto vazio
            modelo = {
                "NOTION_TOKEN": "SEU_TOKEN_AQUI",
                "NOTION_DATABASE_ID": "SEU_ID_DO_NOTION_AQUI",
                "OPENROUTER_API_KEY": "SUA_CHAVE_OPENROUTER_AQUI",
                "DECK_NAME": nome,
                "AI_MODEL": "google/gemini-2.5-flash",
                "AI_MODEL_FALLBACK": "meta-llama/llama-3-8b-instruct:free"
            }
            with open(os.path.join("perfis", f"{nome}.json"), "w", encoding="utf-8") as f:
                json.dump(modelo, f, indent=4, ensure_ascii=False)
                
            self.log(f"✨ Novo perfil '{nome}' criado no sistema.")
            janela_popup.destroy()
            self.atualizar_lista_perfis(selecionar_nome=nome)
            
        ttk.Button(janela_popup, text="Criar Perfil", command=confirmar).pack(pady=5)

    def salvar_configuracoes_atuais(self):
        nome_perfil = self.combo_perfis.get()
        if not nome_perfil:
            messagebox.showwarning("Aviso", "Nenhum perfil ativo para salvar.")
            return
            
        config = {
            "NOTION_TOKEN": self.ent_notion_token.get().strip(),
            "NOTION_DATABASE_ID": self.ent_notion_id.get().strip(),
            "OPENROUTER_API_KEY": self.ent_openrouter_key.get().strip(),
            "DECK_NAME": self.ent_deck_name.get().strip(),
            "AI_MODEL": self.combo_model_principal.get().strip(),
            "AI_MODEL_FALLBACK": self.combo_model_fallback.get().strip()
        }
        
        caminho = os.path.join("perfis", f"{nome_perfil}.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
        self.log(f"💾 Alterações salvas com sucesso em 'perfis/{nome_perfil}.json'.")
        messagebox.showinfo("Sucesso", f"Configurações do perfil '{nome_perfil}' foram salvas!")

    # ================= BACKEND ADAPTADO (MOTOR DO SISTEMA) =================

    def disparar_fluxo_geracao(self):
        nome_perfil = self.combo_perfis.get()
        if not nome_perfil:
            messagebox.showerror("Erro", "Selecione um perfil antes de rodar.")
            return
            
        # Bloqueia o botão temporariamente para o usuário não clicar duas vezes
        self.btn_gerar.config(state="disabled")
        
        # Executa em uma Thread separada pro app não congelar a janela
        threading.Thread(target=self.fluxo_geracao_background, args=(nome_perfil,), daemon=True).start()

    def fluxo_geracao_background(self, nome_perfil):
        try:
            token = self.ent_notion_token.get().strip()
            id_notion = self.ent_notion_id.get().strip()
            api_key_or = self.ent_openrouter_key.get().strip()
            deck_name = self.ent_deck_name.get().strip()
            model_principal = self.combo_model_principal.get().strip()
            model_fallback = self.combo_model_fallback.get().strip()
            
            self.log(f"\n🚀 Iniciando varredura para o perfil: {nome_perfil}")
            
            # 1. Carrega Histórico
            caminho_hist = os.path.join("historicos", f"{nome_perfil}_historico.txt")
            historico = set()
            if os.path.exists(caminho_hist):
                with open(caminho_hist, "r", encoding="utf-8") as f:
                    historico = set(l.strip() for l in f if l.strip())
            
            # 2. Conecta ao Notion
            self.log("📖 Lendo blocos do Notion...")
            url = f"https://api.notion.com/v1/blocks/{id_notion}/children"
            headers = {
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, params={"page_size": 100})
            if response.status_code != 200:
                self.log(f"❌ Erro na API do Notion ({response.status_code}): {response.text}")
                return
                
            dados = response.json()
            blocos_novos = []
            
            for bloco in dados.get("results", []):
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
                self.log(f"✨ Tudo atualizado! Sem anotações inéditas para '{nome_perfil}'.")
                return
                
            self.log(f"💡 Encontradas {len(blocos_novos)} novas linhas estruturadas.")
            texto_para_ia = "\n".join([item["texto"] for item in blocos_novos])
            
            # 3. Chama a Inteligência Artificial (com o seu Fallback Estratégico)
            client = OpenAI(api_key=api_key_or, base_url="https://openrouter.ai/api/v1")
            prompt_sistema = """
            Você é um assistente especialista em concursos de TI e criação de flashcards para o Anki.
            Seu objetivo é receber anotações de estudo e transformá-las em flashcards no formato de Omissão de Palavras (Cloze Deletion).
            Regras:
            1. Esconda apenas comandos, parâmetros ou termos técnicos usando {{c1::termo}}.
            2. Seja extremamente direto. responda obrigatoriamente com um OBJETO JSON contendo uma chave chamada "cards".
            Exemplo: {"cards": [{"texto": "O comando {{c1::ls -la}} lista arquivos ocultos."}]}
            """
            
            lista_de_cards = []
            self.log(f"🤖 Solicitando geração de cards à IA Principal ({model_principal})...")
            
            try:
                res = client.chat.completions.create(
                    model=model_principal,
                    messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_para_ia}],
                    temperature=0.2, max_tokens=2000, response_format={'type': 'json_object'}
                )
                lista_de_cards = json.loads(res.choices[0].message.content).get("cards", [])
            except Exception as err_principal:
                self.log(f"⚠️ Conta principal sem saldo ou em manutenção: {err_principal}")
                self.log(f"🔄 [EMERGÊNCIA] Acionando rota gratuita salvadora: {model_fallback}...")
                try:
                    res = client.chat.completions.create(
                        model=model_fallback,
                        messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_para_ia}],
                        temperature=0.2, max_tokens=2000, response_format={'type': 'json_object'}
                    )
                    lista_de_cards = json.loads(res.choices[0].message.content).get("cards", [])
                    self.log("✅ Backup funcionou perfeitamente e salvou a execução!")
                except Exception as err_fallback:
                    self.log(f"❌ Erro Crítico: A IA de backup também falhou: {err_fallback}")
                    return
            
            # 4. Injeção no Anki
            if not lista_de_cards:
                self.log("⚠️ Nenhuma estrutura de card pôde ser gerada.")
                return
                
            self.log(f"📥 Recebidos {len(lista_de_cards)} cards da IA. Enviando ao Anki...")
            # Garante criação do deck
            try: requests.post(ANKI_CONNECT_URL, json={"action": "createDeck", "version": 6, "params": {"deck": deck_name}})
            except: pass
            
            cards_com_sucesso = 0
            for card in lista_de_cards:
                if "texto" not in card: continue
                payload = {
                    "action": "addNote", "version": 6,
                    "params": {
                        "note": {
                            "deckName": deck_name, "modelName": "Omissão de palavras",
                            "fields": {"Texto": card["texto"]}, "tags": ["concursos", "interface_forge"]
                        }
                    }
                }
                try:
                    res_anki = requests.post(ANKI_CONNECT_URL, json=payload).json()
                    if not res_anki.get("error"):
                        cards_com_sucesso += 1
                except:
                    self.log("❌ Erro fatal: O Anki está fechado! Abra o Anki no computador.")
                    return
                    
            # 5. Salva no histórico se houve inserção bem sucedida
            if cards_com_sucesso > 0:
                with open(caminho_hist, "a", encoding="utf-8") as f:
                    for item in blocos_novos:
                        f.write(f"{item['hash']}\n")
                self.log(f"💾 Sucesso absoluto! {cards_com_sucesso} cards injetados no Anki e histórico do perfil '{nome_perfil}' protegido.")
                messagebox.showinfo("Sucesso", f"{cards_com_sucesso} flashcards foram enviados para o Anki!")
            else:
                self.log("⚠ Nenhum card foi adicionado (possível duplicata ou falha interna do Anki Connect).")
                
        except Exception as e_geral:
            self.log(f"❌ Ocorreu um erro inesperado: {e_geral}")
        finally:
            # Reativa o botão de gerar após o fim da thread
            self.btn_gerar.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = CardForgeApp(root)
    root.mainloop()