import os
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import re
import datetime as dt

def main():
    history = 1 # number of days to plot
    fold = False # fold data for multi-day view
    seen_dates = {} # Dictionary for dates which have been seen 

    # check for folding or infinite history
    if len(sys.argv) >= 2:
        if (sys.argv[1] == "-r"):
            fold = True
            history = -1
        else:
            history = int(sys.argv[1])

    indoor = []
    outdoor = []
    times = []
    cwd = os.getcwd() + "/data2"
    files = os.listdir(cwd)
    now = dt.datetime.today()
    last_seen = 0

    # Look through all files
    for l in np.sort(files):
        # Look at file's date
        d = dt.datetime.strptime(re.findall(r"\d*-\d*", l)[0],'%Y%m%d-%H%M%S')
        if now-d < dt.timedelta(days=history) or history == -1:
            # if within the last "history" days, or if using all dates...
            # print(l)
            f = cwd + "/" + l
            t = np.load(f, allow_pickle = True) #load .npy data array
            if (fold == True):
                # if doing a folded view
                for i in range(len(t[0])):
                    # Look at dates for each data point
                    c_date = t[2][i].date() # current date for analysis
                    if (c_date in seen_dates):
                        # if the date has been seen before, just append the data
                        #print("seen {} before in seen_dates {}".format(c_date, seen_dates))
                        indoor[seen_dates[c_date]].append(t[0][i])
                        outdoor[seen_dates[c_date]].append(t[1][i])
                        times[seen_dates[c_date]].append(t[2][i].time())
                    else:
                        # if the date has not been seen before, make new sub list
                        print("new date: {}".format(c_date))
                        seen_dates[c_date] = last_seen
                        indoor.append([])
                        outdoor.append([])
                        times.append([])
                        indoor[last_seen].append(t[0][i])
                        outdoor[last_seen].append(t[1][i])
                        times[last_seen].append(t[2][i])
                        last_seen += 1
            else:
                for i in [0, -1]: #check first and last dates to check if we've seen them before
                    c_date = t[2][i].date() # current date for analysis
                    if (c_date not in seen_dates):
                        print("new date: {}".format(c_date))
                        seen_dates[c_date] = last_seen
                        last_seen += 1
                # if just looking at a few dates
                for x in t[0]:
                    indoor.append(x)
                for x in t[1]:
                    outdoor.append(x)
                for x in t[2]:
                    times.append(x)

    print(seen_dates)
    if (len(seen_dates) <= 0):
        print("Error: No valid dates")
        exit(-1)

    n_avg = 100
    outdoor_filt = []
    indoor_filt = []
    times_filt = []

    # today = dt.datetime.today().date()

    # Apply moving average filter
    if fold:
        for i in range(len(seen_dates)):
            outdoor_filt.append(np.convolve(np.ones(n_avg)/n_avg, np.array(outdoor[i]), "valid"))
            indoor_filt.append(np.convolve(np.ones(n_avg)/n_avg, np.array(indoor[i]), "valid"))
            times_filt.append([dt.datetime.combine(now.date(), x) for x in times[i][n_avg-1:]])
    else:
        outdoor_filt = np.convolve(np.ones(n_avg)/n_avg, np.array(outdoor), "valid")
        indoor_filt = np.convolve(np.ones(n_avg)/n_avg, np.array(indoor), "valid")
        times_filt = times[n_avg-1:]

    # plot
    plt.figure()
    if (fold):
        n_dates = float(len(seen_dates))+1
        for j, d in enumerate(seen_dates):
            i = seen_dates[d] #dont assume what the mapping is.
            plt.plot(times_filt[i], indoor_filt[i], c = np.array([0,0,0.9])*float(j+1)/n_dates)
            plt.plot(times_filt[i], outdoor_filt[i], c = np.array([0.9, 0, 0])*float(j+1)/n_dates)
    else:
        plt.plot(times_filt, indoor_filt, label="in")
        plt.plot(times_filt, outdoor_filt, label="out") 
        plt.legend(loc=1)


    # print(len(indoor_filt[0]), len(outdoor_filt[0]))
    max_i = max_list(indoor_filt)
    min_i = min_list(indoor_filt)
    max_o = max_list(outdoor_filt)
    min_o = min_list(outdoor_filt)
    mx = np.max([85, max_i+2, max_o+2])
    mn = np.min([55, min_i-2, min_o-2])  
    plt.ylim([mn, mx])

    plt.xlabel("Time")
    plt.xticks(rotation = 20)
    plt.ylabel("Temperature (F)")
    create_folders(history, fold)
    if (history != -1):
        plt.title("Last {} Day(s) Indoor vs. Outdoor Temperatures".format(history))
        plt.savefig(os.getcwd() + "/plots/last_n_days_plots/Last_{}_days_plot_{}".format(history, time.strftime("%Y%m%d-%H%M%S")), dpi=250)
    elif (fold):
        plt.title("All time Indoor vs. Outdoor Temperatures")
        plt.savefig(os.getcwd() + "/plots/folded_plots/folded_all_time_plot_{}".format(time.strftime("%Y%m%d-%H%M%S")), dpi=250)
    else:
        plt.title("All time Indoor vs. Outdoor Temperatures")
        plt.savefig(os.getcwd() + "/plots/all_time_plots/all_time_plot_{}".format(time.strftime("%Y%m%d-%H%M%S")), dpi=250)
        #plt.show()


def create_folders(history, fold):
    if (history != -1):
        try:
            os.mkdir(os.getcwd() + "/plots/last_n_days_plots")
            print("created folder: last_n_days_plots")
        except:
            print("folder exists: last_n_days_plots")
            pass

    elif (fold):
        try:
            os.mkdir(os.getcwd() + "/plots/folded_plots")
            print("created folder: folded_plots")
        except:
            print("folder exists: folded_plots")
            pass
    else:
        try:
            os.mkdir(os.getcwd() + "/plots/all_time_plots")
            print("created folder: all_time_plots")
        except:
            print("folder exists: all_time_plots")
            pass

def min_list(x):
    try:
        return min([min(i) for i in x])
    except:
        return min(x)

def max_list(x):
    try:
        return max([max(i) for i in x])
    except:
        return max(x)

if __name__ == '__main__':
    main()