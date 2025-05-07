# Importuje bibliotekę requests do obsługi żądań HTTP
import requests

# Importuje tkinter do obsługi GUI (graficznego interfejsu użytkownika)
import tkinter as tk

# Definicja klasy do pobierania i przetwarzania danych z API NASA
class NasaImageFetcher:
    # Konstruktor klasy - ustawia podstawowy URL dla wyszukiwania obrazów NASA
    def __init__(self):
        self.base_url = "https://images-api.nasa.gov/search"

    # Metoda do pobierania danych z API na podstawie zapytania użytkownika
    def fetch_data(self, query):
        # Wysyła żądanie GET do API z parametrem zapytania
        response = requests.get(self.base_url, params={'q': query})
        # Sprawdza, czy odpowiedź zakończyła się sukcesem (kod 200)
        if response.status_code == 200:
            # Informuje o pomyślnym pobraniu danych
            print("\nPobrano dane pomyślnie.")
            # Zwraca dane w formacie JSON
            return response.json()
        else:
            # Rzuca wyjątek, jeśli odpowiedź była nieprawidłowa
            raise Exception(f'Nie udało się, kod statusu: {response.status_code}')

    # Metoda pomocnicza do wyciągania listy wyników (tytułów i linków do obrazów) z danych JSON
    def extract_results(self, data, limit=30):
        # Inicjalizuje pustą listę wyników
        results = []
        # Zwraca pustą listę, jeśli nie ma danych
        if not data:
            return results

        # Pobiera listę elementów z odpowiedzi API
        items = data.get("collection", {}).get("items", [])
        # Iteruje przez maksymalnie `limit` elementów
        for item in items[:limit]:
            # Pobiera sekcję "data" dla danego elementu (zwykle zawiera tytuł)
            item_data = item.get("data", [])
            # Pobiera sekcję "links" (zwykle zawiera link do obrazka)
            links = item.get("links", [])

            # Pobiera tytuł z pierwszego elementu "data" lub ustawia domyślny tekst
            title = item_data[0].get("title", "Brak tytułu") if item_data else "Brak tytułu"
            # Pobiera link do obrazka z pierwszego elementu "links" lub None
            href = links[0].get("href") if links else None

            # Dodaje wynik do listy tylko jeśli istnieje link
            if href:
                results.append({'title': title, 'image_url': href})
        # Zwraca listę wyników
        return results

    # Metoda do wyświetlania wyników w widżecie tekstowym GUI lub zwracania listy wyników
    def display_results(self, data, limit=30, log_widget=None):
        # Wyciąga listę wyników z danych
        results = self.extract_results(data, limit)

        # Jeśli nie przekazano widżetu GUI (log_widget), tylko zwraca wyniki
        if log_widget is None:
            return results

        # Jeśli dane są puste, informuje użytkownika
        if not data:
            log_widget.insert(tk.END, "Brak danych\n")
            return results

        # Pobiera listę elementów z odpowiedzi
        items = data.get("collection", {}).get("items", [])
        # Jeśli brak elementów, wyświetla stosowny komunikat
        if not items:
            log_widget.insert(tk.END, "Brak wyników\n")
            return results

        # Informuje użytkownika o liczbie znalezionych i wyświetlanych wyników
        log_widget.insert(tk.END, f"\nZnaleziono {len(items)} wyników. Wyświetlono {len(results)} z nich:\n")
        # Iteruje przez wyniki i wyświetla każdy tytuł i link w widżecie
        for result in results:
            log_widget.insert(tk.END, f"Tytuł: {result['title']}\n")
            log_widget.insert(tk.END, f"Link : {result['image_url']}\n")
            log_widget.insert(tk.END, "-" * 40 + "\n")
        # Zwraca listę wyników
        return results

    # Metoda alternatywna do zwracania wyników bez wyświetlania (do wykorzystania w innych kontekstach)
    def get_results(self, data, limit=30):
        return self.extract_results(data, limit)

    # Metoda uruchamiająca aplikację w wersji terminalowej
    def run(self):
        # Pobiera zapytanie od użytkownika
        query = input("Podaj zapytanie: ")
        try:
            # Pobiera dane z API na podstawie zapytania
            data = self.fetch_data(query)
            # Wyświetla wyniki w konsoli
            self.display_results(data)
        # Obsługuje wyjątki i wyświetla błąd, jeśli wystąpi
        except Exception as error:
            print(f"Błąd: {error}")