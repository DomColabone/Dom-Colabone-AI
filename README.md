# 🎙️ Dom Colabone AI

O **Dom Colabone AI** é um assistente virtual inteligente controlado por voz que integra reconhecimento de fala em tempo real, uma interface gráfica amigável desenvolvida em Tkinter, e um backend de microsserviço utilizando FastAPI. O sistema processa comandos locais e, caso não encontre uma resposta predefinida ou no servidor, utiliza a API da OpenAI (GPT-4o-mini) como inteligência artificial de fallback.

---

## ✨ Funcionalidades

* **Reconhecimento de Voz Bilíngue**: Suporte a comandos em português (`pt-BR`) e inglês (`en-US`) através da biblioteca Google Speech Recognition.
* **Gerenciador de Microfone Inteligente**: Filtra automaticamente dispositivos de saída inválidos (como alto-falantes e fones) e corrige formatações de exibição de hardware na interface.
* **Comunicação Híbrida (Local + Nuvem)**: 
    * Executa comandos nativos de tempo e navegação.
    * Envia requisições HTTP para uma API local em **FastAPI** para processamento de regras de negócio.
    * Utiliza o modelo `gpt-4o-mini` da OpenAI para responder a perguntas gerais.
* **Interface Gráfica Limpa (GUI)**: Janelas responsivas criadas com Tkinter, com tratamento visual de logs e rolagem automática.
* **Síntese de Voz (TTS)**: Respostas faladas de forma assíncrona para não travar a aplicação utilizando `pyttsx3`.

---

## 🛠️ Tecnologias Utilizadas

### Frontend & Assistente (Client)
* **Python 3.10+**
* **Tkinter**: Interface de usuário.
* **SpeechRecognition**: Captura e tradução de áudio para texto.
* **Pyttsx3**: Síntese de voz offline (Text-to-Speech).
* **OpenAI SDK**: Integração com GPT-4o-mini.
* **Requests**: Comunicação HTTP com a API.

### Backend (Server)
* **FastAPI**: Framework web de alta performance para a construção da API.
* **Uvicorn**: Servidor ASGI para rodar a aplicação.
* **Pydantic**: Validação de dados nas requisições.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
Antes de começar, certifique-se de ter o Python instalado e uma chave de API da OpenAI.

### 1. Clonar o Repositório
```bash
git clone [https://github.com/seu-usuario/dom-colabone-ai.git](https://github.com/seu-usuario/dom-colabone-ai.git)
cd dom-colabone-ai
