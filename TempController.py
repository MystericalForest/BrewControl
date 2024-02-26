import random

# Demo class. Must be replaced with a class
# fetching data from the physical termologgers.

class TempController:
    def __init__(self, setpoint):
        self.setpoint=setpoint

    def get_temperatur(self):
        return self.setpoint+4*random.random()-2
        
