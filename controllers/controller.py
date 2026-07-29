# controllers/controller.py
import threading
from tkinter import messagebox
import tkinter as tk
from models.model import MODELOS_PRINCIPAIS, MODELOS_RESERVA

class CardForgeController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        self.conectar_eventos()
        self.sincronizar_lista_perfis()
        
        # Ativa o tema padrão inicial
        self.view.atualizar_tema_visual()
        self.view.log("🤖 Core Engine pronto via padrão MVC. Escolha ou crie um perfil de estudos.")

    def conectar_eventos(self):
        # Traces das variáveis de controle
        self.view.cb_perfil.bind("<<ComboboxSelected>>", lambda e: self.carregar_dados_perfil())
        self.view.str_tema.trace_add("write", lambda *a: self.view.atualizar_tema_visual())
        
        # Cliques dos Botões
        self.view.btn_novo_perfil.config(command=lambda: self.view.abrir_popup_novo_perfil(self.confirmar_criacao_perfil))
        self.view.btn_salvar.config(command=self.salvar_dados_perfil)
        
        # Rotas dos novos botões
        self.view.btn_gerar_notion.config(command=lambda: self.disparar_motor_geracao(origem="notion"))
        self.view.btn_gerar_manual.config(command=lambda: self.disparar_motor_geracao(origem="manual"))
        
        # Vincula o clique do olhinho existente na tela à função genérica
        self.view.btn_toggle_key.config(command=lambda: self.view.toggle_visibilidade(self.view.ent_api_key, self.view.btn_toggle_key))
        ##self.view.btn_olho_notion.config(command=lambda: self.view.toggle_visibilidade(self.view.ent_notion_token, self.view.btn_olho_notion))
        ##self.view.btn_olho_or.config(command=lambda: self.view.toggle_visibilidade(self.view.ent_openrouter_key, self.view.btn_olho_or))
        
        # Rotas de gerenciamento avançado do perfil
        self.view.btn_editar_perfil.config(command=self.handle_editar_perfil)
        self.view.btn_excluir_perfil.config(command=self.handle_excluir_perfil)

    def sincronizar_lista_perfis(self):
        """Atualiza o dropdown de perfis buscando dados atualizados do Model."""
        perfis = self.model.listar_perfis()
        self.view.cb_perfil["values"] = perfis
        
        if perfis:
            # Se já houver perfis, seleciona o primeiro por padrão caso esteja vazio
            if not self.view.str_perfil_ativo.get() or self.view.str_perfil_ativo.get() not in perfis:
                self.view.str_perfil_ativo.set(perfis[0])
        else:
            self.view.str_perfil_ativo.set("")

    def carregar_dados_perfil(self):
        """Busca as configurações do perfil selecionado e injeta na tela."""
        nome_perfil = self.view.str_perfil_ativo.get()
        if not nome_perfil:
            return
            
        # Carrega o banco de perfis de forma segura e resiliente
        try:
            with open(self.model.arquivo_perfis, "r", encoding="utf-8") as f:
                import json
                perfis = json.load(f)
                dados = perfis.get(nome_perfil, {})
        except:
            dados = {}
            
        # Alimenta todos os campos e dropdowns de IA da View de uma vez só!
        self.view.preencher_campos(dados)

    def salvar_dados_perfil(self):
        """Captura os dados da tela em lote e salva permanentemente no Model."""
        nome_perfil = self.view.str_perfil_ativo.get()
        if not nome_perfil:
            messagebox.showwarning("Aviso", "Por favor, selecione ou crie um perfil primeiro!")
            return
            
        # Coleta o dicionário limpo e centralizado direto da View
        dados_completos = self.view.obter_dados_campos()
        
        # Salva utilizando o mecanismo do seu Model
        try:
            with open(self.model.arquivo_perfis, "r", encoding="utf-8") as f:
                import json
                perfis = json.load(f)
        except:
            perfis = {}
            
        perfis[nome_perfil] = dados_completos
        self.model.salvar_todos_perfis(perfis)
        
        self.view.log(f"💾 Perfil '{nome_perfil}' e suas preferências de IA foram salvos com sucesso!")

    def handle_novo_perfil(self):
        """Dispara a janela popup customizada e estilizada para criação de matéria."""
        self.view.abrir_popup_novo_perfil(self.confirmar_criacao_perfil)

    def confirmar_criacao_perfil(self, nome_novo, popup_janela):
        """Valida e cria a nova chave de perfil no arquivo de registros."""
        if not nome_novo:
            return
            
        perfis_existentes = self.model.listar_perfis()
        if nome_novo in perfis_existentes:
            messagebox.showwarning("Aviso", f"O perfil '{nome_novo}' já existe no sistema!")
            return
            
        # Estrutura inicial padrão com os novos campos integrados
        dados_padrao = {
            "NOTION_TOKEN": "",
            "NOTION_DATABASE_ID": "",
            "OPENROUTER_API_KEY": "",
            "DECK_NAME": "Default",
            "AI_MODEL": "google/gemini-2.5-flash",
            "AI_MODEL_FALLBACK": "meta-llama/llama-3-8b-instruct:free",
            "THEME": self.view.str_tema.get()
        }
        
        try:
            with open(self.model.arquivo_perfis, "r", encoding="utf-8") as f:
                import json
                perfis = json.load(f)
        except:
            perfis = {}
            
        perfis[nome_novo] = dados_padrao
        self.model.salvar_todos_perfis(perfis)
        
        # Recarrega a interface e foca no perfil recém-criado
        self.sincronizar_lista_perfis()
        self.view.str_perfil_ativo.set(nome_novo)
        
        popup_janela.destroy()
        self.view.log(f"✨ Sucesso! Perfil de estudos '{nome_novo}' foi gerado.")

    def disparar_motor_geracao(self, origem):
        nome = self.view.cb_perfil.get()
        if not nome: return
        
        # Mapeamento cirúrgico corrigindo os nomes reais dos campos da View
        dados = {
            "token": self.view.ent_notion_token.get().strip(),
            "id_notion": self.view.ent_database_id.get().strip(),       # Corrigido!
            "api_key_or": self.view.ent_api_key.get().strip(),          # Corrigido!
            "deck_name": self.view.ent_deck_name.get().strip(),
            "model_principal": self.view.cb_modelo_principal.get().strip(), # Corrigido!
            "model_fallback": self.view.cb_modelo_reserva.get().strip(),    # Corrigido!
            "origem": origem,
            "texto_manual": ""
        }
        
        if origem == "manual":
            dados["texto_manual"] = self.view.txt_input.get("1.0", tk.END).strip()
        
        self.view.btn_gerar_notion.config(state="disabled")
        self.view.btn_gerar_manual.config(state="disabled")
        
        threading.Thread(target=self._executar_fluxo_background, args=(nome, dados), daemon=True).start()

    def _executar_fluxo_background(self, nome, dados):
        try:
            # 1. Extrai o texto correto dependendo da origem (notion ou manual)
            if dados.get("origem") == "notion":
                # Se for do notion, o seu model vai ler a API usando os tokens, 
                # então passamos o texto_estudo como vazio ou tratamos dentro do fluxo.
                texto_estudo = "" 
            else:
                texto_estudo = dados.get("texto_manual", "")

            # 2. Chama o método real do seu model com a assinatura exata dele
            self.model.gerar_e_enviar_cards(
                dados_perfil=dados, 
                texto_estudo=texto_estudo, 
                callback_log=self.view.log
            )
            
            self.view.log(f"🎉 Processamento concluído com sucesso para o perfil '{nome}'!")
                
        except Exception as e:
            self.view.log(f"❌ Erro crítico no motor de geração: {str(e)}")
            
        finally:
            # Devolve a vida aos botões da interface de forma segura
            self.view.root.after(0, lambda: self.view.btn_gerar_notion.config(state="normal"))
            self.view.root.after(0, lambda: self.view.btn_gerar_manual.config(state="normal"))   
    
    def handle_editar_perfil(self):
        """Dispara a janela para renomear a matéria selecionada."""
        perfil_atual = self.view.str_perfil_ativo.get()
        if not perfil_atual:
            messagebox.showwarning("Aviso", "Selecione um perfil na lista primeiro para poder editá-lo!")
            return
        self.view.abrir_popup_editar_perfil(perfil_atual, self.confirmar_edicao_perfil)

    def confirmar_edicao_perfil(self, nome_antigo, novo_nome, popup_janela):
        """Migra os dados salvos do nome antigo para o novo nome no JSON."""
        perfis_existentes = self.model.listar_perfis()
        
        if novo_nome in perfis_existentes and novo_nome != nome_antigo:
            messagebox.showerror("Erro", f"O perfil '{novo_nome}' já existe!", parent=popup_janela)
            return

        import json
        try:
            with open(self.model.arquivo_perfis, "r", encoding="utf-8") as f:
                perfis = json.load(f)
        except:
            perfis = {}

        if nome_antigo in perfis:
            # Clona as informações antigas na nova chave e deleta o registro antigo
            perfis[novo_nome] = perfis[nome_antigo]
            del perfis[nome_antigo]
            
            # Se o Deck Name for igual ao perfil, atualiza automaticamente
            if perfis[novo_nome].get("DECK_NAME") == nome_antigo:
                perfis[novo_nome]["DECK_NAME"] = novo_nome

            self.model.salvar_todos_perfis(perfis)
            
            # Atualiza interface física e lógica
            self.sincronizar_lista_perfis()
            self.view.str_perfil_ativo.set(novo_nome)
            self.carregar_dados_perfil()
            
            popup_janela.destroy()
            self.view.log(f"✏️ Perfil atualizado com sucesso de '{nome_antigo}' para '{novo_nome}'.")

    def handle_excluir_perfil(self):
        """Remove permanentemente o perfil ativo do arquivo JSON."""
        perfil_atual = self.view.str_perfil_ativo.get()
        if not perfil_atual:
            messagebox.showwarning("Aviso", "Selecione um perfil para poder realizar a exclusão!")
            return
            
        confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja deletar o perfil '{perfil_atual}'?\nTodos os tokens configurados dele serão apagados.")
        if confirmar:
            import json
            try:
                with open(self.model.arquivo_perfis, "r", encoding="utf-8") as f:
                    perfis = json.load(f)
            except:
                perfis = {}

            if perfil_atual in perfis:
                del perfis[perfil_atual]
                self.model.salvar_todos_perfis(perfis)
                
                self.view.log(f"❌ Perfil '{perfil_atual}' foi removido com sucesso.")
                
                # 1. Atualiza fisicamente a lista de opções da Combobox
                self.sincronizar_lista_perfis()
                
                # 2. Força o texto visual da caixinha a ir para o primeiro perfil restante
                perfis_restantes = self.model.listar_perfis()
                if perfis_restantes:
                    self.view.str_perfil_ativo.set(perfis_restantes[0])
                    self.carregar_dados_perfil()
                else:
                    # Se não sobrou nenhum perfil, limpa tudo de vez
                    self.view.str_perfil_ativo.set("")
                    self.view.cb_perfil.set("") # Limpa o texto visível da combobox
                    self.view.preencher_campos({
                        "NOTION_TOKEN": "", "NOTION_DATABASE_ID": "",
                        "OPENROUTER_API_KEY": "", "DECK_NAME": "",
                        "AI_MODEL": MODELOS_PRINCIPAIS[0], "AI_MODEL_FALLBACK": MODELOS_RESERVA[0],
                        "THEME": self.view.str_tema.get()
                    })