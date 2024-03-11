import BrewStep
import DataLogger_Sim
import Setpoint
from enum import Enum

class Brew_status(Enum):
    NOT_STARTED = 1
    STARTED = 2
    PAUSED = 3
    STOPPED = 4
    ERROR = 5

class BrewController:
    def __init__(self, steps):
        # Initializer for BrewController class
        self.first = None           # Reference to the first node in the linked list
        self.last = None            # Reference to the last node in the linked list
        self.active_brew_step = None     # Reference to the currently active step
        self.steps = steps
        self.status=Brew_status.NOT_STARTED
        self.datalogger=DataLogger_Sim.DataLogger_Sim()
        self.setpoints=[]
        self.setpoints.append(Setpoint.Setpoint(0,65))
        self.setpoints.append(Setpoint.Setpoint(15,85))
        self.setpoints.append(Setpoint.Setpoint(35,85))
        self.generate_brew_control_default_data()  # Generate default brewing steps

    def add_brew_step(self, name):
        # Adds a new BrewStep to the linked list
        new_node = BrewStep.BrewStep(name)
        if (self.first is None):
            # If the list is empty, set the new node as the first node
            self.first = new_node
        new_node.previous_node = self.last
        if (self.last is not None):
            # If there is a last node, set its next_node to the new node
            self.last.next_node = new_node
        self.last = new_node         # Update last to the new node
        self.active_brew_step = new_node  # Set the active step to the new node

    def switch_active_brew_step(self, name):
        # Finds and sets the active step to the one with the given name
        current_node = self.first
        while current_node:
            if current_node.name == name:
                self.active_step = current_node
                return
            current_node = current_node.next_node

    def display_all_brew_step(self):
        # Prints the names of all brew steps in the linked list
        current_node = self.first
        while current_node:
            print("Brew Step:", str(current_node)) #.name)
            current_node = current_node.next_node

    def next_brew_step(self):
        # Moves the active step to the next step in the linked list
        if self.active_brew_step is not None:
            if self.status==Brew_status.STARTED:
                self.active_brew_step.stop_brew_step()
                if self.active_brew_step.next_node is not None:
                    self.active_brew_step.next_node.start_brew_step()
                else:
                    self.status=Brew_status.STOPPED
            self.active_brew_step = self.active_brew_step.next_node

    def start_brew(self):
        if (self.status==Brew_status.NOT_STARTED
            or self.status==Brew_status.PAUSED
            or self.status==Brew_status.STOPPED):
            self.status=Brew_status.STARTED
            self.active_brew_step.start_brew_step()

    def stop_brew(self):
        if (self.status==Brew_status.STARTED
            or self.status==Brew_status.PAUSED):
            self.status=Brew_status.STOPPED
            self.active_brew_step.stop_brew_step()

    def pause_brew(self):
        if self.status==Brew_status.STARTED:
            self.status=Brew_status.PAUSED
            self.active_brew_step.pause_brew_step()

    def reset_brew(self):
        self.status=Brew_status.NOT_STARTED
        self.active_brew_step.reset_brew_step()
        self.active_brew_step=self.first

    def get_status(self):
        if (self.status==Brew_status.NOT_STARTED):
            return "Not started"
        if (self.status==Brew_status.STARTED):
            return "Started"
        if (self.status==Brew_status.PAUSED):
            return "Paused"
        if (self.status==Brew_status.STOPPED):
            return "Stopped"
        return "Error"
        
    def get_active_brew_step_name(self):
        # Returns the name of the currently active brew step
        if self.active_brew_step:
            return self.active_brew_step.name
        else:
            return "No active brew steps."

    def get_set_point_data(self):
        x=[]
        y=[]
        time=0
        for idx, step in enumerate(self.steps.steps):
            x.append(time)
            y.append(step.SP)
            time=step.time
            x.append(time)
            y.append(step.SP)
        return x, y

    def get_logger_data(self):
        return self.datalogger.x_values,self.datalogger.y_values

    def get_tast_times(self):
        return self.steps.get_task_times() #[4,10,25,28]

    def get_x_axis_min(self):
        return 0

    def get_current_timestamp(self):
        return self.datalogger.get_logger_timestamp()

    def get_x_axis_max(self):
        sp_x, _ = self.get_set_point_data()
        logger_x=self.datalogger.get_logger_timestamp()
        return max(max(sp_x), logger_x)

    def get_set_point(self, timestamp):
        for idx, SP in enumerate(self.setpoints):
            if SP.time_point>timestamp:
                return self.setpoints[idx-1].temperature
        return self.setpoints[-1].temperature            

    def update_data(self):
        timestamp=self.get_current_timestamp()
        SP=self.get_set_point(timestamp)
        return self.datalogger.update_data(SP)

    def __len__(self):
        # Returns the number of steps in the Brew Controller
        current_node = self.first
        count=0
        while current_node:
            count+=1
            current_node = current_node.next_node
        return count
            
    def generate_brew_control_default_data(self):
        # Initializes the linked list with default brewing steps and sets the active step to the first step
        self.add_brew_step("Step 1")
        self.add_brew_step("Step 2")
        self.add_brew_step("Step 3")
        self.add_brew_step("Step 4")
        self.active_brew_step = self.first

# Eksempel på brug:
if __name__ == "__main__":
    BrewController_instance = BrewController()

    # Vis aktiv underklasse
    print(BrewController_instance.active_brew_step)

    # Skift aktiv underklasse
    BrewController_instance.next_brew_step()
    BrewController_instance.next_brew_step()

    # Vis igen aktiv underklasse
    print(BrewController_instance.active_brew_step)

    # Vis alle underklasser
    print()
    BrewController_instance.display_all_brew_step()
