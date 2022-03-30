import pandas as pd
import matplotlib.pyplot as plt


data_path = "pdp_gen_times.csv"
time_data = pd.read_csv(data_path)



plt.xlabel("Number of Features")
plt.ylabel("Seconds")
plt.title("Time to generate PDP's")
plt.legend(loc="upper right")
plt.show()
