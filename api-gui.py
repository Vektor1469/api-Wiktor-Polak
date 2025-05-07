# Import biblioteki GUI
import tkinter as tk
# Do pobierania danych z internetu
import requests
# Import klasy do pobierania danych z API NASA
from api import NasaImageFetcher
# Do przetwarzania i wyświetlania obrazów
from PIL import Image, ImageTk
# Do konwersji bajtów na obrazy
import io
# Umożliwia przekazywanie argumentów do funkcji przez bind
from functools import partial

# Ustawienia kolorów tła i czcionki
BG_COLOR = "#000000"
FG_COLOR = "#00FF00"

# Tworzenie instancji obiektu do pobierania danych
fetch = NasaImageFetcher()

# Listy referencji do obrazów, by nie usuwał ich garbage collector
image_refs = []
popup_refs = []

# --- Funkcje pomocnicze ---

def create_label(master, text="", **kwargs):
    # Tworzy etykietę z domyślnymi kolorami
    return tk.Label(master, text=text, fg=FG_COLOR, bg=BG_COLOR, **kwargs)

def create_entry(master, **kwargs):
    # Tworzy pole tekstowe z domyślnymi kolorami
    return tk.Entry(master, fg=FG_COLOR, bg=BG_COLOR, insertbackground=FG_COLOR, **kwargs)

def create_button(master, text, command, **kwargs):
    # Przycisk z domyślną kolorystyką
    return tk.Button(master, text=text, command=command, fg=FG_COLOR, bg=BG_COLOR,
                     activebackground=BG_COLOR, activeforeground=FG_COLOR, borderwidth=1, **kwargs)

def load_image_from_url(url, resize=None, thumbnail=None):
    # Pobierz obraz z URL
    response = requests.get(url)
    # Zawartość w bajtach
    image_data = response.content
    # Przekształć bajty na obraz
    image = Image.open(io.BytesIO(image_data))
    if resize:
        # Zmień rozmiar, jeśli podano
        image = image.resize(resize)
    if thumbnail:
        # Zmień do miniatury, jeśli podano
        image.thumbnail(thumbnail)
    # Zwróć gotowy obraz
    return image

# Otwiera nowy popup z klikniętym obrazem
def on_image_click(image_url, title, event=None):
    try:
        # Pobierz i przeskaluj obraz
        image = load_image_from_url(image_url, resize=(800, 600))
        # Nowe okno popup
        popup = tk.Toplevel()
        # Tytuł popupu
        popup.title(title)
        # Kolor tła
        popup.configure(bg=BG_COLOR)

        # Konwertuj na format zrozumiały dla Tkintera
        photo = ImageTk.PhotoImage(image)
        # Przechowuj referencję
        popup_refs.append(photo)

        # Obraz jako etykieta
        label = tk.Label(popup, image=photo, bg=BG_COLOR)
        # Wyśrodkuj z marginesem
        label.pack(padx=10, pady=10)

        # Tytuł obrazu pod spodem
        title_label = create_label(popup, text=title, wraplength=800)
        # Wyświetl tytuł
        title_label.pack()

    except Exception as e:
        # Komunikat o błędzie
        text_log.insert(tk.END, f"B\u0142\u0105d przy otwieraniu obrazu: {e}\n")

# Wyświetla obrazy w siatce
def display_images(results):
    for widget in output_frame.winfo_children():
        # Czyści poprzednie wyniki
        widget.destroy()  

    # Ilość kolumn w siatce
    cols = 3
    row = 0
    col = 0

    for result in results:
        try:
            # Pobierz miniaturkę
            image = load_image_from_url(result['image_url'], thumbnail=(200, 200))
            # Konwertuj na format dla Tkintera
            photo = ImageTk.PhotoImage(image)
            # Przechowuj referencję
            image_refs.append(photo)

            # Ramka na obraz i tytuł
            frame = tk.Frame(output_frame, bg=BG_COLOR, padx=10, pady=10)

            # Pozycjonowanie
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")
            # Etykieta z obrazem
            label_image = tk.Label(frame, image=photo, bg=BG_COLOR, borderwidth=0,
                                   highlightthickness=0, cursor="hand2")
            # Wyświetl
            label_image.pack()
            # Obsługa kliknięcia
            label_image.bind("<Button-1>", partial(on_image_click, result['image_url'], result['title']))

            # Tytuł obrazka
            label_title = create_label(frame, text=result['title'], wraplength=200)
            # Wyświetl tytuł
            label_title.pack()

            # Przejdź do kolejnej kolumny
            col += 1
            # Nowy wiersz po 3 kolumnach
            if col >= cols:
                col = 0
                row += 1

        except Exception as e:
            # Błąd pobierania obrazu
            text_log.insert(tk.END, f"B\u0142\u0105d przy \u0142adowaniu obrazu: {e}\n")

# Obsługa kliknięcia "Szukaj"
def search_image():
    # Pobierz zapytanie
    query = entry.get()
    # Wyczyść logi
    text_log.delete("1.0", tk.END)
    try:
        # Pobierz dane z API
        data = fetch.fetch_data(query)
        # Wyświetl wyniki w logu
        fetch.display_results(data, log_widget=text_log)
        # Przefiltruj wyniki
        results = fetch.get_results(data)
        # Wyświetl obrazy
        display_images(results)
    except Exception as e:
        # Błąd w logu
        text_log.insert(tk.END, f"B\u0142\u0105d: {e}\n")

# --- GUI ---
# Główne okno
window = tk.Tk()
# Tytuł
window.title("NASA Search API")
# Rozmiar okna
window.geometry("1280x720")
# Kolor tła
window.configure(bg=BG_COLOR)

# Konfiguracja kolumn
# Równomierny rozkład
for r in range(4):
    window.columnconfigure(r, weight=1)

# Ramka wejściowa
input_frame = tk.Frame(master=window, bg=BG_COLOR)
input_frame.grid(row=0, column=0, columnspan=3, sticky="new", padx=10, pady=10)

# Etykieta
create_label(input_frame, text="Podaj zapytanie:").grid(row=0, column=1, padx=5, pady=5)

# Pole tekstowe
entry = create_entry(input_frame, width=30)
entry.grid(row=0, column=2, padx=5, pady=5)

# Przycisk szukaj
search_btn = create_button(input_frame, text="Szukaj", command=search_image)
search_btn.grid(row=0, column=3, padx=5, pady=5)

# Obszar wyników z przewijaniem
# Obszar przewijania
canvas = tk.Canvas(window, bg=BG_COLOR, highlightthickness=0)
canvas.grid(row=1, column=0, columnspan=4, rowspan=3, sticky="nsew")

# Scroll pionowy
scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview, bg=BG_COLOR,
                         troughcolor=BG_COLOR, activebackground=BG_COLOR, highlightbackground=BG_COLOR)
scrollbar.grid(row=1, column=4, rowspan=3, sticky="ns")
# Połączenie scrollbara z canvase
canvas.configure(yscrollcommand=scrollbar.set)

# Ramka wyników
output_frame = tk.Frame(canvas, bg=BG_COLOR)
# Umieszczona w canvasie
output_window = canvas.create_window((0, 0), window=output_frame, anchor="nw")

# Przeskalowanie obszaru przewijania
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# Aktualizacja obszaru przy zmianach
output_frame.bind("<Configure>", on_frame_configure)

# Logi
# Ramka logów
log_frame = tk.Frame(master=window, bg=BG_COLOR)
log_frame.grid(row=1, column=5, columnspan=1, rowspan=3, sticky="n")

# Tytuł sekcji logów
create_label(log_frame, text="Logi:").grid(row=0, column=0, padx=5, pady=5)

# Pole tekstowe do logów
text_log = tk.Text(log_frame, width=40, height=40, fg=FG_COLOR, bg=BG_COLOR, insertbackground=FG_COLOR)
text_log.grid(row=1, column=0, padx=5, pady=5)

# Uruchomienie aplikacji
window.mainloop()