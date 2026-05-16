import pyttsx3 
import speech_recognition as sr
import datetime
import os
import webbrowser
import requests  
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from openai import OpenAI

# Configure sua API key aqui
client = OpenAI(api_key="SUA_API_KEY_AQUI")

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def add_punctuation(text):
    text = text.strip()
    interrogatives_start = ['como', 'quando', 'onde', 'por que', 'por quê', 'quem', 'qual', 'quais', 'quanto', 'quantos', 'é', 'você', 'se', 'que']
    interrogatives_anywhere = ['não é', 'né', 'certo', 'verdade', 'pode', 'será', 'pode ser']

    if text.endswith(('.', '!', '?')):
        pass
    else:
        lower_text = text.lower()
        is_question = any(lower_text.startswith(word + ' ') or lower_text == word for word in interrogatives_start)
        is_doubt = any(lower_text.endswith(word) for word in interrogatives_anywhere)

        if is_question or is_doubt:
            text += '?'
        else:
            text += '.'

    if len(text) > 0:
        text = text[0].upper() + text[1:]
    return text

def chatgpt_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
        )
        return add_punctuation(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"Erro OpenAI: {e}")
        return "Desculpe, tive um problema ao consultar o ChatGPT."

def listen_and_execute():
    recognizer = sr.Recognizer()
    try:
        mic = sr.Microphone(device_index=selected_mic_index) if selected_mic_index is not None else sr.Microphone()
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            txt_display.insert(tk.END, "Ouvindo...\n")
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=15)

            idiomas = ["pt-BR", "en-US"]
            command = None
            for lang in idiomas:
                try:
                    command = recognizer.recognize_google(audio, language=lang)
                    command = add_punctuation(command)
                    break
                except sr.UnknownValueError:
                    continue

            if command is None:
                finalizar_interface("Não entendi o que você disse.")
                return

            txt_display.insert(tk.END, f"Você disse: {command}\n")
            execute_command(command)
    except Exception:
        finalizar_interface("Erro ao acessar o microfone.")

def execute_command(command):
    command_lower = command.lower()
    API_URL = "http://127.0.0.1:8000/execute"

    if 'hora' in command_lower:
        now = datetime.datetime.now()
        finalizar_interface(f"Agora são {now.hour} horas e {now.minute} minutos.")
    elif 'abrir google' in command_lower:
        webbrowser.open('https://www.google.com')
        finalizar_interface("Abrindo o Google.")
    elif 'sair' in command_lower:
        finalizar_interface("Encerrando. Até mais!")
        root.after(2000, root.quit)
    else:
        try:
            response = requests.post(API_URL, json={"command": command}, timeout=5)
            if response.status_code == 200:
                finalizar_interface(response.json().get("response"))
            else:
                finalizar_interface(chatgpt_response(command))
        except Exception:
            finalizar_interface(chatgpt_response(command))

def finalizar_interface(texto):
    texto_formatado = add_punctuation(texto)
    threading.Thread(target=lambda: speak(texto_formatado)).start()
    txt_display.insert(tk.END, f"Dom: {texto_formatado.strip()}\n")
    txt_display.see(tk.END)

def escolher_microfone():
    global selected_mic_index
    devices = sr.Microphone.list_microphone_names()
    if not devices: return

    mics_validos = []
    bloqueados = ['speaker', 'alto-falante', 'output', 'headphones', 'fones', 'mapeador', 'realtek(r) au']

    for i, name in enumerate(devices):
        try:
            name_limpo = name.encode('latin-1').decode('utf-8')
        except:
            name_limpo = name.replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã', 'í')
            name_limpo = name_limpo.replace('primÃ¡rio', 'primário').replace('estÃ©reo', 'estéreo')

        name_lower = name_limpo.lower()
        
        if not any(name_lower.endswith(b) or name_lower == b for b in bloqueados):
            # Correção de parênteses
            abertos = name_limpo.count('(')
            fechados = name_limpo.count(')')
            if abertos > fechados:
                name_limpo += ')' * (abertos - fechados)
            
            if name_limpo not in [m['nome'] for m in mics_validos]:
                mics_validos.append({'id_real': i, 'nome': name_limpo})

    mics_validos = mics_validos[:4]

    dialog = tk.Toplevel(root)
    dialog.title("Configuração de Microfone")
    
    # AJUSTE AQUI: Mudei para 600x350 para tirar o excesso de branco embaixo
    dialog.geometry("500x270") 
    dialog.configure(bg="#ffffff")
    dialog.grab_set()

    tk.Label(dialog, text="Selecione o número do dispositivo (Top 4):", 
             bg="#ffffff", font=("Arial", 12, "bold")).pack(pady=(20, 10))

    list_frame = tk.Frame(dialog, bg="#ffffff")
    list_frame.pack(padx=30, fill=tk.BOTH)

    mapa_escolha = {}
    for index, mic in enumerate(mics_validos, start=1):
        lbl = tk.Label(list_frame, text=f"{index}: {mic['nome']}", 
                        bg="#ffffff", font=("Arial", 12), anchor="w", justify=tk.LEFT)
        lbl.pack(fill=tk.X, padx=50, pady=2) 
        mapa_escolha[index] = mic['id_real']

    entry = tk.Entry(dialog, width=10, highlightthickness=1, 
                      highlightbackground="#dddddd", bd=0, font=("Arial", 12), justify='center')
    entry.pack(pady=15)
    entry.focus_set()

    def confirmar():
        global selected_mic_index
        escolha = entry.get()
        try:
            if escolha and int(escolha) in mapa_escolha:
                selected_mic_index = mapa_escolha[int(escolha)]
            else:
                selected_mic_index = None
        except ValueError:
            selected_mic_index = None
        dialog.destroy()

    btn_ok = tk.Button(dialog, text="OK", command=confirmar, width=15, 
                        bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                        relief="flat", activebackground="#45a049")
    btn_ok.pack(pady=(0, 20)) # Reduzi o padding inferior

    dialog.bind('<Return>', lambda event: confirmar())
    root.wait_window(dialog)

def start_listening():
    btn_listen.config(state=tk.DISABLED)
    def run():
        listen_and_execute()
        btn_listen.config(state=tk.NORMAL)
    threading.Thread(target=run).start()

# --- INTERFACE PRINCIPAL ---
selected_mic_index = None
root = tk.Tk()
root.title("Dom Colabone AI")
root.geometry("500x380")
root.configure(bg="#ffffff")

btn_listen = tk.Button(root, text="Ouvir Comando", command=start_listening, 
                        bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                        relief="flat", borderwidth=0, highlightthickness=0, 
                        padx=25, pady=10, activebackground="#45a049")
btn_listen.pack(pady=25)

border_frame = tk.Frame(root, bg="#dddddd", bd=0, highlightthickness=1, highlightbackground="#dddddd")
border_frame.pack(padx=20, pady=10)

txt_display = scrolledtext.ScrolledText(border_frame, width=75, height=55, 
                                        font=("Arial", 10),
                                        bg="#fafafa", fg="#333333",
                                        bd=0, highlightthickness=0,
                                        padx=10, pady=10)
txt_display.pack()

root.after(500, lambda: threading.Thread(target=lambda: speak("Dom Colabone pronto.")).start())
root.after(600, escolher_microfone)
root.mainloop()