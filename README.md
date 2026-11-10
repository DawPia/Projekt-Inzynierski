## Wymagania wstępne

Aplikacja wymaga:
* **Python 3.10+** – [Pobierz Python](https://www.python.org/downloads/) (podczas instalacji zaznacz opcję **"Add Python to PATH"**).
* **Git** – [Pobierz Git](https://git-scm.com/downloads).

---

## Instrukcja instalacji

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/DawPia/Projekt-Inzynierski.git
cd Projekt-Inzynierski
```

### 2. Utworzenie i aktywacja środowiska wirtualnego

* **Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalacja wymaganych pakietów

```bash
pip install -r requirements.txt
```

---

## Uruchomienie aplikacji

```bash
python manage.py runserver
```

Po wszystkim wejdź na adres http://127.0.0.1:8000 bądź inny który pojawi się przy linijce "Starting development server at " w terminalu
