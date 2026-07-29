# views/view.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from views.design_system import TEMAS, FONTS, SPACING
# Importa as listas de modelos diretamente do seu Model centralizado
from models.model import MODELOS_PRINCIPAIS, MODELOS_RESERVA

class CardForgeView:
    def __init__(self, root):
        self.root = root
        self.root.title("CardForge v6.0")
        self.root.geometry("700x860")
        
        # Listas de componentes para renderização dinâmica de temas
        self.frames_principais = []
        self.label_frames_cards = []
        self.labels_normais = []
        self.labels_muted = []
        self.entries = []
        self.botoes_destaque = []
        self.botoes_secundarios = []
        self.comboboxes = []
        
        # Variáveis de controle de estado da interface
        self.str_tema = tk.StringVar(value="Dark Purple Edition")
        self.str_perfil_ativo = tk.StringVar()
        
        self.criar_interface_estilizada()

    def criar_interface_estilizada(self):
        self.frames_principais.append(self.root)
        padx_janela = SPACING.get("padding_janela", 15)
        gap_medio = SPACING.get("gap_medio", 10)
        
        # =========================================================================
        # SEÇÃO 1: CONFIGURAÇÕES DE AMBIENTE (PERFIL, CHAVES E MODELOS DE IA)
        # =========================================================================
        frame_perfil = tk.LabelFrame(self.root, text=" Configurações de Ambiente ", font=FONTS.get("titulo_secao"), padx=10, pady=10)
        frame_perfil.pack(fill="x", padx=padx_janela, pady=gap_medio)
        self.label_frames_cards.append(frame_perfil)
        
        # Linha 0: Seleção de Perfil, Criar, Editar e Excluir Perfil
        lbl_perfil = tk.Label(frame_perfil, text="Perfil / Matéria:")
        lbl_perfil.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_perfil)
        
        self.cb_perfil = ttk.Combobox(frame_perfil, textvariable=self.str_perfil_ativo, state="readonly", width=22)
        self.cb_perfil.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.comboboxes.append(self.cb_perfil)
        
        # Container horizontal invisível para agrupar as ações
        frame_acoes_perfil = tk.Frame(frame_perfil)
        frame_acoes_perfil.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.frames_principais.append(frame_acoes_perfil)
        
        self.btn_novo_perfil = tk.Button(frame_acoes_perfil, text="➕ Novo", font=("Arial", 9, "bold"))
        self.btn_novo_perfil.pack(side="left", padx=2)
        self.botoes_secundarios.append(self.btn_novo_perfil)
        
        self.btn_editar_perfil = tk.Button(frame_acoes_perfil, text="✏️ Editar", font=("Arial", 9, "bold"))
        self.btn_editar_perfil.pack(side="left", padx=2)
        self.botoes_secundarios.append(self.btn_editar_perfil)
        
        self.btn_excluir_perfil = tk.Button(frame_acoes_perfil, text="❌ Excluir", font=("Arial", 9, "bold"))
        self.btn_excluir_perfil.pack(side="left", padx=2)
        self.botoes_secundarios.append(self.btn_excluir_perfil)
        
        # Linha 1: Notion Token
        lbl_notion = tk.Label(frame_perfil, text="Notion Token:")
        lbl_notion.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_notion)
        
        self.ent_notion_token = tk.Entry(frame_perfil, width=50)
        self.ent_notion_token.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.entries.append(self.ent_notion_token)
        
        # Linha 2: Notion Database ID
        lbl_db = tk.Label(frame_perfil, text="Database ID:")
        lbl_db.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_db)
        
        self.ent_database_id = tk.Entry(frame_perfil, width=50)
        self.ent_database_id.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.entries.append(self.ent_database_id)
        
        # Linha 3: OpenRouter API Key (Com botão de espiar/ocultar senha)
        lbl_key = tk.Label(frame_perfil, text="OpenRouter Key:")
        lbl_key.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_key)
        
        self.ent_api_key = tk.Entry(frame_perfil, width=42, show="*")
        self.ent_api_key.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.entries.append(self.ent_api_key)
        
        self.btn_toggle_key = tk.Button(frame_perfil, text="👁️", width=3, command=self.toggle_senha_api)
        self.btn_toggle_key.grid(row=3, column=2, sticky="w", padx=5, pady=5)
        self.botoes_secundarios.append(self.btn_toggle_key)
        
        # Linha 4: Nome do Deck do Anki
        lbl_deck = tk.Label(frame_perfil, text="Nome do Deck:")
        lbl_deck.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_deck)
        
        self.ent_deck_name = tk.Entry(frame_perfil, width=50)
        self.ent_deck_name.grid(row=4, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.entries.append(self.ent_deck_name)
        
        # 🌟 INTEGRAÇÃO NOVO CAMPO - Linha 5: Dropdown do Modelo Principal de IA
        lbl_mod_p = tk.Label(frame_perfil, text="Modelo Principal:")
        lbl_mod_p.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_mod_p)
        
        self.cb_modelo_principal = ttk.Combobox(frame_perfil, values=MODELOS_PRINCIPAIS, state="readonly", width=40)
        self.cb_modelo_principal.grid(row=5, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.cb_modelo_principal.set(MODELOS_PRINCIPAIS[0])
        self.comboboxes.append(self.cb_modelo_principal)
        
        # 🌟 INTEGRAÇÃO NOVO CAMPO - Linha 6: Dropdown do Modelo Reserva (Fallback)
        lbl_mod_r = tk.Label(frame_perfil, text="Modelo Reserva:")
        lbl_mod_r.grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_mod_r)
        
        self.cb_modelo_reserva = ttk.Combobox(frame_perfil, values=MODELOS_RESERVA, state="readonly", width=40)
        self.cb_modelo_reserva.grid(row=6, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.cb_modelo_reserva.set(MODELOS_RESERVA[0])
        self.comboboxes.append(self.cb_modelo_reserva)
        
        # Linha 7: Seleção de Tema e Botão de Salvar Configurações do Perfil
        lbl_tema = tk.Label(frame_perfil, text="Tema Visual:")
        lbl_tema.grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.labels_normais.append(lbl_tema)
        
        self.cb_tema = ttk.Combobox(frame_perfil, textvariable=self.str_tema, values=list(TEMAS.keys()), state="readonly", width=25)
        self.cb_tema.grid(row=7, column=1, sticky="w", padx=5, pady=5)
        self.comboboxes.append(self.cb_tema)
        
        self.btn_salvar_perfil = tk.Button(frame_perfil, text="💾 Salvar Perfil", font=("Arial", 10, "bold"))
        self.btn_salvar_perfil.grid(row=7, column=2, sticky="e", padx=5, pady=5)
        self.botoes_destaque.append(self.btn_salvar_perfil)
        
        frame_perfil.grid_columnconfigure(1, weight=1)

        # =========================================================================
        # SEÇÃO 2: ÁREA DE ENTRADA DO MATERIAL DE ESTUDO
        # =========================================================================
        frame_botoes = tk.Frame(self.root, pady=5)
        frame_botoes.pack(fill="x", padx=15, pady=5)
        self.frames_principais.append(frame_botoes)
        
        self.btn_salvar = tk.Button(frame_botoes, text="💾 Guardar Configurações", height=2, font=("Arial", 9, "bold"))
        self.btn_salvar.pack(side="left", expand=True, fill="x", padx=2)
        self.botoes_secundarios.append(self.btn_salvar)
        
        self.btn_gerar_notion = tk.Button(frame_botoes, text="✨ Sincronizar via Notion", height=2, font=("Arial", 9, "bold"))
        self.btn_gerar_notion.pack(side="left", expand=True, fill="x", padx=2)
        self.botoes_destaque.append(self.btn_gerar_notion)

        self.btn_gerar_manual = tk.Button(frame_botoes, text="📝 Converter Texto da Tela", height=2, font=("Arial", 9, "bold"))
        self.btn_gerar_manual.pack(side="left", expand=True, fill="x", padx=2)
        self.botoes_destaque.append(self.btn_gerar_manual)

        # =========================================================================
        # SEÇÃO 3: CONSOLE DE LOGS EM TEMPO REAL
        # =========================================================================
        self.lbl_input_title = tk.Label(self.root, text="Material de Estudo para Conversão Manual:", font=("Arial", 9))
        self.lbl_input_title.pack(anchor="w", padx=15, pady=(5,0))
        
        # Caixa do meio (onde você digita o texto manual)
        self.txt_input = scrolledtext.ScrolledText(self.root, height=8, font=("Arial", 10), bd=1, relief="solid")
        self.txt_input.pack(fill="x", padx=15, pady=(5, 5))

        self.lbl_log_title = tk.Label(self.root, text="Histórico de Execução e Logs do Sistema:", font=("Arial", 9))
        self.lbl_log_title.pack(anchor="w", padx=15, pady=(5,0))
        
        # Caixa do fundo (onde aparecem as mensagens roxas de sucesso/erro)
        self.txt_log = scrolledtext.ScrolledText(self.root, height=8, font=("Consolas", 10), bd=1, relief="solid")
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(5, 15))

    # =========================================================================
    # ENGENHARIA DE MÉTODOS DE DADOS DA INTERFACE
    # =========================================================================
    def toggle_senha_api(self):
        """Alterna a visibilidade da OpenRouter Key."""
        if self.ent_api_key.cget("show") == "*":
            self.ent_api_key.config(show="")
            self.btn_toggle_key.config(text="🔒")
        else:
            self.ent_api_key.config(show="*")
            self.btn_toggle_key.config(text="👁️")

    def toggle_visibilidade(self, campo_entry, botao_clicado):
        """Método genérico que o seu Controller usa para alternar senhas."""
        if campo_entry.cget("show") == "*":
            campo_entry.config(show="")
            botao_clicado.config(text="🔒")
        else:
            campo_entry.config(show="*")
            botao_clicado.config(text="👁️")

    def log(self, mensagem):
        """Redireciona as mensagens corretamente para o seu novo txt_log."""
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, f"{mensagem}\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")
        self.root.update_idletasks()

    def limpar_console(self):
        """Limpa o seu histórico de logs atualizado."""
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", tk.END)
        self.txt_log.config(state="disabled")

    def obter_dados_campos(self):
        """
        Coleta e empacota 100% dos dados da tela em um dicionário padronizado.
        Garante que os novos modelos selecionados vão para o JSON!
        """
        return {
            "NOTION_TOKEN": self.ent_notion_token.get().strip(),
            "NOTION_DATABASE_ID": self.ent_database_id.get().strip(),
            "OPENROUTER_API_KEY": self.ent_api_key.get().strip(),
            "DECK_NAME": self.ent_deck_name.get().strip(),
            "AI_MODEL": self.cb_modelo_principal.get(),
            "AI_MODEL_FALLBACK": self.cb_modelo_reserva.get(),
            "THEME": self.str_tema.get()
        }

    def preencher_campos(self, dados):
        """Preenche a tela com os dados carregados do perfil ativo."""
        if not dados:
            return
        
        # Limpa os campos antes da injeção
        self.ent_notion_token.delete(0, tk.END)
        self.ent_database_id.delete(0, tk.END)
        self.ent_api_key.delete(0, tk.END)
        self.ent_deck_name.delete(0, tk.END)
        
        # Insere as strings de texto
        self.ent_notion_token.insert(0, dados.get("NOTION_TOKEN", ""))
        self.ent_database_id.insert(0, dados.get("NOTION_DATABASE_ID", ""))
        self.ent_api_key.insert(0, dados.get("OPENROUTER_API_KEY", ""))
        self.ent_deck_name.insert(0, dados.get("DECK_NAME", ""))
        
        # Restaura a seleção do Modelo Principal
        mod_p = dados.get("AI_MODEL")
        if mod_p in MODELOS_PRINCIPAIS:
            self.cb_modelo_principal.set(mod_p)
        else:
            self.cb_modelo_principal.set(MODELOS_PRINCIPAL[0])
            
        # Restaura a seleção do Modelo Reserva
        mod_r = dados.get("AI_MODEL_FALLBACK")
        if mod_r in MODELOS_RESERVA:
            self.cb_modelo_reserva.set(mod_r)
        else:
            self.cb_modelo_reserva.set(MODELOS_RESERVA[0])

        # Seta o tema salvo no perfil
        tema_salvo = dados.get("THEME", "Dark Purple Edition")
        if tema_salvo in TEMAS:
            self.str_tema.set(tema_salvo)
            self.atualizar_tema_visual()

    def abrir_popup_novo_perfil(self, confirmar_callback):
        popup = tk.Toplevel(self.root)
        popup.title("Novo Perfil")
        popup.geometry("340x150")
        popup.grab_set()
        popup.resizable(False, False)
        
        cores_atuais = TEMAS[self.str_tema.get()]
        popup.configure(bg=cores_atuais["fundo_card"])
        
        tk.Label(popup, text="Nome da Matéria / Perfil:", bg=cores_atuais["fundo_card"], fg=cores_atuais["texto"], font=("Arial", 10, "bold")).pack(pady=10)
        ent_nome = tk.Entry(popup, bg=cores_atuais["fundo_principal"], fg=cores_atuais["texto"], bd=1, relief="solid", width=30, insertbackground="white")
        ent_nome.pack(pady=5)
        ent_nome.focus()
        
        def acao_confirmar():
            nome = ent_nome.get().strip()
            if nome:
                confirmar_callback(nome, popup)
            else:
                messagebox.showwarning("Aviso", "O nome do perfil não pode ser vazio!", parent=popup)

        tk.Button(popup, text="Criar Perfil", bg=cores_atuais["destaque"], fg="white", bd=0, padx=15, pady=5, font=("Arial", 9, "bold"), command=acao_confirmar).pack(pady=10)

    def atualizar_tema_visual(self):
        """Gerencia e aplica tokens de cores do design system dinamicamente."""
        nome_tema = self.str_tema.get()
        if nome_tema not in TEMAS:
            return
            
        cores = TEMAS[nome_tema]
        
        for frame in self.frames_principais:
            frame.configure(bg=cores["fundo_principal"])
            
        for tf in self.label_frames_cards:
            tf.configure(bg=cores["fundo_card"], fg=cores["texto"], bd=1, relief="solid")
            
        for lbl in self.labels_normais:
            lbl.configure(bg=cores["fundo_card"], fg=cores["texto"])
            
        for lbl_m in self.labels_muted:
            lbl_m.configure(bg=cores["fundo_card"], fg=cores["texto_muted"])
            
        for entry in self.entries:
            entry.configure(bg=cores["fundo_principal"], fg=cores["texto"], bd=1, relief="solid", insertbackground=cores["texto"])
            
        for btn in self.botoes_destaque:
            btn.configure(bg=cores["destaque"], fg="white", activebackground=cores["destaque_hover"], activeforeground="white", bd=0, cursor="hand2")
            
        for btn_s in self.botoes_secundarios:
            btn_s.configure(bg=cores["fundo_principal"], fg=cores["texto"], activebackground=cores["fundo_card"], activeforeground=cores["texto"], bd=1, relief="solid", cursor="hand2")
            
        self.txt_input.configure(bg=cores["fundo_principal"], fg=cores["texto"], insertbackground=cores["texto"])
        self.txt_log.configure(bg=cores["console_bg"], fg=cores["console_fg"], insertbackground=cores["texto"])
        
    def abrir_popup_editar_perfil(self, nome_atual, confirmar_callback):
        popup = tk.Toplevel(self.root)
        popup.title("Editar Nome do Perfil")
        popup.geometry("340x150")
        popup.grab_set()
        popup.resizable(False, False)
        
        cores_atuais = TEMAS[self.str_tema.get()]
        popup.configure(bg=cores_atuais["fundo_card"])
        
        tk.Label(popup, text=f"Novo nome para '{nome_atual}':", bg=cores_atuais["fundo_card"], fg=cores_atuais["texto"], font=("Arial", 10, "bold")).pack(pady=10)
        ent_nome = tk.Entry(popup, bg=cores_atuais["fundo_principal"], fg=cores_atuais["texto"], bd=1, relief="solid", width=30, insertbackground="white")
        ent_nome.pack(pady=5)
        ent_nome.insert(0, nome_atual)
        ent_nome.focus()
        
        def acao_confirmar():
            novo_nome = ent_nome.get().strip()
            if novo_nome:
                confirmar_callback(nome_atual, novo_nome, popup)
            else:
                messagebox.showwarning("Aviso", "O nome não pode ser vazio!", parent=popup)

        tk.Button(popup, text="Salvar Alteração", bg=cores_atuais["destaque"], fg="white", bd=0, padx=15, pady=5, font=("Arial", 9, "bold"), command=acao_confirmar).pack(pady=10)    