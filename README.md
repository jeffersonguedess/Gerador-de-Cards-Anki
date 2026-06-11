# 🤖 Automação Notion para Anki com IA (DeepSeek / Llama)

# 🚀 CardForge

O **CardForge** é uma aplicação desktop inteligente projetada para automatizar a conversão de anotações de estudo baseadas no **Notion** diretamente para flashcards do **Anki** usando Inteligência Artificial (via **OpenRouter**). O sistema foi construído com foco em concurseiros e estudantes de TI de alto rendimento, utilizando o formato de **Omissão de Palavras (Cloze Deletion)**.

---

## 🎯 Funcionalidades Principais

* **Sincronização com Notion:** Varredura em tempo real de blocos de texto estruturados em páginas ou bancos de dados.
* **Inteligência Artificial Dupla:** Motor integrado com IA Principal e uma rota de IA Reserva (Fallback) automática para o caso de falhas ou falta de saldo na API.
* **Gerenciador Multi-Perfil:** Salva credenciais, caminhos, modelos de IA e preferências visuais separadamente por matéria/tópico em arquivos `.json` locais.
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
| **v5.1** | *Customização Visual* |  Primeiro modelo de estilização *Dark Purple*. |

## ⚙️ Como Executar o Projeto

1. Clone o repositório.
2. Execute o script principal para gerar o arquivo `config.json`.
3. Insira suas credenciais do Notion e OpenRouter no `config.json`.
4. Abra o Anki e execute o programa!

### Pré-requisitos
1. Certifique-se de que o aplicativo do **Anki** está aberto em segundo plano.
2. Certifique-se de ter a extensão **AnkiConnect** instalada no seu Anki.

# Gerador-de-Cards-Anki
Estuando o Linux queria uma forma de estudar os comandos, saber oque cada um faz de forma simples, com perguntas pequenas e diretas. Então achei o software Anki, tem uma versã para computador e app para celulares, ele gera cards com perguntas e então vi que seria uma ideia automatizar de alguma forma a geração de perguntas com IA. 

