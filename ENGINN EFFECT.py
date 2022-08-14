class CheckResidual:
    def __init__(self, log_in, log_out):
        self.log_in, self.log_out = log_in, log_out
        self.times, self.omega, self.k, self.p_rgh = [], [], [], []

    # Opening of data input and data collection
    def data_extraction(self):
        with open(self.log_in) as f:
            lines = f.readlines()
            # "temp_data" is being used to store last found line which could be used as p_rgh - need to find last one
            temp_data = ""
            for line in lines:
                # This block is being used to tell, which line is supposed to be used for which variable, based on
                # different strings in input file
                if "GAMG:  Solving for p_rgh, Initial residual" in line:
                    temp_data = line
                elif "Time =" in line and "ExecutionTime" not in line:
                    self.times.append(float(str(line.replace("Time = ", ""))))
                elif "smoothSolver:  Solving for omega" in line:
                    for _ in line.split(","):
                        if " Final residual = " in _:
                            self.omega.append(float(str(_.replace(" Final residual = ", ""))))
                elif "smoothSolver:  Solving for k," in line:
                    for _ in line.split(","):
                        if " Final residual = " in _:
                            self.k.append(float(str(_.replace(" Final residual = ", ""))))
                    for _ in temp_data.split(","):
                        if " Final residual = " in _:
                            self.p_rgh.append(float(str(_.replace(" Final residual = ", ""))))

    # Saving of data into .txt document
    def data_save(self):
        f = open(self.log_out, "w+")
        # Header creation
        f.write("Columns are in order - Times / p_rgh / omega / k\n")
        for i in range(len(self.times)):
            f.write(str(self.times[i]) + ", " + str(self.p_rgh[i]) + ", " + str(self.omega[i]) + ", " + str(self.k[i]) + "\n")

    # Graph plot
    def data_plot(self):
        import matplotlib.pyplot as plt

        # This block is responsible for different plots for each requested combination
        plt.plot(self.times, self.p_rgh)
        plt.plot(self.times, self.omega)
        plt.plot(self.times, self.k)

        # Changing of labels / title and requested logarithmic scale
        plt.xlabel('Čas')
        plt.ylabel('Final residual (log)')
        plt.title('Průběh reziduí')
        plt.yscale('log')

        plt.show()


class DynamicTermination:
    def __init__(self, log_in):
        self.log_in = log_in
        self.times, self.Water_fraction = [], []

    # Opening of data input and data collection
    def data_extraction(self):
        with open(self.log_in) as f:
            lines = f.readlines()
            # "sorting_counter" is being used for altering between "times" and "Water_fraction" data
            sorting_counter = 0
            for line in lines:
                # Skipping of first lines with headers
                if "#" in line:
                    continue
                else:
                    for _ in line.split(" "):
                        if _ != "" and sorting_counter == 0:
                            self.times.append(_)
                            sorting_counter = 1
                            continue
                        elif _ != "" and sorting_counter == 1:
                            self.Water_fraction.append(float(_))
                            sorting_counter = 0
                            continue

    # Calculation of first suitable moment for process termination (has to meet both conditions)
    def time_solution(self):
        # Conditions settings
        time_boundary, maximal_allowed_value, value_boundary = 20000, 0.5, 0.1

        # Looping through dataset "Water_fraction" - checking for the first condition - maximal_allowed_value
        for index, value in enumerate(self.Water_fraction):
            if value > maximal_allowed_value:
                continue
            else:
                # Check of next condition - time_boundary / value_boundary
                check = False
                for i in range(time_boundary):
                    if abs(value - self.Water_fraction[index - i]) > value_boundary:
                        check = True
                        break
                if not check:
                    print("First suitable moment for process termination is at " + self.times[index] + " seconds.")
                    break


# Launch of "CheckResidual" - 1st argument = input file in directory 2nd argument = output file (will be created)
RunResidual = CheckResidual("log.run", "log.txt")
CheckResidual.data_extraction(RunResidual)
CheckResidual.data_save(RunResidual)
CheckResidual.data_plot(RunResidual)


# Launch of "DynamicTermination" - 1st argument = input file in directory
RunDynamicTermination = DynamicTermination("alpha.water")
DynamicTermination.data_extraction(RunDynamicTermination)
DynamicTermination.time_solution(RunDynamicTermination)
