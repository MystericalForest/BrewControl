# StepsClass.py
import settings  # Importer Settings-klassen fra settings.py
import StepClass

class StepsClass:
    def __init__(self):
        self.steps=[]

    def add_new_step(self, name, time, SP):
        step=StepClass.StepClass(name, time, SP)
        self.steps.append(step)
        self.reindex()

    def edit_step(self, index_name, name, time, SP):
        step=self.get_step_by_index_name(index_name)
        step.name=name
        step.time=int(time)
        step.SP=int(SP)
        self.reindex()

    def add_new_task(self, index, name, time):
        self.steps[index].add_new_task(name, time)

    def edit_task(self, index_name, name, time):
        task=self.get_task_by_index_name(index_name)
        task.name=name
        task.time=time
        self.reindex()

    def reindex(self):
        self.steps.sort(key=lambda x: x.time, reverse=False)
        for idx, step in enumerate(self.steps):
            step.index=idx
            step.index_name="S" + str(idx)
        

    def get_entry_by_name(self, name):
        for x in self.steps:
            if x.name == name:
                return x
                break
            else:
                x = None
            if x.has_tasks:
                for y in x.tasks.tasks:
                    if y.name == name:
                        return y
                        break
                    else:
                       y = None
        return

    def get_step_by_id(self, index_name):
        for x in self.steps:
            if x.index_name == index_name:
                return x
        return
        
    def get_step_by_index_name(self, index_name):
        for x in self.steps:
            if x.index_name == index_name:
                return x
                break
        return
        
    def get_task_by_index_name(self, index_name):
        index_split=index_name.split("T")
        step_index=index_split[0]
        task_index="T"+index_split[1]
        print(task_index)
        step=self.get_step_by_index_name(step_index)
        for x in step.tasks:
            if x.index_name == task_index:
                return x
                break
        return

    def get_task_by_name(self, name):
        for x in self.steps:
            if x.has_tasks:
                for y in x.tasks.tasks:
                    if y.name == name:
                        return y
                        break
        return

    def get_task_times(self):
        rtn=[]
        for x in self.steps:
            rtn=rtn+x.get_task_times()
        return rtn
