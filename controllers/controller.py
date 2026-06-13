import threading
from tkinter import messagebox
import tkinter as tk

class CardForgeController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        self.conectar_eventos()
        self.sincronizar_lista_perfis()
        self.view.atualizar_tema_interface()
        self.view.log("🤖 Core Engine pronto via padrão MVC. Escolha o seu perfil de estudos.")

    def conectar_eventos(self):
        # Traces das variáveis de controle
        self.view.combo_perfis.trace_add("write", lambda *a: self.carregar_dados_perfil())
        self.view.str_tema.trace_add("write", lambda *a: self.view.atualizar_tema_interface())
        
        # Cliques dos Botões
        self.view.btn_novo.config(command=lambda: self.view.abrir_popup_novo_perfil(self.criar_perfil))
        self.view.btn_salvar.config(command=self.salvar_dados_perfil)
        self.view.btn_gerar.config(command=self.disparar_motor_geracao)
        
        # Botões de Olho (visibilidade)
        self.view.btn_olho_notion.config(command=lambda: self.view.toggle_visibilidade(self.view.ent_notion_token, self.view.btn_olho_notion))
        self.view.btn_olho_or.config(command=lambda: self.view.toggle_visibilidade(self.view.ent_openrouter_key, self.view.btn_olho_or))

    def sincronizar_lista_perfis(self, selecionar=None):
        perfis = self.model.obter_perfis()
        menu = self.view.dropdown_perfis["menu"]
        menu.delete(0, "end")
        
        for p in perfis:
            menu.add_command(label=p, command=lambda v=p: self.view.combo_perfis.set(v))
            
        if perfis:
            self.view.combo_perfis.set(selecionar if selecionar in perfis else perfis[0])
        else:
            self.limpar_campos_interface()

    def carregar_dados_perfil(self):
        nome = self.view.combo_perfis.get()
        if not nome: return
        config = self.model.carregar_perfil(nome)
        if not config: return
        
        self.limpar_campos_interface()
        self.view.ent_notion_token.insert(0, config.get("NOTION_TOKEN", ""))
        self.view.ent_notion_id.insert(0, config.get("NOTION_DATABASE_ID") or config.get("NOTION_PAGE_ID", ""))
        self.view.ent_openrouter_key.insert(0, config.get("OPENROUTER_API_KEY", ""))
        self.view.ent_deck_name.insert(0, config.get("DECK_NAME", nome))
        self.view.str_model_principal.set(config.get("AI_MODEL", ""))
        self.view.str_model_fallback.set(config.get("AI_MODEL_FALLBACK", ""))
        self.view.str_tema.set(config.get("THEME", "Dark Purple Edition"))
        
        self.view.log(f"📁 Perfil '{nome}' carregado. Layout: [{self.view.str_tema.get()}]")

    def limpar_campos_interface(self):
        self.view.ent_notion_token.delete(0, tk.END)
        self.view.ent_notion_id.delete(0, tk.END)
        self.view.ent_openrouter_key.delete(0, tk.END)
        self.view.ent_deck_name.delete(0, tk.END)

    def criar_perfil(self, nome, popup):
        if not nome or f"{nome}.json" in self.model.obter_perfis():
            messagebox.showerror("Erro", "Nome inválido ou perfil já existente.", parent=popup)
            return
        self.model.criar_novo_perfil(nome, self.view.str_tema.get())
        self.view.log(f"✨ Perfil '{nome}' criado.")
        popup.destroy()
        self.sincronizar_lista_perfis(selecionar=nome)

    def salvar_dados_perfil(self):
        nome = self.view.combo_perfis.get()
        if not nome: return
        
        config = {
            "NOTION_TOKEN": self.view.ent_notion_token.get().strip(),
            "NOTION_DATABASE_ID": self.view.ent_notion_id.get().strip(),
            "OPENROUTER_API_KEY": self.view.ent_openrouter_key.get().strip(),
            "DECK_NAME": self.view.ent_deck_name.get().strip(),
            "AI_MODEL": self.view.str_model_principal.get().strip(),
            "AI_MODEL_FALLBACK": self.view.str_model_fallback.get().strip(),
            "THEME": self.view.str_tema.get()
        }
        self.model.salvar_perfil(nome, config)
        self.view.log(f"💾 Perfil 'perfis/{nome}.json' guardado e sincronizado.")
        messagebox.showinfo("Sucesso", f"Definições de '{nome}' foram salvas!")

    def disparar_motor_geracao(self):
        nome = self.view.combo_perfis.get()
        if not nome: return
        
        dados = {
            "token": self.view.ent_notion_token.get().strip(),
            "id_notion": self.view.ent_notion_id.get().strip(),
            "api_key_or": self.view.ent_openrouter_key.get().strip(),
            "deck_name": self.view.ent_deck_name.get().strip(),
            "model_principal": self.view.str_model_principal.get().strip(),
            "model_fallback": self.view.str_model_fallback.get().strip()
        }
        
        self.view.btn_gerar.config(state="disabled")
        threading.Thread(target=self._executar_fluxo_background, args=(nome, dados), daemon=True).start()

    def _executar_fluxo_background(self, nome, dados):
        resultado = self.model.fluxo_geracao_core(nome, dados, self.view.log)
        
        if isinstance(resultado, int) and resultado > 0:
            messagebox.showinfo("Concluído", f"{resultado} flashcards foram enviados para o Anki!")
        elif resultado == "sincronizado":
            messagebox.showinfo("Sincronizado", "Tudo pronto! Nenhuma nota nova encontrada.")
            
        self.view.btn_gerar.config(state="normal")