from datetime import datetime
import time, datetime as dt, pandas as pd, serial, matplotlib.pyplot as plt, numpy as np
from Arduino import Arduino

class controller:
    def __init__(self, serial_port="/dev/ttyACM0", baud_rate=9600): 
        self.serial_port = serial_port
        self.baud = baud_rate
        self.serial_connection = self.attempt_connection()
        self.data = self.__create_df()
        self.fig, self.ax = self.__create_plot()

    def create_serial_connection(self):
        try:
            serial_connection = serial.Serial(self.serial_port, self.baud)
            return serial_connection
        except Exception as e:
            print(e)
            return False

    def attempt_connection(self):
        serial_connection = None
        first = True
        while not serial_connection:
            serial_connection = self.create_serial_connection()
            if not first:
                time.sleep(5)
            first = False
        print("Connection successful.")
        return serial_connection

    def __get_line(self):
        line = self.serial_connection.readline().decode("utf-8")
        return line

    """
    def link_board(serial_port="/dev/ttyACM0", baud_rate="115200"):
        board = Arduino(baud_rate, serial_port)
        return board
    """

    def append_to_df(self):
        line = self.__get_line()
        def create_dict():
            var_list = line.split(",")
            datum = [float(i) for i in var_list]
            time_str = dt.datetime.now()
            datum = [time_str] + datum
            return {"DATETIME": datum[0], "HUMIDITY": datum[1], "TEMPERATURE": datum[2],
            "HEAT_INDEX": datum[3], "RELAY_STATUS": int(datum[4]), "TIMESTAMP": datum[0].timestamp()}
        try:
            series = [create_dict()]
            self.data = pd.concat([self.data, pd.DataFrame(series)], ignore_index=True)
            if self.data.shape[0] == 1:
                self.data.DATETIME = pd.to_datetime(self.data.DATETIME)
        except Exception as e:
            print(e)


    def __create_df(self):
        return pd.DataFrame(columns=["DATETIME", "HUMIDITY", "TEMPERATURE", "HEAT_INDEX", "RELAY_STATUS", "TIMESTAMP"])

    def __create_plot(self):
        plt.ion()
        fig = plt.figure(figsize=(13.66, 6.65), dpi=150)
        ax = fig.subplots(2, 1)
        return (fig, ax)
    
    def last_ms_axis(self, minutes):
        higher_time_limit = dt.datetime.now() + dt.timedelta(seconds=5)
        lower_time_limit = higher_time_limit + dt.timedelta(minutes=-minutes)
        lower_minute = dt.datetime(lower_time_limit.year, lower_time_limit.month, lower_time_limit.day,
        lower_time_limit.hour, lower_time_limit.minute) + dt.timedelta(minutes=1)
        xticks = [lower_minute]
        while xticks[-1] <= higher_time_limit + dt.timedelta(minutes=-1):
            xticks.append(xticks[-1] + dt.timedelta(minutes=1))
        xlabels = [i.strftime("%H:%M") for i in xticks]
        xticks = [i.timestamp() for  i in xticks]
        xlims = [lower_time_limit.timestamp(), higher_time_limit.timestamp()]
        return (xticks, xlabels, xlims)
    
    def plot_last_ms(self, data_subset, minutes):
        self.last_ms_line, = self.ax[0].plot(data_subset.TIMESTAMP, data_subset.TEMPERATURE, color="#ff0000")
        self.ax[0].grid(axis="y")
        xticks, xlabels, xlims = self.last_ms_axis(minutes)
        self.ax[0].set_xlim(xlims)
        self.ax[0].set_xticks(xticks)
        self.ax[0].set_xticklabels(xlabels)
        self.ax[0].set_ylim(23, 33)
        self.ax[0].set_yticks([i for i in range(23, 34)])

    def refresh_last_ms(self, minutes=8, collection_freq=5):
        data_subset = self.subset_ms(minutes, collection_freq)
        if not hasattr(self, "last_ms_line"):
            self.plot_last_ms(data_subset, minutes)
        self.last_ms_line.set_ydata(data_subset.TEMPERATURE)
        self.last_ms_line.set_xdata(data_subset.TIMESTAMP)
        xticks, xlabels, xlims = self.last_ms_axis(minutes)
        self.ax[0].set_xlim(xlims)
        self.ax[0].set_xticks(xticks)
        self.ax[0].set_xticklabels(xlabels)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def subset_ms(self, minutes, collection_freq):
        collection_min = 60 / collection_freq
        number_of_data = int(minutes * collection_min)
        data_subset = self.data.tail(number_of_data)
        return data_subset
    
    def subset_hs(self, hours=24):
        now = dt.datetime.now()
        if now.minute >= 8:
            yesterdays_next_hour = dt.datetime(now.year, now.month, now.day - 1, now.hour) + dt.timedelta(hour=1)
        else:
            yesterdays_next_hour = dt.datetime(now.year, now.month, now.day -1, now.hour)
        data_subset = self.data[self.data.DATETIME >= yesterdays_next_hour]
        return data_subset
    
    def plot_last_hs(self):
        data_subset = self.subset_hs()
        self.last_hs_box, = self.ax[1]