import tkinter as tk
from tkinter import ttk
import settings  # Importer Settings-klassen fra settings.py

class StepSettingsForm(tk.Toplevel):
    def __init__(self, parent, index_name=None, name=None, time=None, SP=None):
        super().__init__(parent)
        self.title(settings.STEP_SETTINGS_FORM_TITLE)
        self.parent = parent
        
        self.grab_set()  # Gør modalvinduet aktivt og inaktiverer hovedvinduet
        self.focus_set()  # Sæt fokus på modalvinduet
        self.ok_pressed=False
        self.index_name=index_name
        self.name=name
        self.time=time
        self.SP=SP
        self.configure(bg=settings.BACKGROUND_COLOR)  # Baggrundsfarve for mørkt tema

        self.columnconfigure(1, weight=1)

        self.step_var = tk.StringVar(value=name)
        self.time_var = tk.StringVar(value=time)
        self.sp_var = tk.StringVar(value=SP)

        tk.Label(self, text=settings.STEP_COLLUMN_NAME + ":",
                 bg=settings.BACKGROUND_COLOR,
                 fg=settings.FOREGROUND_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        tk.Entry(self, textvariable=self.step_var, bg=settings.BACKGROUND_COLOR,
                 fg=settings.FOREGROUND_COLOR,
                 insertbackground=settings.FOREGROUND_COLOR).grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        tk.Label(self, text=settings.TIME_COLLUMN_NAME + ":",
                 bg=settings.BACKGROUND_COLOR,
                 fg=settings.FOREGROUND_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        tk.Entry(self, textvariable=self.time_var,
                 bg=settings.BACKGROUND_COLOR,
                 fg=settings.FOREGROUND_COLOR,
                 insertbackground=settings.FOREGROUND_COLOR).grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        tk.Label(self, text=settings.SP_COLLUMN_NAME + ":",
                 bg=settings.BACKGROUND_COLOR,
                 fg=settings.FOREGROUND_COLOR).grid(row=2, column=0, padx=5, pady=5, sticky='e')
        tk.Entry(self, textvariable=self.sp_var, bg=settings.BACKGROUND_COLOR,
                 fg=settings.FOREGROUND_COLOR,
                 insertbackground=settings.FOREGROUND_COLOR).grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        ok_button = tk.Button(self, text=settings.OK_BUTTON_TEXT, command=self.ok_button_clicked)
        ok_button.grid(row=3, column=0, pady=10)

        add_task_button = tk.Button(self, text=settings.ADD_TASK_BUTTON_TEXT, command=self.add_task_button_clicked)
        add_task_button.grid(row=3, column=1, pady=10)

        cancel_button = tk.Button(self, text=settings.CLOSE_BUTTON_TEXT, command=self.cancel_button_clicked)
        cancel_button.grid(row=3, column=2, pady=10)

    def add_task_button_clicked(self):
        edit_entry_form = TaskSettingsForm.TaskSettingsForm(self)
        edit_entry_form.wait_window(edit_entry_form)

    def cancel_button_clicked(self):
        self.close_modal_form()

    def ok_button_clicked(self):
        self.name=self.step_var.get()
        self.time=self.time_var.get()
        self.SP=self.sp_var.get()
        self.ok_pressed=True
        self.close_modal_form()

    def close_modal_form(self):
        self.destroy()
        self.parent.focus_set()  # Giver fokus tilbage til hovedvinduet
