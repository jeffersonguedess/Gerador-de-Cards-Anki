import sys
import os
import json
import requests
import hashlib
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from openai import OpenAI

ANKI_CONNECT_URL = "http://localhost:8765"

# --- BANCO DE DADOS DOS TEMAS VISUAIS ---
TEMAS = {
    "Dark Purple Edition": {
        "fundo_principal": "#0a0a0c",
        "fundo_card": "#16161a",
        "destaque": "#6d28d9",
        "destaque_hover": "#7c3aed",
        "texto": "#f3f4f6",
        "texto_muted": "#9ca3af",
        "console_bg": "#020203",
        "console_fg": "#a78bfa"
    },
    "Cyberpunk Terminal": {
        "fundo_principal": "#000000",
        "fundo_card": "#0a0f0d",
        "destaque": "#00ff66",
        "destaque_hover": "#33ff88",
        "texto": "#cbffd9",
        "texto_muted": "#00aa44",
        "console_bg": "#000000",
        "console_fg": "#00ff66"
    },
    "Steel Minimalist": {
        "fundo_principal": "#f3f4f6",
        "fundo_card": "#ffffff",
        "destaque": "#1e40af",
        "destaque_hover": "#2563eb",
        "texto": "#1f2937",
        "texto_muted": "#4b5563",
        "console_bg": "#1f2937",
        "console_fg": "#ffffff"
    }
}

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

class CardForgeThemeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CardForge v6.0 - Theme Engine Edition")
        self.root.geometry("680x810")
        
        os.makedirs("perfis", exist_ok=True)
        os.makedirs("historicos", exist_ok=True)
        
        # Listas de controlo para o motor dinâmico de recolorização
        self.frames_principais = []
        self.label_frames_cards = []
        self.labels_normais = []
        self.labels_muted = []
        self.entries = []
        self.botoes_destaque = []
        self.botoes_secundarios = []
        self.option_menus = []
        
        self.criar_interface_estilizada()
        self.atualizar_lista_perfis()

    def criar_interface_estilizada(self):
        # Frame Base do Root para controlo de fundo
        self.frames_principais.append(self.root)
        
        # --- SEÇÃO 1: GERENCIAMENTO DE PERFIL E TEMA ---
        frame_perfil = tk.LabelFrame(self.root, text=" Configurações de Ambiente ", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_perfil.pack(fill="x", padx=15, pady=10)
        self.label_frames_cards.append(frame_perfil)
        
        # Linha do Perfil
        lbl_p = tk.Label(frame_perfil, text="Perfil Ativo:")
        lbl_p.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_p)
        
        self.combo_perfis = tk.StringVar()
        self.dropdown_perfis = tk.OptionMenu(frame_perfil, self.combo_perfis, "")
        self.dropdown_perfis.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.option_menus.append(self.dropdown_perfis)
        self.combo_perfis.trace_add("write", lambda *args: self.evento_perfil_selecionado())
        
        btn_novo = tk.Button(frame_perfil, text="➕ Novo Perfil", font=("Arial", 9, "bold"), bd=0, padx=8, command=self.janela_novo_perfil)
        btn_novo.grid(row=0, column=2, sticky="w", padx=15, pady=5)
        self.botoes_destaque.append(btn_novo)
        
        # Linha do Tema Visual (O SEU PEDIDO)
        lbl_t = tk.Label(frame_perfil, text="Tema Visual:")
        lbl_t.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_t)
        
        self.str_tema = tk.StringVar(value="Dark Purple Edition")
        self.dropdown_temas = tk.OptionMenu(frame_perfil, self.str_tema, *list(TEMAS.keys()))
        self.dropdown_temas.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.option_menus.append(self.dropdown_temas)
        self.str_tema.trace_add("write", lambda *args: self.atualizar_tema_interface())
        
        # --- SEÇÃO 2: CONFIGURAÇÕES DE DADOS ---
        frame_dados = tk.LabelFrame(self.root, text=" Credenciais e API Endpoints ", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_dados.pack(fill="x", padx=15, pady=5)
        frame_dados.columnconfigure(1, weight=1)
        self.label_frames_cards.append(frame_dados)
        
        # Notion Token + Olho
        lbl_d1 = tk.Label(frame_dados, text="Notion Token:")
        lbl_d1.grid(row=0, column=0, sticky="w", pady=6, padx=5)
        self.labels_muted.append(lbl_d1)
        self.ent_notion_token = tk.Entry(frame_dados, show="*")
        self.ent_notion_token.grid(row=0, column=1, sticky="ew", pady=6, padx=(5, 2))
        self.entries.append(self.ent_notion_token)
        
        self.btn_olho_notion = tk.Button(frame_dados, text="👁️", width=3, command=lambda: self.toggle_visibilidade(self.ent_notion_token, self.btn_olho_notion))
        self.btn_olho_notion.grid(row=0, column=2, pady=6, padx=(0, 5), sticky="w")
        self.botoes_secundarios.append(self.btn_olho_notion)
        
        # Notion ID
        lbl_d2 = tk.Label(frame_dados, text="Notion ID / DB:")
        lbl_d2.grid(row=1, column=0, sticky="w", pady=6, padx=5)
        self.labels_muted.append(lbl_d2)
        self.ent_notion_id = tk.Entry(frame_dados)
        self.ent_notion_id.grid(row=1, column=1, columnspan=2, sticky="ew", pady=6, padx=5)
        self.entries.append(self.ent_notion_id)
        
        # OpenRouter Key + Olho
        lbl_d3 = tk.Label(frame_dados, text="OpenRouter Key:")
        lbl_d3.grid(row=2, column=0, sticky="w", pady=6, padx=5)
        self.labels_muted.append(lbl_d3)
        self.ent_openrouter_key = tk.Entry(frame_dados, show="*")
        self.ent_openrouter_key.grid(row=2, column=1, sticky="ew", pady=6, padx=(5, 2))
        self.entries.append(self.ent_openrouter_key)
        
        self.btn_olho_or = tk.Button(frame_dados, text="👁️", width=3, command=lambda: self.toggle_visibilidade(self.ent_openrouter_key, self.btn_olho_or))
        self.btn_olho_or.grid(row=2, column=2, pady=6, padx=(0, 5), sticky="w")
        self.botoes_secundarios.append(self.btn_olho_or)
        
        # Deck Anki
        lbl_d4 = tk.Label(frame_dados, text="Nome do Deck Anki:")
        lbl_d4.grid(row=3, column=0, sticky="w", pady=6, padx=5)
        self.labels_muted.append(lbl_d4)
        self.ent_deck_name = tk.Entry(frame_dados)
        self.ent_deck_name.grid(row=3, column=1, columnspan=2, sticky="ew", pady=6, padx=5)
        self.entries.append(self.ent_deck_name)

        # --- SEÇÃO 3: SELEÇÃO DE INTELEGÊNCIA ARTIFICIAL ---
        frame_ia = tk.LabelFrame(self.root, text=" Configuração de Inteligência Artificial ", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_ia.pack(fill="x", padx=15, pady=10)
        frame_ia.columnconfigure(1, weight=1)
        self.label_frames_cards.append(frame_ia)
        
        lbl_ia1 = tk.Label(frame_ia, text="IA Principal:")
        lbl_ia1.grid(row=0, column=0, sticky="w", pady=6, padx=5)
        self.labels_muted.append(lbl_ia1)
        self.str_model_principal = tk.StringVar(value=MODELOS_PRINCIPAIS[0])
        self.menu_principal = tk.OptionMenu(frame_ia, self.str_model_principal, *MODELOS_PRINCIPAIS)
        self.menu_principal.grid(row=0, column=1, sticky="ew", pady=6, padx=5)
        self.option_menus.append(self.menu_principal)
        
        lbl_ia2 = tk.Label(frame_ia, text="IA Reserva (Plano B):")
        lbl_ia2.grid(row=1, column=0, sticky="w", pady=6, padx=5)
        self.labels_muted.append(lbl_ia2)
        self.str_model_fallback = tk.StringVar(value=MODELOS_RESERVA[0])
        self.menu_fallback = tk.OptionMenu(frame_ia, self.str_model_fallback, *MODELOS_RESERVA)
        self.menu_fallback.grid(row=1, column=1, sticky="ew", pady=6, padx=5)
        self.option_menus.append(self.menu_fallback)

        # --- SEÇÃO 4: BOTÕES DE ACÇÃO ---
        frame_botoes = tk.Frame(self.root, pady=5)
        frame_botoes.pack(fill="x", padx=15, pady=5)
        self.frames_principais.append(frame_botoes)
        
        self.btn_salvar = tk.Button(frame_botoes, text="💾 Guardar Configurações", height=2, font=("Arial", 10, "bold"), command=self.salvar_configuracoes_atuais)
        self.btn_salvar.pack(side="left", expand=True, fill="x", padx=5)
        self.botoes_secundarios.append(self.btn_salvar)
        
        self.btn_gerar = tk.Button(frame_botoes, text="🚀 Gerar Flashcards", height=2, font=("Arial", 10, "bold"), command=self.disparar_fluxo_geracao)
        self.btn_gerar.pack(side="left", expand=True, fill="x", padx=5)
        self.botoes_destaque.append(self.btn_gerar)
        
        # --- SEÇÃO 5: LOG CONSOLE ---
        self.lbl_log_title = tk.Label(self.root, text="Histórico de Execução e Logs do Sistema:", font=("Arial", 9))
        self.lbl_log_title.pack(anchor="w", padx=15, pady=(10,0))
        
        self.txt_log = scrolledtext.ScrolledText(self.root, height=11, font=("Consolas", 10), bd=1, relief="solid")
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        # Força aplicação inicial do tema padrão
        self.atualizar_tema_interface()
        self.log("🤖 Core Engine pronto. Selecione ou configure o seu perfil de estudos.")

    # ================= ENGINE DE TEMAS DINÂMICOS =================

    def atualizar_tema_interface(self):
        """Redesenha todos os componentes da janela em tempo real baseado no tema ativo"""
        tema_atual = self.str_tema.get()
        if tema_atual not in TEMAS: return
        cores = TEMAS[tema_atual]
        
        # 1. Altera frames principais e root
        for f in self.frames_principais:
            f.configure(bg=cores["fundo_principal"])
            
        # 2. Altera caixas de agrupamento (Cards)
        for lf in self.label_frames_cards:
            lf.configure(bg=cores["fundo_card"], fg=cores["destaque"], bd=1, relief="solid")
            
        # 3. Altera as Labels de texto
        for lbl in self.labels_normais:
            lbl.configure(bg=cores["fundo_card"], fg=cores["texto"])
        for lbl_m in self.labels_muted:
            lbl_m.configure(bg=cores["fundo_card"], fg=cores["texto_muted"])
            
        self.lbl_log_title.configure(bg=cores["fundo_principal"], fg=cores["texto_muted"])
            
        # 4. Altera campos de digitação (Inputs)
        caret_color = "black" if tema_atual == "Steel Minimalist" else "white"
        for ent in self.entries:
            ent.configure(bg=cores["fundo_principal"], fg=cores["texto"], bd=1, relief="solid", insertbackground=caret_color)
            
        # 5. Altera botões principais (Destaques)
        texto_botao_principal = "#000000" if tema_atual == "Cyberpunk Terminal" else "#ffffff"
        for btn in self.botoes_destaque:
            btn.configure(bg=cores["destaque"], fg=texto_botao_principal, activebackground=cores["destaque_hover"], activeforeground=texto_botao_principal)
            
        # 6. Altera botões secundários (Olho / Guardar)
        bg_secundario = "#e5e7eb" if tema_atual == "Steel Minimalist" else cores["fundo_principal"]
        for btn_s in self.botoes_secundarios:
            btn_s.configure(bg=bg_secundario, fg=cores["texto"], activebackground=cores["fundo_card"], activeforeground=cores["texto"], bd=1, relief="solid")
            
        # 7. Altera menus Dropdown
        for m in self.option_menus:
            m.configure(bg=cores["fundo_principal"], fg=cores["texto"], activebackground=cores["destaque"], activeforeground="#ffffff", bd=1, relief="flat")
            m["menu"].configure(bg=cores["fundo_card"], fg=cores["texto"], activebackground=cores["destaque"])
            
        # 8. Altera a caixa preta do terminal
        self.txt_log.configure(bg=cores["console_bg"], fg=cores["console_fg"], insertbackground=caret_color)

    def toggle_visibilidade(self, campo_entry, botao):
        if campo_entry.cget("show") == "*":
            campo_entry.config(show="")
            botao.config(text="🙈")
        else:
            campo_entry.config(show="*")
            botao.config(text="👁️")

    def log(self, mensagem):
        self.txt_log.insert(tk.END, f"{mensagem}\n")
        self.txt_log.see(tk.END)

    # ================= PERSISTÊNCIA MULTIPERFIL (JSON) =================

    def atualizar_lista_perfis(self, selecionar_nome=None):
        perfis = [f.replace(".json", "") for f in os.listdir("perfis") if f.endswith(".json")]
        menu = self.dropdown_perfis["menu"]
        menu.delete(0, "end")
        for p in perfis:
            menu.add_command(label=p, command=lambda v=p: self.combo_perfis.set(v))
            
        if perfis:
            if selecionar_nome in perfis:
                self.combo_perfis.set(selecionar_nome)
            else:
                self.combo_perfis.set(perfis[0])
        else:
            self.limpar_campos()

    def evento_perfil_selecionado(self):
        nome_perfil = self.combo_perfis.get()
        if not nome_perfil: return
        caminho = os.path.join("perfis", f"{nome_perfil}.json")
        if not os.path.exists(caminho): return
        
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
            
            self.str_model_principal.set(config.get("AI_MODEL", MODELOS_PRINCIPAIS[0]))
            self.str_model_fallback.set(config.get("AI_MODEL_FALLBACK", MODELOS_RESERVA[0]))
            
            # Recupera o tema salvo no JSON ou assume o padrão Purple
            tema_salvo = config.get("THEME", "Dark Purple Edition")
            self.str_tema.set(tema_salvo)
            
            self.log(f"📁 Perfil '{nome_perfil}' carregado com Sucesso. Layout: [{tema_salvo}]")
        except Exception as e:
            self.log(f"❌ Falha de carregamento do perfil: {e}")

    def limpar_campos(self):
        self.ent_notion_token.delete(0, tk.END)
        self.ent_notion_id.delete(0, tk.END)
        self.ent_openrouter_key.delete(0, tk.END)
        self.ent_deck_name.delete(0, tk.END)

    def janela_novo_perfil(self):
        popup = tk.Toplevel(self.root)
        popup.title("Novo Perfil")
        popup.geometry("320x140")
        popup.grab_set()
        popup.resizable(False, False)
        
        # Estilização temporária rápida do popup herdadando o fundo escuro/claro atual
        cores_atuais = TEMAS[self.str_tema.get()]
        popup.configure(bg=cores_atuais["fundo_card"])
        
        tk.Label(popup, text="Nome da Matéria / Perfil:", bg=cores_atuais["fundo_card"], fg=cores_atuais["texto"]).pack(pady=10)
        ent_nome = tk.Entry(popup, bg=cores_atuais["fundo_principal"], fg=cores_atuais["texto"], bd=1, relief="solid", width=28, insertbackground="white")
        ent_nome.pack(pady=5)
        ent_nome.focus()
        
        def confirmar():
            nome = ent_nome.get().strip()
            if not nome or f"{nome}.json" in os.listdir("perfis"):
                messagebox.showerror("Erro", "Nome inválido ou duplicado.", parent=popup)
                return
            
            modelo = {
                "NOTION_TOKEN": "SEU_TOKEN_AQUI",
                "NOTION_DATABASE_ID": "SEU_ID_NOTION_AQUI",
                "OPENROUTER_API_KEY": "SUA_KEY_AQUI",
                "DECK_NAME": nome,
                "AI_MODEL": MODELOS_PRINCIPAIS[0],
                "AI_MODEL_FALLBACK": MODELOS_RESERVA[0],
                "THEME": self.str_tema.get() # Inicializa com o tema atual da tela
            }
            with open(os.path.join("perfis", f"{nome}.json"), "w", encoding="utf-8") as f:
                json.dump(modelo, f, indent=4, ensure_ascii=False)
                
            self.log(f"✨ Perfil '{nome}' criado.")
            popup.destroy()
            self.atualizar_lista_perfis(selecionar_nome=nome)
            
        tk.Button(popup, text="Criar", bg=cores_atuais["destaque"], fg="white", bd=0, padx=15, command=confirmar).pack(pady=10)

    def salvar_configuracoes_atuais(self):
        nome_perfil = self.combo_perfis.get()
        if not nome_perfil: return
            
        config = {
            "NOTION_TOKEN": self.ent_notion_token.get().strip(),
            "NOTION_DATABASE_ID": self.ent_notion_id.get().strip(),
            "OPENROUTER_API_KEY": self.ent_openrouter_key.get().strip(),
            "DECK_NAME": self.ent_deck_name.get().strip(),
            "AI_MODEL": self.str_model_principal.get().strip(),
            "AI_MODEL_FALLBACK": self.str_model_fallback.get().strip(),
            "THEME": self.str_tema.get() # SALVA O TEMA ATIVO NO ARQUIVO JSON!
        }
        
        with open(os.path.join("perfis", f"{nome_perfil}.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
        self.log(f"💾 Perfil 'perfis/{nome_perfil}.json' guardado e sincronizado com o tema [{self.str_tema.get()}].")
        messagebox.showinfo("Sucesso", f"Definições de '{nome_perfil}' foram salvas com sucesso!")

    # ================= FLUXO ASSÍNCRONO DE EXECUÇÃO =================

    def disparar_fluxo_geracao(self):
        nome_perfil = self.combo_perfis.get()
        if not nome_perfil: return
        self.btn_gerar.config(state="disabled")
        threading.Thread(target=self.fluxo_geracao_background, args=(nome_perfil,), daemon=True).start()

    def fluxo_geracao_background(self, nome_perfil):
        try:
            token = self.ent_notion_token.get().strip()
            id_notion = self.ent_notion_id.get().strip()
            api_key_or = self.ent_openrouter_key.get().strip()
            deck_name = self.ent_deck_name.get().strip()
            model_principal = self.str_model_principal.get().strip()
            model_fallback = self.str_model_fallback.get().strip()
            
            self.log(f"\n🚀 [EXECUÇÃO] Iniciando varredura para o perfil: {nome_perfil}")
            
            caminho_hist = os.path.join("historicos", f"{nome_perfil}_historico.txt")
            historico = set()
            if os.path.exists(caminho_hist):
                with open(caminho_hist, "r", encoding="utf-8") as f:
                    historico = set(l.strip() for l in f if l.strip())
            
            self.log("📖 Lendo blocos novos da página do Notion...")
            url = f"https://api.notion.com/v1/blocks/{id_notion}/children"
            headers = {
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, params={"page_size": 100})
            if response.status_code != 200:
                self.log(f"❌ Erro de API no Notion ({response.status_code}): {response.text}")
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
                self.log(f"✨ Tudo sincronizado! Nenhuma anotação inédita no perfil '{nome_perfil}'.")
                return
                
            self.log(f"💡 Foram localizadas {len(blocos_novos)} novas linhas estruturadas.")
            texto_para_ia = "\n".join([item["texto"] for item in blocos_novos])
            
            client = OpenAI(api_key=api_key_or, base_url="https://openrouter.ai/api/v1")
            prompt_sistema = """
            Você é um assistente especialista em concursos de TI e criação de flashcards para o Anki.
            Seu objetivo é receber anotações de estudo e transformá-las em flashcards no formato de Omissão de Palavras (Cloze Deletion).
            Regras:
            1. Esconda apenas comandos, parâmetros ou termos técnicos usando {{c1::termo}}.
            2. Seja extremamente direto. Responda obrigatoriamente com um OBJETO JSON contendo uma chave chamada "cards".
            Exemplo: {"cards": [{"texto": "O comando {{c1::ls -la}} lista arquivos ocultos."}]}
            """
            
            lista_de_cards = []
            self.log(f"🤖 Solicitando geração via inteligência principal ({model_principal})...")
            
            try:
                res = client.chat.completions.create(
                    model=model_principal,
                    messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_para_ia}],
                    temperature=0.2, max_tokens=2000, response_format={'type': 'json_object'}
                )
                lista_de_cards = json.loads(res.choices[0].message.content).get("cards", [])
            except Exception as err_principal:
                self.log(f"⚠️ Alerta: Modelo principal falhou/sem saldo: {err_principal}")
                self.log(f"🔄 [CONTINGÊNCIA] Acionando rota inteligente reserva: {model_fallback}...")
                try:
                    res = client.chat.completions.create(
                        model=model_fallback,
                        messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_para_ia}],
                        temperature=0.2, max_tokens=2000, response_format={'type': 'json_object'}
                    )
                    lista_de_cards = json.loads(res.choices[0].message.content).get("cards", [])
                    self.log("✅ Rota reserva salvou a execução com sucesso!")
                except Exception as err_fallback:
                    self.log(f"❌ Erro Crítico: A IA de contingência também falhou: {err_fallback}")
                    return
            
            if not lista_de_cards:
                self.log("⚠️ Nenhuma estrutura de card pôde ser extraída.")
                return
                
            self.log(f"📥 Processando {len(lista_de_cards)} cards gerados. Injetando no Anki Connect...")
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
                            "fields": {"Texto": card["texto"]}, "tags": ["concursos", "theme_forge"]
                        }
                    }
                }
                try:
                    res_anki = requests.post(ANKI_CONNECT_URL, json=payload).json()
                    if not res_anki.get("error"):
                        cards_com_sucesso += 1
                except:
                    self.log("❌ Falha crítica: O Anki Connect recusou a conexão. O seu Anki está aberto?")
                    return
                    
            if cards_com_sucesso > 0:
                with open(caminho_hist, "a", encoding="utf-8") as f:
                    for item in blocos_novos:
                        f.write(f"{item['hash']}\n")
                self.log(f"💾 Sucesso absoluto! {cards_com_sucesso} flashcards criados e histórico de '{nome_perfil}' protegido.")
                messagebox.showinfo("Concluído", f"{cards_com_sucesso} flashcards foram enviados para o Anki!")
            else:
                self.log("⚠ Nenhum card pôde ser inserido no Anki (possível conteúdo duplicado).")
                
        except Exception as e_geral:
            self.log(f"❌ Falha inesperada no motor: {e_geral}")
        finally:
            self.btn_gerar.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = CardForgeThemeApp(root)
    root.mainloop()