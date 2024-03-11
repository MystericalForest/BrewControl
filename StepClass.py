# StepClass.py
import settings  # Importer Settings-klassen fra settings.py
import TaskClass
#import TasksClass

class StepClass:
    def __init__(self, name, time, SP):
        self.tasks=[]
        self.name=name
        self.time=int(time)
        self.SP=int(SP)
        self.index=None
        self.index_name=None

    def add_new_task(self, name, time):
        task=TaskClass.TaskClass(name, time)
        self.tasks.append(task)
        self.reindex()

    def reindex(self):
        self.tasks.sort(key=lambda x: x.time, reverse=False)
        for idx, task in enumerate(self.tasks):
            task.index=idx
            task.index_name="T" + str(idx)

    def has_tasks(self):
        if (len(self.tasks)>0):
            return True
        return False

    def get_tasks(self):
        return self.tasks

    def get_step_by_id(self, index_name):
        for x in self.tasks:
            if x.index_name == index_name:
                return x
        return
        
    def get_step_by_index_name(self, index_name):
        for x in self.tasks:
            if x.index_name == index_name:
                return x
                break
        return

    def get_task_times(self):
        rtn=[]
        for x in self.tasks:
            rtn.append(x.get_times())
        return rtn
        
