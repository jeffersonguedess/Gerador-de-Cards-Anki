# controllers/controller.py
import threading
from tkinter import messagebox
import tkinter as tk

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
        """Mapeia com precisão os novos componentes da View aos métodos do Controller."""
        # Detecta mudança de perfil para recarregar os inputs automaticamente
        self.view.str_perfil_ativo.trace_add("write", lambda *a: self.carregar_dados_perfil())
        
        # Cliques de botões (Ajustados com os novos nomes da View)
        self.view.btn_novo_perfil.config(command=self.handle_novo_perfil)
        self.view.btn_salvar_perfil.config(command=self.salvar_dados_perfil)
        self.view.btn_generar.config(command=self.disparar_motor_geracao)

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

    def disparar_motor_geracao(self):
        """Extrai o texto e envia para o motor de IA em segundo plano (Thread)."""
        nome_perfil = self.view.str_perfil_ativo.get()
        texto_estudo = self.view.txt_material.get("1.0", tk.END).strip()
        
        if not nome_perfil:
            messagebox.showwarning("Aviso", "Selecione um perfil de estudos ativo.")
            return
        if not texto_estudo or len(texto_estudo) < 5:
            messagebox.showwarning("Aviso", "Insira um conteúdo/material de estudo válido para gerar.")
            return
            
        dados_perfil = self.view.obter_dados_campos()
        
        # Bloqueia o botão para evitar cliques duplos acidentais
        self.view.btn_generar.config(state="disabled")
        self.view.limpar_console()
        
        # Inicializa o processo em background de forma assíncrona
        threading.Thread(
            target=self._executar_fluxo_background, 
            args=(nome_perfil, dados_perfil, texto_estudo), 
            daemon=True
        ).start()

    def _executar_fluxo_background(self, nome, dados_perfil, texto_estudo):
        """Executa a chamada na OpenRouter e integração com o Anki sem travar a interface."""
        try:
            # Tenta executar pelo método core ou pela versão adaptada de envio
            if hasattr(self.model, "fluxo_geracao_core"):
                resultado = self.model.fluxo_geracao_core(nome, dados_perfil, self.view.log)
            else:
                resultado = self.model.gerar_e_enviar_cards(dados_perfil, texto_estudo, self.view.log)
            
            # Trata as respostas visuais de sucesso
            if isinstance(resultado, int) and resultado > 0:
                messagebox.showinfo("Concluído", f"🎉 {resultado} flashcards novos foram gerados e sincronizados no seu Anki!")
            elif resultado == "sincronizado" or resultado is True:
                messagebox.showinfo("Concluído", "🚀 O motor de dados finalizou as operações com êxito!")
                
        except Exception as e:
            self.view.log(f"❌ Erro crítico na execução em background: {e}")
        finally:
            # Devolve o controle do botão para o usuário
            self.view.btn_generar.config(state="normal")   