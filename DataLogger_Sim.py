import random

class DataLogger_Sim:
    def __init__(self):
        self.x_values=[1]
        self.y_values=[5]

    def get_logger_timestamp(self):
        return len(self.y_values)

    def update_data(self, set_point):
        delta_temp=set_point-self.y_values[-1]
        if delta_temp>0:
            if delta_temp>15:
                new_temp=self.y_values[-1]+15
            else:
                new_temp=self.y_values[-1]+5
        else:
           new_temp=self.y_values[-1]-5
        new_temp=random.randint(new_temp-3, new_temp+3)

        # Tilføj de nye data til listen
        self.x_values.append(self.x_values[-1] + 1)
        self.y_values.append(new_temp)
        
