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
        return response.choices[0].text.strip()
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
            command = recognizer.recognize_google(audio)
            command = command.lower()
            txt_display.insert(tk.END, f"Você disse: {command}\n")
            execute_command(command)

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
    if 'hora' in command:
        now = datetime.datetime.now()
        resposta = f"Agora são {now.hour} horas e {now.minute} minutos."
        speak(resposta)
        txt_display.insert(tk.END, resposta + "\n")
    elif 'abrir google' in command:
        webbrowser.open('https://www.google.com')
        speak("Abrindo o Google.")
        txt_display.insert(tk.END, "Abrindo o Google...\n")
    elif 'abrir notepad' in command:
        os.system('notepad')
        speak("Abrindo o Bloco de Notas.")
        txt_display.insert(tk.END, "Abrindo o Bloco de Notas...\n")
    elif 'sair' in command:
        speak("Encerrando. Até mais!")
        txt_display.insert(tk.END, "Encerrando o programa...\n")
        root.quit()
    else:
        # Se não for comando fixo, usa o ChatGPT para responder
        resposta = chatgpt_response(command)
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

# Mensagem inicial
speak("Olá! Como posso ajudá-lo hoje?")
txt_display.insert(tk.END, "Olá! Clique no botão e fale um comando.\n")

root.after(100, escolher_microfone)

root.mainloop()
