import pyttsx3 
import speech_recognition as sr
import datetime
import os
import webbrowser
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import threading
import openai

# Configure sua API key aqui (não esqueça de colocar a sua chave)
openai.api_key = "SUA_API_KEY_AQUI"

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def add_punctuation(text):
    text = text.strip()
    interrogatives_start = ['como', 'quando', 'onde', 'por que', 'por quê', 'quem', 'qual', 'quais', 'quanto', 'quantos', 'é', 'você', 'se']
    interrogatives_anywhere = ['não é', 'né', 'certo', 'verdade', 'pode', 'será', 'pode ser']

    # Se já termina com algum sinal de pontuação válido, mantém
    if text.endswith(('.', '!', '?')):
        pass
    else:
        lower_text = text.lower()

        # Verifica se começa com palavra interrogativa
        if any(lower_text.startswith(word + ' ') for word in interrogatives_start):
            text += '?'
        # Verifica se termina com palavra interrogativa
        elif any(lower_text.endswith(word) for word in interrogatives_start + interrogatives_anywhere):
            text += '?'
        # Verifica se contém palavra interrogativa no meio (heurística simples)
        elif any(word in lower_text for word in interrogatives_start + interrogatives_anywhere):
            text += '?'
        else:
            text += '.'

    # Coloca a primeira letra maiúscula
    if len(text) > 0:
        text = text[0].upper() + text[1:]

    return text

def chatgpt_response(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
            n=1,
            stop=None,
        )
        text = response.choices[0].text.strip()
        return add_punctuation(text)
    except Exception as e:
        return "Desculpe, não consegui processar sua pergunta."

def listen_and_execute():
    recognizer = sr.Recognizer()
    try:
        if selected_mic_index is not None:
            mic = sr.Microphone(device_index=selected_mic_index)
        else:
            mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            txt_display.insert(tk.END, "Ouvindo...\n")
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=15)

            idiomas = ["pt-BR", "en-US", "es-ES", "fr-FR"]
            command = None
            for lang in idiomas:
                try:
                    command = recognizer.recognize_google(audio, language=lang)
                    command = add_punctuation(command)  # adiciona pontuação e maiúscula
                    txt_display.insert(tk.END, f"Idioma detectado: {lang}\n")
                    break
                except sr.UnknownValueError:
                    continue

            if command is None:
                speak("Desculpe, não entendi o que você disse.")
                txt_display.insert(tk.END, "Não entendi o que você disse.\n")
                return

            command_lower = command.lower()  # para processamento sem case
            txt_display.insert(tk.END, f"Você disse: {command}\n")
            execute_command(command_lower)

    except sr.UnknownValueError:
        speak("Desculpe, não entendi o que você disse.")
        txt_display.insert(tk.END, "Não entendi o que você disse.\n")
    except sr.RequestError:
        speak("Erro ao conectar com o serviço de reconhecimento de fala.")
        txt_display.insert(tk.END, "Erro na conexão com o serviço.\n")
    except sr.WaitTimeoutError:
        speak("Você não disse nada.")
        txt_display.insert(tk.END, "Você não disse nada.\n")
    except OSError:
        speak("Nenhum microfone disponível.")
        txt_display.insert(tk.END, "Nenhum microfone disponível.\n")

def execute_command(command):
    if 'hora' in command or 'time' in command:
        now = datetime.datetime.now()
        resposta = f"Agora são {now.hour} horas e {now.minute} minutos."
        resposta = add_punctuation(resposta)
        speak(resposta)
        txt_display.insert(tk.END, resposta + "\n")
    elif 'abrir google' in command or 'open google' in command:
        webbrowser.open('https://www.google.com')
        resposta = "Abrindo o Google."
        resposta = add_punctuation(resposta)
        speak(resposta)
        txt_display.insert(tk.END, resposta + "\n")
    elif 'abrir notepad' in command or 'open notepad' in command:
        os.system('notepad')
        resposta = "Abrindo o Bloco de Notas."
        resposta = add_punctuation(resposta)
        speak(resposta)
        txt_display.insert(tk.END, resposta + "\n")
    elif 'sair' in command or 'exit' in command or 'quit' in command:
        resposta = "Encerrando. Até mais!"
        resposta = add_punctuation(resposta)
        speak(resposta)
        txt_display.insert(tk.END, resposta + "\n")
        root.quit()
    else:
        # Se não for comando fixo, usa o ChatGPT para responder
        resposta = chatgpt_response(command)
        resposta = add_punctuation(resposta)
        speak(resposta)
        txt_display.insert(tk.END, resposta + "\n")

def start_listening():
    threading.Thread(target=listen_and_execute).start()

def escolher_microfone():
    global selected_mic_index
    devices = sr.Microphone.list_microphone_names()
    if not devices:
        messagebox.showerror("Erro", "Nenhum microfone encontrado no sistema.")
        btn_listen.config(state=tk.DISABLED)
        selected_mic_index = None
        txt_display.insert(tk.END, "Nenhum microfone disponível.\n")
        return

    escolha = simpledialog.askstring(
        "Selecionar Microfone",
        "Microfones encontrados:\n" + "\n".join(f"{i}: {name}" for i, name in enumerate(devices)) +
        "\n\nDigite o número do microfone que deseja usar (ou deixe vazio para padrão):"
    )

    if escolha is None or escolha.strip() == "":
        selected_mic_index = None
        txt_display.insert(tk.END, "Usando microfone padrão do sistema.\n")
    else:
        try:
            idx = int(escolha)
            if idx < 0 or idx >= len(devices):
                raise ValueError
            selected_mic_index = idx
            txt_display.insert(tk.END, f"Microfone selecionado: {devices[idx]}\n")
        except ValueError:
            messagebox.showwarning("Aviso", "Entrada inválida. Usando microfone padrão.")
            selected_mic_index = None
            txt_display.insert(tk.END, "Usando microfone padrão do sistema.\n")

selected_mic_index = None

root = tk.Tk()
root.title("Dom Colabone AI")

btn_listen = tk.Button(root, text="Ouvir Comando", command=start_listening)
btn_listen.pack(pady=10)

txt_display = scrolledtext.ScrolledText(root, width=50, height=15)
txt_display.pack(padx=10, pady=10)

txt_display.insert(tk.END, "Olá! Clique no botão e fale um comando.\n")

def fala_inicial():
    threading.Thread(target=lambda: speak("Olá! Como posso ajudá-lo hoje?")).start()

root.after(500, fala_inicial)
root.after(100, escolher_microfone)

root.mainloop()
