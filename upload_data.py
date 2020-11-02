import numpy as np
import time
import pandas as pd
from influxdb import DataFrameClient as DFC
import sys
import os

client = DFC("192.168.1.251")
#if len(sys.argv) == 2:
#    file_name = sys.argv[1]
#else:
#    print("error no path given")
#    exit(-1)
cwd = os.path.dirname(os.path.realpath(__file__))
cwd_data = cwd + "/data2"
print(cwd_data)
files = np.sort(os.listdir(cwd_data))
n_files = len(files)
c = 0
total_index = 0
sz = 100000
data = np.zeros((3, sz), dtype = object)
for file_number, f in enumerate(files[::-1]):
    if (file_number > 75500):
        file_name = cwd_data + "/" + f
        print("file: {}, file_number: {}, processed: {}".format(file_name, file_number, total_index))
        try:
            data[:,c*100:(c+1)*100] = np.load(file_name, allow_pickle = True)
            c += 1
            total_index += 1
            if ((c)*100 == sz or file_number == n_files -1):
                pandas_data = pd.DataFrame(index=data[2], data = data[:2].T, columns=["inside temperature", "outside temperature"])
                print(pandas_data)
                pandas_data.index = pandas_data.index.tz_localize("US/Pacific")
                try:
                    client.write_points(pandas_data, measurement = "temperatures", batch_size = 5000, database = "home_data", time_precision = "ms")
                except:
                    print("couldnt write to influx")
                    np.save("full_data.npy", data)
                c = 0
        except:
            pass
