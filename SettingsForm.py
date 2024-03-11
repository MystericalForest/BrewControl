import tkinter as tk
from tkinter import ttk, simpledialog
import settings  # Importer Settings-klassen fra settings.py
import StepsClass, TaskSettingsForm, StepSettingsForm
        
class SettingsForm(tk.Toplevel):
    def __init__(self, parent, steps):
        super().__init__(parent)
        self.parent = parent
        self.steps = steps
        self.title(settings.SETTINGS_FORM_TITLE)
        self.configure(bg=settings.BACKGROUND_COLOR)

        # Mørkt tema
        style = ttk.Style()
        style.theme_use('clam')  # Vælg et tema, der understøtter 'clam'
        style.configure('Treeview', background=settings.BACKGROUND_COLOR,
                        fieldbackground=settings.BACKGROUND_COLOR,
                        foreground=settings.FOREGROUND_COLOR)
        style.map('Treeview', background=[('selected', settings.SELECTED_COLOR)])

        # configure the grid layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        self.tree = ttk.Treeview(self, selectmode="browse",
                                 columns=("index_name", settings.STEP_COLLUMN_NAME, settings.TIME_COLLUMN_NAME, settings.SP_COLLUMN_NAME)
                                 , show='headings')
        self.tree.heading("index_name", text="index_name")
        self.tree.heading(settings.STEP_COLLUMN_NAME, text=settings.STEP_COLLUMN_NAME)
        self.tree.heading(settings.TIME_COLLUMN_NAME, text=settings.TIME_COLLUMN_NAME)
        self.tree.heading(settings.SP_COLLUMN_NAME, text=settings.SP_COLLUMN_NAME)

        self.tree.column(settings.STEP_COLLUMN_NAME, width=150, anchor='w')
        self.tree.column(settings.TIME_COLLUMN_NAME, width=150, anchor='center')
        self.tree.column(settings.SP_COLLUMN_NAME, width=150, anchor='center')

        self.tree.grid(row=0, column=0, columnspan=4, pady=10, sticky=tk.NSEW)

        self.add_step_button = tk.Button(self, text=settings.ADD_STEP_BUTTON_TEXT, command=self.add_step_button_clicked)
        self.add_step_button.grid(row=1, column=0, pady=5)

        self.add_task_button = tk.Button(self, text=settings.ADD_TASK_BUTTON_TEXT, command=self.add_task_button_clicked)
        self.add_task_button.grid(row=1, column=1, pady=5)

        self.delete_button = tk.Button(self, text=settings.DELETE_BUTTON_TEXT, command=self.delete_button_clicked)
        self.delete_button.grid(row=1, column=2, pady=5)

        self.close_button = tk.Button(self, text=settings.CLOSE_BUTTON_TEXT, command=self.close_button_clicked)
        self.close_button.grid(row=1, column=3, pady=5)

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=4, sticky='ns')

        self.updateListView()
        self.tree.focus(0)
        self.tree.selection_set(0)

        self.tree.bind("<ButtonRelease-1>", self.OnSingleClick)
        self.tree.bind("<Double-1>", self.edit_entry)

    def updateListView(self):
        if len(self.tree.get_children())>0:
            self.tree.delete(*self.tree.get_children())

        for step in self.steps.steps:
           self.tree.insert('', tk.END, values=(step.index_name,
                                                step.name, step.time,
                                                step.SP),
                            iid=step.index, open=False) 

        # adding tasks
        no_of_steps=len(self.steps.steps)

        for step in self.steps.steps:
            if step.has_tasks():
                for task in step.get_tasks():
                    self.tree.insert('', tk.END, values=(step.index_name+task.index_name, task.name, task.time), iid=no_of_steps, open=False)
                    self.tree.move(no_of_steps, step.index, task.index)
                    no_of_steps=no_of_steps+1
        self.tree["displaycolumns"]=(settings.STEP_COLLUMN_NAME, settings.TIME_COLLUMN_NAME, settings.SP_COLLUMN_NAME)

    def OnSingleClick(self, event):
        if len(self.tree.selection())>0:
            item = self.tree.selection()[0]
            print("you clicked on", self.tree.item(item,"values"), item)
            if (self.tree.item(item, 'open')==0):
                self.tree.item(item, open=True)
            else:
                self.tree.item(item, open=False)

    def edit_entry(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item, 'values')
            if len(item_values)>3:
                index_name = item_values[0]
                step = item_values[1]
                tid = item_values[2]
                SP = item_values[3]
                edit_entry_form = StepSettingsForm.StepSettingsForm(self, index_name, step, tid, SP)
                edit_entry_form.wait_window(edit_entry_form)
                if edit_entry_form.ok_pressed:
                    self.steps.edit_step(edit_entry_form.index_name,
                                           edit_entry_form.name,
                                           edit_entry_form.time,
                                           edit_entry_form.SP)
                    self.updateListView()
            else:
                index_name = item_values[0]
                task = item_values[1]
                tid = item_values[2]
                edit_entry_form = TaskSettingsForm.TaskSettingsForm(self, index_name, task, tid)
                edit_entry_form.wait_window(edit_entry_form)
                if edit_entry_form.ok_pressed:
                    self.steps.edit_task(edit_entry_form.index_name,
                                         edit_entry_form.name,
                                         edit_entry_form.time)
                    self.updateListView()
                
    def close_button_clicked(self):
        pass
                
    def delete_button_clicked(self):
        pass
                
    def add_task_button_clicked(self):
        pass
                
    def add_step_button_clicked(self):
        # Åbn modal form og send initialværdier
        edit_entry_form = StepSettingsForm.StepSettingsForm(self)
        edit_entry_form.wait_window(edit_entry_form)
        if edit_entry_form.ok_pressed:
            self.steps.add_new_step(edit_entry_form.name,
                                    edit_entry_form.time,
                                    edit_entry_form.SP)
            self.updateListView()

if __name__ == "__main__":
    steps=StepsClass.StepsClass()
    steps.add_new_step("Mæskning", 60, 65)
    steps.add_new_task(0, '- Tilsæt bitterhumle', 15)
    steps.add_new_task(0, '- Tilsæt smagshumle', 30)
    steps.add_new_step("Udmæskning", 75, 85)
    steps.add_new_step("Kogning", 135, 100)
    steps.add_new_task(2, '- Tilsæt honning', 25)
    for item in steps.steps:
        print(item.index, item.name, item.time)
        for task in item.tasks:
            print(task.index, task.name, task.time)
    root = tk.Tk()
    app = SettingsForm(root, steps)
    root.mainloop()
