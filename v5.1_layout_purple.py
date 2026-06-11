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

# --- PALETA DE CORES PERSONALIZADA ---
COR_FUNDO_PRINCIPAL = "#0a0a0c"  # Preto profundo
COR_FUNDO_CARD = "#16161a"       # Cinza muito escuro para blocos
COR_ROXO_DESTAQUE = "#6d28d9"    # Roxo principal
COR_ROXO_HOVER = "#7c3aed"       # Roxo ao passar o rato
COR_TEXTO = "#f3f4f6"            # Branco / Cinza claro
COR_TEXTO_MUTED = "#9ca3af"      # Cinza para labels
COR_CONSOLE_BG = "#020203"       # Preto puro para o log

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

class CardForgePurpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CardForge v5.1 - Dark Purple Edition")
        self.root.geometry("680x780")
        self.root.configure(bg=COR_FUNDO_PRINCIPAL)
        
        os.makedirs("perfis", exist_ok=True)
        os.makedirs("historicos", exist_ok=True)
        
        self.criar_interface_estilizada()
        self.atualizar_lista_perfis()

    def criar_interface_estilizada(self):
        # --- SEÇÃO 1: GERENCIAMENTO DE PERFIL ---
        frame_perfil = tk.LabelFrame(self.root, text=" Gerenciamento de Perfil ", bg=COR_FUNDO_CARD, fg=COR_ROXO_DESTAQUE, font=("Arial", 10, "bold"), padx=10, pady=10, bd=1, relief="solid")
        frame_perfil.pack(fill="x", padx=15, pady=10)
        
        tk.Label(frame_perfil, text="Perfil Ativo:", bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(side="left", padx=5)
        
        self.combo_perfis = tk.StringVar()
        self.dropdown_perfis = tk.OptionMenu(frame_perfil, self.combo_perfis, "")
        self.dropdown_perfis.config(bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO, activebackground=COR_ROXO_DESTAQUE, activeforeground=COR_TEXTO, bd=1, relief="flat", width=22)
        self.dropdown_perfis.pack(side="left", padx=5)
        
        # Monitora a alteração do perfil de forma nativa
        self.combo_perfis.trace_add("write", lambda *args: self.evento_perfil_selecionado())
        
        btn_novo = tk.Button(frame_perfil, text=" Novo Perfil", bg=COR_ROXO_DESTAQUE, fg=COR_TEXTO, activebackground=COR_ROXO_HOVER, activeforeground=COR_TEXTO, bd=0, padx=10, relief="flat", font=("Arial", 9, "bold"), command=self.janela_novo_perfil)
        btn_novo.pack(side="left", padx=10)
        
        # --- SEÇÃO 2: CONFIGURAÇÕES DO PERFIL (DADOS) ---
        frame_dados = tk.LabelFrame(self.root, text=" Configurações do Perfil ", bg=COR_FUNDO_CARD, fg=COR_ROXO_DESTAQUE, font=("Arial", 10, "bold"), padx=10, pady=10, bd=1, relief="solid")
        frame_dados.pack(fill="x", padx=15, pady=5)
        frame_dados.columnconfigure(1, weight=1)
        
        # Linha 0: Notion Token
        tk.Label(frame_dados, text="Notion Token:", bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).grid(row=0, column=0, sticky="w", pady=6, padx=5)
        self.ent_notion_token = tk.Entry(frame_dados, show="*", bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO, bd=1, relief="solid", insertbackground="white")
        self.ent_notion_token.grid(row=0, column=1, sticky="ew", pady=6, padx=(5, 2))
        
        self.btn_olho_notion = tk.Button(frame_dados, text="👁️", bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO_MUTED, activebackground=COR_FUNDO_CARD, activeforeground=COR_TEXTO, bd=1, relief="solid", width=3, command=lambda: self.toggle_visibilidade(self.ent_notion_token, self.btn_olho_notion))
        self.btn_olho_notion.grid(row=0, column=2, pady=6, padx=(0, 5), sticky="w")
        
        # Linha 1: Notion ID
        tk.Label(frame_dados, text="Notion ID / DB:", bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).grid(row=1, column=0, sticky="w", pady=6, padx=5)
        self.ent_notion_id = tk.Entry(frame_dados, bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO, bd=1, relief="solid", insertbackground="white")
        self.ent_notion_id.grid(row=1, column=1, columnspan=2, sticky="ew", pady=6, padx=5)
        
        # Linha 2: OpenRouter Key
        tk.Label(frame_dados, text="OpenRouter Key:", bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).grid(row=2, column=0, sticky="w", pady=6, padx=5)
        self.ent_openrouter_key = tk.Entry(frame_dados, show="*", bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO, bd=1, relief="solid", insertbackground="white")
        self.ent_openrouter_key.grid(row=2, column=1, sticky="ew", pady=6, padx=(5, 2))
        
        self.btn_olho_or = tk.Button(frame_dados, text="👁️", bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO_MUTED, activebackground=COR_FUNDO_CARD, activeforeground=COR_TEXTO, bd=1, relief="solid", width=3, command=lambda: self.toggle_visibilidade(self.ent_openrouter_key, self.btn_olho_or))
        self.btn_olho_or.grid(row=2, column=2, pady=6, padx=(0, 5), sticky="w")
        
        # Linha 3: Deck Anki
        tk.Label(frame_dados, text="Nome do Deck Anki:", bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).grid(row=3, column=0, sticky="w", pady=6, padx=5)
        self.ent_deck_name = tk.Entry(frame_dados, bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO, bd=1, relief="solid", insertbackground="white")
        self.ent_deck_name.grid(row=3, column=1, columnspan=2, sticky="ew", pady=6, padx=5)

        # --- SEÇÃO 3: SELEÇÃO DE INTELIGÊNCIA ARTIFICIAL ---
        frame_ia = tk.LabelFrame(self.root, text=" Configuração de Inteligência Artificial ", bg=COR_FUNDO_CARD, fg=COR_ROXO_DESTAQUE, font=("Arial", 10, "bold"), padx=10, pady=10, bd=1, relief="solid")
        frame_ia.pack(fill="x", padx=15, pady=10)
        frame_ia.columnconfigure(1, weight=1)
        
        # Menu IA Principal
        tk.Label(frame_ia, text="IA Principal:", bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).grid(row=0, column=0, sticky="w", pady=6, padx=5)
        self.str_model_principal = tk.StringVar(value=MODELOS_PRINCIPAIS[0])
        self.menu_principal = tk.OptionMenu(frame_ia, self.str_model_principal, *MODELOS_PRINCIPAIS)
        self.menu_principal.config(bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO, activebackground=COR_ROXO_DESTAQUE, bd=1, relief="flat")
        self.menu_principal.grid(row=0, column=1, sticky="ew", pady=6, padx=5)
        
        # Menu IA Reserva
        tk.Label(frame_ia, text="IA Reserva (Backup):", bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).grid(row=1, column=0, sticky="w", pady=6, padx=5)
        self.str_model_fallback = tk.StringVar(value=MODELOS_RESERVA[0])
        self.menu_fallback = tk.OptionMenu(frame_ia, self.str_model_fallback, *MODELOS_RESERVA)
        self.menu_fallback.config(bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO, activebackground=COR_ROXO_DESTAQUE, bd=1, relief="flat")
        self.menu_fallback.grid(row=1, column=1, sticky="ew", pady=6, padx=5)

        # --- SEÇÃO 4: BOTÕES DE ACÇÃO ---
        frame_botoes = tk.Frame(self.root, bg=COR_FUNDO_PRINCIPAL, pady=5)
        frame_botoes.pack(fill="x", padx=15, pady=5)
        
        self.btn_salvar = tk.Button(frame_botoes, text="💾 Salvar Configurações", bg="#4b5563", fg=COR_TEXTO, activebackground="#374151", activeforeground=COR_TEXTO, bd=0, height=2, font=("Arial", 10, "bold"), command=self.salvar_configuracoes_atuais)
        self.btn_salvar.pack(side="left", expand=True, fill="x", padx=5)
        
        self.btn_gerar = tk.Button(frame_botoes, text="🚀 Gerar Flashcards", bg=COR_ROXO_DESTAQUE, fg=COR_TEXTO, activebackground=COR_ROXO_HOVER, activeforeground=COR_TEXTO, bd=0, height=2, font=("Arial", 10, "bold"), command=self.disparar_fluxo_geracao)
        self.btn_gerar.pack(side="left", expand=True, fill="x", padx=5)
        
        # --- SEÇÃO 5: LOG CONSOLE ---
        tk.Label(self.root, text="Histórico de Execução e Logs em Tempo Real:", bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO_MUTED, font=("Arial", 9)).pack(anchor="w", padx=15, pady=(10,0))
        self.txt_log = scrolledtext.ScrolledText(self.root, height=12, bg=COR_CONSOLE_BG, fg="#a78bfa", insertbackground="white", font=("Consolas", 10), bd=1, relief="solid")
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        self.log("🤖 Sistema iniciado. Selecione ou crie um perfil acima para carregar o ecossistema.")

    # ================= FUNCIONALIDADES DA INTERFACE =================

    def log(self, mensagem):
        self.txt_log.insert(tk.END, f"{mensagem}\n")
        self.txt_log.see(tk.END)

    def toggle_visibilidade(self, campo_entry, botao):
        """Muda dinamicamente o mascaramento do campo de texto (Olho)"""
        if campo_entry.cget("show") == "*":
            campo_entry.config(show="")
            botao.config(text="🙈", fg=COR_ROXO_DESTAQUE)
        else:
            campo_entry.config(show="*")
            botao.config(text="👁️", fg=COR_TEXTO_MUTED)

    def atualizar_lista_perfis(self, selecionar_nome=None):
        perfis = [f.replace(".json", "") for f in os.listdir("perfis") if f.endswith(".json")]
        
        # Atualiza as opções do menu dropdown nativo
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
        if not nome_perfil:
            return
        
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
            
            self.log(f"📁 Perfil '{nome_perfil}' carregado.")
        except Exception as e:
            self.log(f"❌ Erro ao ler perfil: {e}")

    def limpar_campos(self):
        self.ent_notion_token.delete(0, tk.END)
        self.ent_notion_id.delete(0, tk.END)
        self.ent_openrouter_key.delete(0, tk.END)
        self.ent_deck_name.delete(0, tk.END)

    def janela_novo_perfil(self):
        popup = tk.Toplevel(self.root)
        popup.title("Novo Perfil")
        popup.geometry("320x140")
        popup.configure(bg=COR_FUNDO_CARD)
        popup.grab_set()
        popup.resizable(False, False)
        
        tk.Label(popup, text="Nome do Perfil / Matéria:", bg=COR_FUNDO_CARD, fg=COR_TEXTO, font=("Arial", 10)).pack(pady=10)
        ent_nome = tk.Entry(popup, bg=COR_FUNDO_PRINCIPAL, fg=COR_TEXTO, bd=1, relief="solid", width=28, insertbackground="white")
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
                "AI_MODEL_FALLBACK": MODELOS_RESERVA[0]
            }
            with open(os.path.join("perfis", f"{nome}.json"), "w", encoding="utf-8") as f:
                json.dump(modelo, f, indent=4, ensure_ascii=False)
                
            self.log(f"✨ Perfil '{nome}' gerado no sistema.")
            popup.destroy()
            self.atualizar_lista_perfis(selecionar_nome=nome)
            
        tk.Button(popup, text="Criar Perfil", bg=COR_ROXO_DESTAQUE, fg=COR_TEXTO, activebackground=COR_ROXO_HOVER, activeforeground=COR_TEXTO, bd=0, padx=15, pady=3, command=confirmar).pack(pady=10)

    def salvar_configuracoes_atuais(self):
        nome_perfil = self.combo_perfis.get()
        if not nome_perfil: return
            
        config = {
            "NOTION_TOKEN": self.ent_notion_token.get().strip(),
            "NOTION_DATABASE_ID": self.ent_notion_id.get().strip(),
            "OPENROUTER_API_KEY": self.ent_openrouter_key.get().strip(),
            "DECK_NAME": self.ent_deck_name.get().strip(),
            "AI_MODEL": self.str_model_principal.get().strip(),
            "AI_MODEL_FALLBACK": self.str_model_fallback.get().strip()
        }
        
        with open(os.path.join("perfis", f"{nome_perfil}.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
        self.log(f"💾 Ficheiro 'perfis/{nome_perfil}.json' atualizado com sucesso.")
        messagebox.showinfo("Sucesso", f"Configurações de '{nome_perfil}' guardadas!")

    # ================= PROCESSAMENTO AUTOMATIZADO EM BACKGROUND =================

    def disparar_fluxo_geracao(self):
        nome_perfil = self.combo_perfis.get()
        if not nome_perfil: return
        self.btn_gerar.config(state="disabled", bg="#374151")
        threading.Thread(target=self.fluxo_geracao_background, args=(nome_perfil,), daemon=True).start()

    def fluxo_geracao_background(self, nome_perfil):
        try:
            token = self.ent_notion_token.get().strip()
            id_notion = self.ent_notion_id.get().strip()
            api_key_or = self.ent_openrouter_key.get().strip()
            deck_name = self.ent_deck_name.get().strip()
            model_principal = self.str_model_principal.get().strip()
            model_fallback = self.str_model_fallback.get().strip()
            
            self.log(f"\n🚀 A varrer atualizações para o perfil: {nome_perfil}")
            
            # Histórico
            caminho_hist = os.path.join("historicos", f"{nome_perfil}_historico.txt")
            historico = set()
            if os.path.exists(caminho_hist):
                with open(caminho_hist, "r", encoding="utf-8") as f:
                    historico = set(l.strip() for l in f if l.strip())
            
            # Notion
            self.log("📖 A recolher novos dados da API do Notion...")
            url = f"https://api.notion.com/v1/blocks/{id_notion}/children"
            headers = {
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, params={"page_size": 100})
            if response.status_code != 200:
                self.log(f"❌ Falha no Notion ({response.status_code}): {response.text}")
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
                self.log(f"✨ Tudo em dia. Nenhuma linha inédita detetada para '{nome_perfil}'.")
                return
                
            self.log(f"💡 Foram localizadas {len(blocos_novos)} anotações novas para conversão.")
            texto_para_ia = "\n".join([item["texto"] for item in blocos_novos])
            
            # Motores de Inteligência Artificial
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
            self.log(f"🤖 A enviar dados para a IA Principal ({model_principal})...")
            
            try:
                res = client.chat.completions.create(
                    model=model_principal,
                    messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_para_ia}],
                    temperature=0.2, max_tokens=2000, response_format={'type': 'json_object'}
                )
                lista_de_cards = json.loads(res.choices[0].message.content).get("cards", [])
            except Exception as err_principal:
                self.log(f"⚠️ Alerta: Modelo principal indisponível ou sem saldo: {err_principal}")
                self.log(f"🔄 [CONTINGÊNCIA] A ligar à rota gratuita de backup: {model_fallback}...")
                try:
                    res = client.chat.completions.create(
                        model=model_fallback,
                        messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": texto_para_ia}],
                        temperature=0.2, max_tokens=2000, response_format={'type': 'json_object'}
                    )
                    lista_de_cards = json.loads(res.choices[0].message.content).get("cards", [])
                    self.log("✅ Excelente: O motor reserva processou tudo com sucesso!")
                except Exception as err_fallback:
                    self.log(f"❌ Erro Crítico: O motor de emergência também falhou: {err_fallback}")
                    return
            
            # Anki Connect Injeção
            if not lista_de_cards:
                self.log("⚠️ Nenhuma estrutura de card gerada.")
                return
                
            self.log(f"📥 A injetar {len(lista_de_cards)} novos cards diretamente no Anki...")
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
                            "fields": {"Texto": card["texto"]}, "tags": ["concursos", "dark_purple_forge"]
                        }
                    }
                }
                try:
                    res_anki = requests.post(ANKI_CONNECT_URL, json=payload).json()
                    if not res_anki.get("error"):
                        cards_com_sucesso += 1
                except:
                    self.log("❌ Falha de Conexão: Verifique se a aplicação do Anki está aberta.")
                    return
                    
            if cards_com_sucesso > 0:
                with open(caminho_hist, "a", encoding="utf-8") as f:
                    for item in blocos_novos:
                        f.write(f"{item['hash']}\n")
                self.log(f"💾 Concluído! {cards_com_sucesso} cards gerados. Histórico do perfil '{nome_perfil}' protegido.")
                messagebox.showinfo("Sucesso", f"{cards_com_sucesso} cards foram enviados para o Anki!")
            else:
                self.log("⚠ Nenhum card pôde ser inserido (pode tratar-se de conteúdo duplicado).")
                
        except Exception as e_geral:
            self.log(f"❌ Falha inesperada: {e_geral}")
        finally:
            self.btn_gerar.config(state="normal", bg=COR_ROXO_DESTAQUE)


if __name__ == "__main__":
    root = tk.Tk()
    app = CardForgePurpleApp(root)
    root.mainloop()