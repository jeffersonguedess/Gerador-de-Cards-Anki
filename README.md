# 🤖 Automação Notion para Anki com IA (DeepSeek / Llama)

# 🚀 CardForge

O **CardForge** é uma aplicação desktop inteligente projetada para automatizar a conversão de anotações de estudo baseadas no **Notion** diretamente para flashcards do **Anki** usando Inteligência Artificial (via **OpenRouter**). O sistema foi construído com foco em concurseiros e estudantes de TI de alto rendimento, utilizando o formato de **Omissão de Palavras (Cloze Deletion)**.

---

## 🎯 Funcionalidades Principais

* **Sincronização com Notion:** Varredura em tempo real de blocos de texto estruturados em páginas ou bancos de dados.
* **Inteligência Artificial Dupla:** Motor integrado com IA Principal e uma rota de IA Reserva (Fallback) automática para o caso de falhas ou falta de saldo na API.
* **Gerenciador Avançado de Perfis (CRUD):** Permite criar, salvar, editar (renomear) e excluir perfis e tópicos de estudo diretamente pela interface gráfica, sem necessidade de manipulação manual de arquivos locais `.json`.
* **Filtro Antiduplicidade:** Mecanismo de hashing MD5 que garante que apenas anotações inéditas virem flashcards, blindando o seu histórico de revisões.
* **Interface Assíncrona:** Varreduras em segundo plano (*Multi-threading*) que impedem o congelamento da interface gráfica durante chamadas de rede.

## 🛠️ Tecnologias Utilizadas

* **Python 3.10**
* **OpenAI SDK & Requests** (Comunicação HTTP e chamadas de API)
* **Notion API** (Captura de dados estruturados)
* **AnkiConnect API** (Injeção automatizada de cartões)
* **PyInstaller** (Empacotamento para executável)
* **Tkinter** (Interface Gráfica Nativa)
* **Requests** (Consumo de APIs REST)
* **OpenAI Python SDK** (Conexão estruturada com LLMs via OpenRouter)
* **Hashlib** (Criptografia e integridade de dados com MD5)

## 📈 Evolução do Projeto e Linha do Tempo

O projeto foi desenvolvido de forma estritamente incremental e cronológica. Toda a jornada de engenharia de software — partindo de um script utilitário de terminal até a entrega de um ecossistema desktop modularizado — está documentada e pode ser revisada passo a passo:

| Versão | Fase / Foco | Descrição e Impacto Técnico |
| :--- | :--- | :--- |
| **v1.0** | *Prova de Conceito* | Script síncrono básico em terminal focado na validação das integrações iniciais das APIs. |
| **v2.0** | *Persistência Local* | Implementação do primeiro sistema de persistência e leitura de histórico local de execução. |
| **v3.0** | *Desacoplamento* | Refatoração completa para isolamento seguro de chaves/credenciais via `config.json` e suporte a empacotamento. |
| **v4.0** | *Multi-Perfil Local* | Introdução da arquitetura de diretórios para múltiplos perfis de estudo e blindagem contra cards repetidos via hash MD5. |
| **v4.1** | *Estabilização* | Otimização no pipeline de prompts da IA, tratamento robusto de exceções de rede e pequenos ajustes de lógica. |
| **v5.0** | *Interface Gráfica* | Migração definitiva da CLI (Terminal) para o primeiro layout visual desktop desenvolvido nativamente em Tkinter. |
| **v5.1** | *Customização Visual* | Primeiro modelo de estilização *Dark Purple*. |
| **v6.0** | *Arquitetura MVC & CRUD* | Modularização completa do ecossistema dividida estritamente em Model-View-Controller, acoplamento assíncrono de eventos, gerenciador visual dinâmico de perfis (Criação, Edição e Exclusão rápida) e correção de estados visuais na interface. |

---

## 📖 Manual do Usuário (Guia Rápido)

### 🧠 1. Regras de Estruturação no Notion
Para que o motor capture os seus estudos corretamente, escreva uma linha curta e direta por comando ou conceito. O app gera um hash MD5 único de cada linha enviada, **filtrando automaticamente o que já foi enviado** e gerando cartões stritamente para as linhas inéditas.

### 📂 2. Gerenciando Perfis e Matérias
Cada matéria possui suas próprias credenciais e preferências salvas localmente:
* **Criar/Editar:** Clique em `+ Novo` ou `Editar` para gerenciar as chaves e modelos de IA do perfil ativo.
* **Estrutura de Decks:** No campo *Nome do Deck*, use dois pontos duplos (`::`) para segmentar subpastas organizacionais no Anki (Ex: `Git::Comandos`).
* Sempre clique no botão roxo `💾 Salvar Perfil` após alterar qualquer configuração.

### ⚡ 3. Modos de Sincronização
* **Modo A (Automático via Notion):** Selecione o perfil de ambiente e clique em `🍇 Sincronizar via Notion`. O fluxo de logs assíncrono exibirá o andamento em tempo real.
* **Modo B (Manual):** Cole o seu resumo diretamente na caixa *"Material de Estudo para Conversão Manual"* e clique em `📝 Converter Texto da Tela`.

> 📥 **Quer o manual completo e diagramado no tema Dark Purple?** Acesse a nossa documentação oficial em PDF: **[Baixar Manual do Usuário (PDF)](./docs/manual_cardforge.pdf)**

---

## ⚙️ Como Executar o Projeto

1. Clone o repositório.
2. Execute o script principal para gerar o arquivo `config.json`.
3. Insira suas credenciais do Notion e OpenRouter no `config.json`.
4. Abra o Anki e execute o programa!

### Pré-requisitos
1. Certifique-se de que o aplicativo do **Anki** está aberto em segundo plano.
2. Certifique-se de ter a extensão **AnkiConnect** instalada no seu Anki.

> ⚠️ **Aviso sobre Chaves de API:** O CardForge v6.0 utiliza o **OpenRouter** como agregador central de modelos de IA. O campo *OpenRouter Key* aceita **estritamente** chaves geradas dentro da plataforma OpenRouter (que geralmente iniciam com `sk-or-...`). Inserir chaves diretas de outras provedoras (como chaves puras da OpenAI, Google Gemini ou Anthropic) quebrará a comunicação com o motor e resultará em falhas de geração.

# Gerador-de-Cards-Anki
Estudando o Linux queria uma forma de estudar os comandos, saber o que cada um faz de forma simples, com perguntas pequenas e diretas. Então achei o software Anki, tem uma versão para computador e app para celulares, ele gera cards com perguntas e então vi que seria uma ideia automatizar de alguma forma a geração de perguntas com IA.