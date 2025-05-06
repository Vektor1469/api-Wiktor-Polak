import tkinter as tk
from tkinter import ttk
import requests
from api import NasaImageFetcher
from PIL import Image, ImageTk
import io
import urllib.request
from functools import partial

#kolor tła
BG_COLOR = "#000000"

#kolor czcionki
FG_COLOR = "#00FF00"

fetch =  NasaImageFetcher()

image_refs = []

popup_refs = []

#otwarcie obrazu w nowym oknie
def on_image_click(image_url, title, event=None):
    try:
        response = requests.get(image_url)
        image_data = response.content
        image = Image.open(io.BytesIO(image_data))

        popup = tk.Toplevel()
        popup.title(title)
        popup.configure(bg=BG_COLOR)

        image = image.resize((min(800, image.width), min(600, image.height)))
        photo = ImageTk.PhotoImage(image)
        popup_refs.append(photo)

        label = tk.Label(popup, image=photo, bg=BG_COLOR)
        label.pack(padx=10, pady=10)

        title_label = tk.Label(popup, text=title, fg=FG_COLOR, bg=BG_COLOR, wraplength=800)
        title_label.pack()

    except Exception as e:
        text_log.insert(tk.END, f"Błąd przy otwieraniu obrazu: {e}\n")

#Wyświetlanie obrazów w kolumnach
def display_images(results):
    for widget in output_frame.winfo_children():
        widget.destroy()

    cols = 3
    row = 0
    col = 0

    for idx, result in enumerate(results):
        try:
            response = requests.get(result['image_url'])
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail((200, 200))

            photo = ImageTk.PhotoImage(image)
            image_refs.append(photo)

            frame = tk.Frame(output_frame, bg=BG_COLOR, padx=10, pady=10)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")

            label_image = tk.Label(frame, image=photo,  bg=BG_COLOR, borderwidth=0, highlightthickness=0, cursor="hand2")
            label_image.pack()

            label_image.bind("<Button-1>", partial(on_image_click, result['image_url'], result['title']))

            label_title = tk.Label(frame, text=result['title'], wraplength=200,  fg=FG_COLOR, bg=BG_COLOR)
            label_title.pack()

            col += 1
            if col >= cols:
                col = 0
                row += 1

        except Exception as e:
            text_log.insert(tk.END, f"Błąd przy ładowaniu obrazu: {e}\n")

#obiekt szukający obraz
def search_image():
    query = entry.get()
    text_log.delete("1.0", tk.END)
    try:
        data = fetch.fetch_data(query)
        fetch.display_results(data, log_widget=text_log)
        results = fetch.get_results(data)
        display_images(results)
    except Exception as e:
        text_log.insert(tk.END, f"Błąd: {e}\n")

#Główne okno
window = tk.Tk()
window.title("NASA Search API")
window.geometry("1280x720")
window.configure(bg=BG_COLOR)

#Layout siatki
for r in range(4):
    window.rowconfigure(r, weight=1)
for c in range(6):
    window.columnconfigure(c, weight=1)

#inputy
input_frame = tk.Frame(master=window, bg=BG_COLOR)
input_frame.grid(row=0, column=0, columnspan=3, sticky="new", padx=10, pady=10)

text = tk.Label(input_frame, text="Podaj zapytanie:", fg=FG_COLOR, bg=BG_COLOR)
text.grid(row=0, column=1, padx=5, pady=5)

entry = tk.Entry(input_frame, width=30, fg=FG_COLOR, bg=BG_COLOR, insertbackground=FG_COLOR)
entry.grid(row=0, column=2, padx=5, pady=5)

button = tk.Button(master = input_frame, text="Szukaj", command = search_image, fg=FG_COLOR, bg=BG_COLOR, activebackground=BG_COLOR, activeforeground=FG_COLOR, borderwidth=1)
button.grid(row=0, column=3, padx=5, pady=5)

#output
output_frame = tk.Frame(master = window)
output_frame.grid(row=1, column=0, columnspan=3, rowspan = 3, sticky="s")
text_output = tk.Label(output_frame, text="Wyniki:")
text_output.grid(row=1, column=0, padx=5, pady=5)

#scroll
canvas = tk.Canvas(window, bg=BG_COLOR, highlightthickness=0)
canvas.grid(row=1, column=0, columnspan=4, rowspan=3, sticky="nsew")

scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview, bg=BG_COLOR, troughcolor=BG_COLOR, activebackground=BG_COLOR, highlightbackground=BG_COLOR)
scrollbar.grid(row=1, column=4, rowspan=3, sticky="ns")

canvas.configure(yscrollcommand=scrollbar.set)

output_frame = tk.Frame(canvas, bg=BG_COLOR)
output_window = canvas.create_window((0, 0), window=output_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

output_frame.bind("<Configure>", on_frame_configure)

#logi
log_frame = tk.Frame(master=window, bg=BG_COLOR)
log_frame.grid(row=1, column=5, columnspan=1, rowspan=3, sticky="n")

log_label = tk.Label(log_frame, text="Logi:", fg=FG_COLOR, bg=BG_COLOR)
log_label.grid(row=0, column=0, padx=5, pady=5)

text_log = tk.Text(log_frame, width=40, height=40, fg=FG_COLOR, bg=BG_COLOR, insertbackground=FG_COLOR)
text_log.grid(row=1, column=0, padx=5, pady=5)

window.mainloop()