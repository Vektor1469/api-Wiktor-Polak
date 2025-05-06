import requests
import json
import tkinter as tk
from tkinter import ttk
from result import Ok, Err, Result, is_ok, is_err

class NasaImageFetcher:

    def __init__(self):
        self.base_url = "https://images-api.nasa.gov/search"


    def fetch_data(self, query):
        params_query = {
            'q': query
        }
        response = requests.get(self.base_url, params=params_query)

        if response.status_code == 200:
            print("\nPobrano dane pomyślnie.")
            return response.json()
        else:
            raise Exception(f'Nie udało się, kod statusu: {response.status_code}')


    def display_results(self, data, limit=30, log_widget=None):
        results = []
        if not data:
            if log_widget:
                log_widget.insert(tk.END, "Brak danych\n")
            return

        items = data.get("collection", {}).get("items", [])

        if not items:
            if log_widget:
                log_widget.insert(tk.END, "Brak wyników\n")
            return

        if log_widget:
            log_widget.insert(tk.END, f"\nZnaleziono {len(items)} wyników. Wyswietlono {limit} z nich:\n")

        for item in items[:limit]:
            item_data = item.get("data", [])
            links = item.get("links", [])

            title = item_data[0].get("title", "Brak Tutułu") if item_data else "Brak Tytułu"

            href = links[0].get("href", "Brak linku") if links else "Brak linku"

            if log_widget:
                log_widget.insert(tk.END, f"Tytuł: {title}\n")
                log_widget.insert(tk.END, f"Link : {href}\n")
                log_widget.insert(tk.END, "-" * 40 + "\n")

            if href:
                results.append({'title': title, 'image_url': href})
        return results
        
    def get_results(self, data, limit=30):
        results = []
        if not data:
            return results

        items = data.get("collection", {}).get("items", [])
        for item in items[:limit]:
            item_data = item.get("data", [])
            links = item.get("links", [])

            title = "Brak tytułu"
            if isinstance(item_data, list) and item_data and isinstance(item_data[0], dict):
                title = item_data[0].get("title", "Brak tytułu")

            href = None
            if isinstance(links, list) and links and isinstance(links[0], dict):
                href = links[0].get("href", None)

            if href:
                results.append({'title': title, 'image_url': href})

        return results

    def run(self):
        query = input("Podaj zapytanie: ")
        try:
            data = self.fetch_data(query)
            self.display_results(data)
        except Exception as error:
            print(f"Błąd: {error}")

if __name__ == "__main__":
    fetcher = NasaImageFetcher()
    fetcher.run()