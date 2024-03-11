import tkinter as tk
from tkinter import ttk
import settings  # Importer Settings-klassen fra settings.py
        
class TaskSettingsForm(tk.Toplevel):
    def __init__(self, parent, index_name=None, name=None, time=None):
        super().__init__(parent)
        self.title(settings.TASK_SETTINGS_FORM_TITLE)
        self.parent = parent
        self.ok_pressed=False
        self.index_name=index_name
        self.name=name
        self.time=time
        self.configure(bg=settings.BACKGROUND_COLOR)  # Baggrundsfarve for mørkt tema

        self.columnconfigure(1, weight=1)

        self.task_var = tk.StringVar(value=name)
        self.time_var = tk.StringVar(value=time)

        tk.Label(self, text=settings.TASK_COLLUMN_NAME + ":",
                 bg=settings.BACKGROUND_COLOR,
                 fg=settings.FOREGROUND_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        tk.Entry(self, textvariable=self.task_var,
                 bg=settings.BACKGROUND_COLOR,
                 fg=settings.FOREGROUND_COLOR,
                 insertbackground=settings.FOREGROUND_COLOR).grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        tk.Label(self, text=settings.TIME_COLLUMN_NAME + ":",
                 bg=settings.BACKGROUND_COLOR,
                 fg=settings.FOREGROUND_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        tk.Entry(self, textvariable=self.time_var,
                 bg=settings.BACKGROUND_COLOR,
                 fg=settings.FOREGROUND_COLOR,
                 insertbackground=settings.FOREGROUND_COLOR).grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        ok_button = tk.Button(self, text=settings.OK_BUTTON_TEXT, command=self.ok_button_clicked)
        ok_button.grid(row=3, column=0, pady=10)

        cancel_button = tk.Button(self, text=settings.CLOSE_BUTTON_TEXT, command=self.cancel_button_clicked)
        cancel_button.grid(row=3, column=2, pady=10)

    def cancel_button_clicked(self):
        self.close_modal_form()

    def ok_button_clicked(self):
        self.name=self.task_var.get()
        self.time=self.time_var.get()
        self.ok_pressed=True
        self.close_modal_form()

    def close_modal_form(self):
        self.destroy()
        self.parent.focus_set()  # Giver fokus tilbage til hovedvinduet
