# TaskClass.py
import settings  # Importer Settings-klassen fra settings.py

class TaskClass:
    def __init__(self, name, time):
        self.name=name
        self.time=int(time)
        self.index=None
        self.index_name=None

    def get_times(self):
        return {"name": self.name, "time":self.time}
