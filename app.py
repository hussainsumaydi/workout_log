import json
import socket
import tkinter as tk
from tkinter import messagebox, ttk
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

BASE_URL = 'http://127.0.0.1:5050'


class WorkoutApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Workout Log')
        self.geometry('620x460')
        self.selected_id = None

        # --- Input fields (row 0 to 2) ---
        tk.Label(self, text='Exercise Name:').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.name_box = tk.Entry(self, width=25)
        self.name_box.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text='Target Muscle:').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.muscle_box = tk.Entry(self, width=25)
        self.muscle_box.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self, text='Weight (kg):').grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.weight_box = tk.Entry(self, width=25)
        self.weight_box.grid(row=2, column=1, padx=10, pady=5)

        # --- Action buttons (row 3) ---
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=8)

        tk.Button(btn_frame, text='Add Workout', command=self.add_workout).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text='Update Selected', command=self.update_workout).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text='Delete Selected', command=self.delete_workout).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text='Clear Fields', command=self.clear_fields).grid(row=0, column=3, padx=5)

        # --- Extra feature: Filter by Muscle (row 4) ---
        filter_frame = tk.Frame(self)
        filter_frame.grid(row=4, column=0, columnspan=3, pady=5)

        tk.Label(filter_frame, text='Filter by Muscle:').grid(row=0, column=0, padx=5)
        self.filter_box = tk.Entry(filter_frame, width=18)
        self.filter_box.grid(row=0, column=1, padx=5)
        tk.Button(filter_frame, text='Filter', command=self.filter_workouts).grid(row=0, column=2, padx=5)
        tk.Button(filter_frame, text='Show All', command=self.load_workouts).grid(row=0, column=3, padx=5)

        # --- Table of workouts (row 5) ---
        cols = ('id', 'name', 'muscle', 'weight')
        self.table = ttk.Treeview(self, columns=cols, show='headings', height=10)
        self.table.heading('id', text='ID')
        self.table.heading('name', text='Exercise')
        self.table.heading('muscle', text='Muscle')
        self.table.heading('weight', text='Weight (kg)')

        self.table.column('id', width=50, anchor='center')
        self.table.column('name', width=200)
        self.table.column('muscle', width=150)
        self.table.column('weight', width=120, anchor='center')

        self.table.grid(row=5, column=0, columnspan=3, padx=15, pady=10)
        self.table.bind('<<TreeviewSelect>>', self.on_select)

        # --- Status label for success/error messages (row 6) ---
        self.status_label = tk.Label(self, text='Ready.', fg='blue')
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)

        self.load_workouts()

    def set_status(self, message, is_error=False):
        color = 'red' if is_error else 'green'
        self.status_label.config(text=message, fg=color)

    def send_request(self, path, values=None):
        url = BASE_URL + path
        try:
            if values is None:
                with urlopen(url, timeout=5) as reply:
                    return json.loads(reply.read().decode('utf-8'))
            else:
                body = urlencode(values).encode('utf-8')
                with urlopen(url, data=body, timeout=5) as reply:
                    return json.loads(reply.read().decode('utf-8'))
        except HTTPError as error:
            raw = error.read().decode('utf-8')
            data = json.loads(raw)
            self.set_status(data.get('error', 'Server error.'), is_error=True)
            return None
        except socket.timeout:
            self.set_status('Connection timed out. Check if Flask is running.', is_error=True)
            return None
        except URLError:
            self.set_status('Cannot connect to server. Start Flask and try again.', is_error=True)
            return None

    def fill_table(self, workouts):
        for item in self.table.get_children():
            self.table.delete(item)
        for w in workouts:
            self.table.insert('', 'end', values=(w['id'], w['name'], w['muscle'], w['weight']))

    def load_workouts(self):
        self.filter_box.delete(0, tk.END)
        data = self.send_request('/workouts')
        if data is not None:
            workouts = data['workouts']
            self.fill_table(workouts)
            if not workouts:
                self.set_status('No workouts saved yet.')
            else:
                self.set_status(f'Loaded {len(workouts)} workout(s).')

    def filter_workouts(self):
        muscle = self.filter_box.get().strip()
        if not muscle:
            self.load_workouts()
            return
        query = urlencode({'muscle': muscle})
        data = self.send_request('/workouts?' + query)
        if data is not None:
            workouts = data['workouts']
            self.fill_table(workouts)
            if not workouts:
                self.set_status(f'No workouts found for muscle: {muscle}')
            else:
                self.set_status(f'Showing {len(workouts)} workout(s) for {muscle}.')

    def on_select(self, event):
        selected = self.table.selection()
        if not selected:
            return
        values = self.table.item(selected[0], 'values')
        self.selected_id = values[0]

        self.name_box.delete(0, tk.END)
        self.name_box.insert(0, values[1])

        self.muscle_box.delete(0, tk.END)
        self.muscle_box.insert(0, values[2])

        self.weight_box.delete(0, tk.END)
        self.weight_box.insert(0, values[3])

    def clear_fields(self):
        self.selected_id = None
        self.name_box.delete(0, tk.END)
        self.muscle_box.delete(0, tk.END)
        self.weight_box.delete(0, tk.END)
        for item in self.table.selection():
            self.table.selection_remove(item)
        self.set_status('Fields cleared.')

    def add_workout(self):
        values = {
            'name': self.name_box.get(),
            'muscle': self.muscle_box.get(),
            'weight': self.weight_box.get()
        }
        result = self.send_request('/workouts/add', values)
        if result is not None:
            self.clear_fields()
            self.load_workouts()
            self.set_status(result['message'])

    def update_workout(self):
        if self.selected_id is None:
            self.set_status('Select a workout from the table first.', is_error=True)
            return
        values = {
            'id': self.selected_id,
            'name': self.name_box.get(),
            'muscle': self.muscle_box.get(),
            'weight': self.weight_box.get()
        }
        result = self.send_request('/workouts/edit', values)
        if result is not None:
            self.clear_fields()
            self.load_workouts()
            self.set_status(result['message'])

    def delete_workout(self):
        if self.selected_id is None:
            self.set_status('Select a workout from the table first.', is_error=True)
            return
        confirm = messagebox.askyesno('Confirm Delete', 'Are you sure you want to delete this workout?')
        if not confirm:
            return
        result = self.send_request('/workouts/delete', {'id': self.selected_id})
        if result is not None:
            self.clear_fields()
            self.load_workouts()
            self.set_status(result['message'])


if __name__ == '__main__':
    app = WorkoutApp()
    app.mainloop()