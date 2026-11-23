# Workout Log (Client-Server Application)

A desktop client-server application built with a **Python Tkinter** graphical front end, a **Flask** REST/JSON back end, and an **SQLite** database. Users can add, view, edit, delete, and filter workout exercises by target muscle directly from the GUI without manually entering server addresses or URLs.

---

## Setup and Run Instructions

### 1. Install Required Packages
Make sure Python 3 is installed, then install Flask from the project folder:
```bash
python -m pip install -r requirements.txt
```

### 2. Create the Database Table (Optional Sample Data)
Run `workout_store.py` once to initialize `workouts.db` and populate initial sample workouts (the server also creates the table automatically if missing):
```bash
python workout_store.py
```

### 3. Start the Flask Back-End Server
Start the Flask server on port `5050` first and keep its terminal running:
```bash
python server.py
```

### 4. Start the Tkinter Front-End Application
Open a second terminal in the project folder and launch the GUI:
```bash
python app.py
```

### 5. Run the Threaded Report Helper
While the Flask server is running, open a terminal and run:
```bash
python report.py
```
This fetches the saved workouts from `http://127.0.0.1:5050/workouts` and writes a formatted UTF-8 summary to `workout_report.txt` using a separate thread.

---

## Course Topics Location

| Topic | Evidence in Project (File & Class/Function) |
| :--- | :--- |
| **Python and collections** | Lists of `Workout` objects and dictionaries (`to_dict()`) used in `workout_store.py` (`Workout`, `WorkoutStore.all`), `server.py` (`get_workouts`), and `app.py` (`fill_table`, `add_workout`). |
| **Exceptions** | Input validation (`ValueError`) in `server.py` (`add_workout`, `edit_workout`, `delete_workout`); HTTP and network error handling (`HTTPError`, `socket.timeout`, `URLError`) in `app.py` (`send_request`); file error handling (`OSError`) in `report.py` (`write_report`). |
| **Classes** | `Workout` and `WorkoutStore` in `workout_store.py` for data modeling and SQLite access; `WorkoutApp(tk.Tk)` in `app.py` for the GUI window. |
| **SQLite** | `WorkoutStore` in `workout_store.py` (`__init__`, `add`, `all`, `filter_by_muscle`, `find`, `update`, `delete`) using `CREATE TABLE IF NOT EXISTS`, SQL placeholders (`?`), `with self.conn:`, and per-request connections closed in `finally:` blocks in `server.py`. |
| **Threads and files** | `report.py` (`main` and `write_report`) creates a `threading.Thread`, runs `start()` and `join()`, and writes `workout_report.txt` using `with open(..., 'w', encoding='utf-8')`. |
| **Tkinter** | `WorkoutApp` in `app.py` uses `Label`, `Entry`, `Button`, `ttk.Treeview`, `grid()` layout, `messagebox.askyesno` for delete confirmation, and a status label for feedback. |
| **Client and server** | `WorkoutApp.send_request` in `app.py` sends `GET` and URL-encoded `POST` HTTP requests via `urllib.request.urlopen` to `http://127.0.0.1:5050` and parses JSON replies with `json.loads`. |
| **Flask** | `server.py` defines routes (`/workouts`, `/workouts/add`, `/workouts/edit`, `/workouts/delete`), validates form inputs, and returns JSON responses with HTTP status codes `200`, `400`, and `404`. |

---

## Test Results

- **CRUD Operations:** Added new exercises, viewed records in the table, edited selected records, and deleted records with confirmation; verified only the selected record was modified.
- **Extra Feature (Filter by Muscle):** Filtered workouts by muscle name (e.g., `Chest`) and restored the full list using `Show All`.
- **Data Persistence:** Stopped both Flask and Tkinter, restarted them, and confirmed all saved records remained in `workouts.db`.
- **Validation & Empty State:** Tested empty fields, non-numeric/zero weights (returned HTTP `400` and displayed clear error messages), and deleting all records (displayed `"No workouts saved yet."`).
- **Unknown ID Handling:** Selected the same record in two Tkinter windows, deleted it in the first window, and attempted to update it in the second window; Flask returned HTTP `404` (`"Workout ID not found."`) and the GUI displayed the error without crashing.
- **Connection Checks:** Stopped the Flask server and clicked an action in Tkinter; the GUI caught `URLError` and displayed `"Cannot connect to server. Start Flask and try again."` Restarted Flask and retried the action without restarting the Tkinter window.
- **Threaded Report Helper:** Ran `python report.py` while Flask was active; verified `workout_report.txt` was generated with UTF-8 encoding and listed all saved workouts.

---

## Credits & Academic Integrity

- Project structure, SQLite data access pattern, Tkinter `grid` layout, and Flask JSON routes follow the examples taught in **Advanced Programming 462** lectures by Dr. Majed Hariri.
- AI assistance was used for guidance, code structuring, and documentation review in accordance with the course academic integrity policy.