import tkinter as tk
from tkinter import scrolledtext, messagebox
from models.model import TEMAS, MODELOS_PRINCIPAIS, MODELOS_RESERVA

class CardForgeView:
    def __init__(self, root):
        self.root = root
        self.root.title("CardForge v6.0 - MVC Engine Edition")
        self.root.geometry("680x810")
        
        # Listas de componentes para renderização dinâmica de temas
        self.frames_principais, self.label_frames_cards = [], []
        self.labels_normais, self.labels_muted, self.entries = [], [], []
        self.botoes_destaque, self.botoes_secundarios, self.option_menus = [], [], []
        
        self.criar_interface_estilizada()

    def criar_interface_estilizada(self):
        self.frames_principais.append(self.root)
        
        # --- SEÇÃO 1: PERFIL E TEMA ---
        frame_perfil = tk.LabelFrame(self.root, text=" Configurações de Ambiente ", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_perfil.pack(fill="x", padx=15, pady=10)
        self.label_frames_cards.append(frame_perfil)
        
        lbl_p = tk.Label(frame_perfil, text="Perfil Ativo:")
        lbl_p.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_p)
        
        self.combo_perfis = tk.StringVar()
        self.dropdown_perfis = tk.OptionMenu(frame_perfil, self.combo_perfis, "")
        self.dropdown_perfis.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.option_menus.append(self.dropdown_perfis)
        
        self.btn_novo = tk.Button(frame_perfil, text="➕ Novo Perfil", font=("Arial", 9, "bold"), bd=0, padx=8)
        self.btn_novo.grid(row=0, column=2, sticky="w", padx=15, pady=5)
        self.botoes_destaque.append(self.btn_novo)
        
        lbl_t = tk.Label(frame_perfil, text="Tema Visual:")
        lbl_t.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_t)
        
        self.str_tema = tk.StringVar(value="Dark Purple Edition")
        self.dropdown_temas = tk.OptionMenu(frame_perfil, self.str_tema, *list(TEMAS.keys()))
        self.dropdown_temas.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.option_menus.append(self.dropdown_temas)
        
        # --- SEÇÃO 2: CREDENCIAIS ---
        frame_dados = tk.LabelFrame(self.root, text=" Credenciais e API Endpoints ", font=("Arial", 10, "bold"), padx=10, pady=10)
        frame_dados.pack(fill="x", padx=15, pady=5)
        frame_dados.columnconfigure(1, weight=1)
        self.label_frames_cards.append(frame_dados)
        
        lbl_d1 = tk.Label(frame_dados, text="Notion Token:")
        lbl_d1.grid(row=0, column=0, sticky="w", pady=6, padx=5)
        self.labels_muted.append(lbl_d1)
        self.ent_notion_token = tk.Entry(frame_dados, show="*")
        self.ent_notion_token.grid(row=0, column=1, sticky="ew", pady=6, padx=(5, 2))
        self.entries.append(self.ent_notion_token)
        
        self.btn_olho_notion = tk.Button(frame_dados, text="👁️", width=3)
        self.btn_olho_notion.grid(row=0, column=2, pady=6, padx=(0, 5), sticky="w")
        self.botoes_secundarios.append(self.btn_olho_notion)
        
        lbl_d2 = tk.Label(frame_dados, text="Notion ID / DB:")
        lbl_d2.grid(row=1, column=0, sticky="w", pady=6, padx=5)
        self.labels_muted.append(lbl_d2)
        self.ent_notion_id = tk.Entry(frame_dados)
        self.ent_notion_id.grid(row=1, column=1, columnspan=2, sticky="ew", pady=6, padx=5)
        self.entries.append(self.ent_notion_id)
        
        lbl_d3 = tk.Label(frame_dados, text="OpenRouter Key:")
        lbl_d3.grid(row=2, column=0, sticky="w", pady=6, padx=5)
        self.labels_muted.append(lbl_d3)
        self.ent_openrouter_key = tk.Entry(frame_dados, show="*")
        self.ent_openrouter_key.grid(row=2, column=1, sticky="ew", pady=6, padx=(5, 2))
        self.entries.append(self.ent_openrouter_key)
        
        self.btn_olho_or = tk.Button(frame_dados, text="👁️", width=3)
        self.btn_olho_or.grid(row=2, column=2, pady=6, padx=(0, 5), sticky="w")
        self.botoes_secundarios.append(self.btn_olho_or)
        
        lbl_d4 = tk.Label(frame_dados, text="Nome do Deck Anki:")
        lbl_d4.grid(row=3, column=0, sticky="w", pady=6, padx=5)
        self.labels_muted.append(lbl_d4)
        self.ent_deck_name = tk.Entry(frame_dados)
        self.ent_deck_name.grid(row=3, column=1, columnspan=2, sticky="ew", pady=6, padx=5)
        self.entries.append(self.ent_deck_name)

        # --- SEÇÃO 3: INTELIGÊNCIA ARTIFICIAL ---
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

        # --- SEÇÃO 4: BOTÕES DE AÇÃO ---
        frame_botoes = tk.Frame(self.root, pady=5)
        frame_botoes.pack(fill="x", padx=15, pady=5)
        self.frames_principais.append(frame_botoes)
        
        self.btn_salvar = tk.Button(frame_botoes, text="💾 Guardar Configurações", height=2, font=("Arial", 10, "bold"))
        self.btn_salvar.pack(side="left", expand=True, fill="x", padx=5)
        self.botoes_secundarios.append(self.btn_salvar)
        
        self.btn_gerar = tk.Button(frame_botoes, text="🚀 Gerar Flashcards", height=2, font=("Arial", 10, "bold"))
        self.btn_gerar.pack(side="left", expand=True, fill="x", padx=5)
        self.botoes_destaque.append(self.btn_gerar)
        
        # --- SEÇÃO 5: LOG CONSOLE ---
        self.lbl_log_title = tk.Label(self.root, text="Histórico de Execução e Logs do Sistema:", font=("Arial", 9))
        self.lbl_log_title.pack(anchor="w", padx=15, pady=(10,0))
        
        self.txt_log = scrolledtext.ScrolledText(self.root, height=11, font=("Consolas", 10), bd=1, relief="solid")
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(5, 15))

    def atualizar_tema_interface(self):
        tema_atual = self.str_tema.get()
        if tema_atual not in TEMAS: return
        cores = TEMAS[tema_atual]
        
        for f in self.frames_principais: f.configure(bg=cores["fundo_principal"])
        for lf in self.label_frames_cards: lf.configure(bg=cores["fundo_card"], fg=cores["destaque"], bd=1, relief="solid")
        for lbl in self.labels_normais: lbl.configure(bg=cores["fundo_card"], fg=cores["texto"])
        for lbl_m in self.labels_muted: lbl_m.configure(bg=cores["fundo_card"], fg=cores["texto_muted"])
        self.lbl_log_title.configure(bg=cores["fundo_principal"], fg=cores["texto_muted"])
        
        caret_color = "black" if tema_atual == "Steel Minimalist" else "white"
        for ent in self.entries: ent.configure(bg=cores["fundo_principal"], fg=cores["texto"], bd=1, relief="solid", insertbackground=caret_color)
        
        texto_botao = "#000000" if tema_atual == "Cyberpunk Terminal" else "#ffffff"
        for btn in self.botoes_destaque: btn.configure(bg=cores["destaque"], fg=texto_botao, activebackground=cores["destaque_hover"], activeforeground=texto_botao)
        
        bg_secundario = "#e5e7eb" if tema_atual == "Steel Minimalist" else cores["fundo_principal"]
        for btn_s in self.botoes_secundarios: btn_s.configure(bg=bg_secundario, fg=cores["texto"], activebackground=cores["fundo_card"], activeforeground=cores["texto"], bd=1, relief="solid")
        
        for m in self.option_menus:
            m.configure(bg=cores["fundo_principal"], fg=cores["texto"], activebackground=cores["destaque"], activeforeground="#ffffff", bd=1, relief="flat")
            m["menu"].configure(bg=cores["fundo_card"], fg=cores["texto"], activebackground=cores["destaque"])
            
        self.txt_log.configure(bg=cores["console_bg"], fg=cores["console_fg"], insertbackground=caret_color)

    def log(self, mensagem):
        self.txt_log.insert(tk.END, f"{mensagem}\n")
        self.txt_log.see(tk.END)

    def toggle_visibilidade(self, campo, botao):
        if campo.cget("show") == "*":
            campo.config(show="")
            botao.config(text="🙈")
        else:
            campo.config(show="*")
            botao.config(text="👁️")

    def abrir_popup_novo_perfil(self, confirmar_callback):
        popup = tk.Toplevel(self.root)
        popup.title("Novo Perfil")
        popup.geometry("320x140")
        popup.grab_set()
        popup.resizable(False, False)
        
        cores_atuais = TEMAS[self.str_tema.get()]
        popup.configure(bg=cores_atuais["fundo_card"])
        
        tk.Label(popup, text="Nome da Matéria / Perfil:", bg=cores_atuais["fundo_card"], fg=cores_atuais["texto"]).pack(pady=10)
        ent_nome = tk.Entry(popup, bg=cores_atuais["fundo_principal"], fg=cores_atuais["texto"], bd=1, relief="solid", width=28, insertbackground="white")
        ent_nome.pack(pady=5)
        ent_nome.focus()
        
        tk.Button(popup, text="Criar", bg=cores_atuais["destaque"], fg="white", bd=0, padx=15, command=lambda: confirmar_callback(ent_nome.get().strip(), popup)).pack(pady=10)