# User Interface for DigiNose - by Leo Biljesko

# Can select start measurement from file at the top left, PCB must be connected to the PC via USB cable.
# User must type in name of a file and then plug in power to PCB, press Start measurement immediately after.
# When measurement is done, press Stop measurement. Data will be stored in the CSV file in file directory where code is.
# To import data select file that is created by New measurement and it will plot sensor resitance.
# For PCA, select same file as for import data and PCA will be done.
# When it comes to LDA, it needs more preprocessing. Before you must know how much data you have and names of labels.
# Example: 15 CSV files for ethanol, 10 CSV files for d-limonene. and write them down in code. Disadvantage of LDA.
# Store all data in one folder (e.g. all substances), press Select folder
# and code will take last row of each CSV file and store it to new file, then it will clean unneccessary data.
# Then write in test size for training (e.g. 20 will use 80% of data for training and 20% for testing).
# After this LDA is plotted. 
# 

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
from matplotlib.animation import FuncAnimation
from sklearn.decomposition import IncrementalPCA, PCA
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from tkinter import filedialog
from PIL import Image
import seaborn as sns
from tkinter import *
import pandas as pd
import numpy as np
import serial
import os
import csv

sns.set(style="whitegrid") # Use seaboarn matplotlib style

# Window settings
root = Tk()
root.title("DigiNose")
root.configure(background='white')
#icon = PhotoImage(file='FH.gif')
#root.iconphoto(True, icon)
root.state('zoomed')

# Initial values for data
time_data=[]
temperature_data=[]
humidity_data=[]
sensors=[]
anim = None

save_fig=False

def measurement_start():  # Reading live data
     
     def serial_connection(): # Connect to arduino
          global file_name, ser

          # Serial connection
          ser = serial.Serial('COM3', baudrate=9600, timeout=1)  # Connect arduino to python via serial communication, have to select COM port

          # Set file name
          file_name = f"{create_file.get()}.csv" # Creates file in which data is written 

          # Clear file if data inside
          f = open(file_name, "w+")
          f.close()

          # Open file
          # logging = open(file_name, mode='a', newline='')

     # Function to write data to csv file
     def write_to_csv(df):

          # header_names=['Time','CO2','TVOC','Temperature','Humidity','MQ3','MQ135','GGS1330','GGS2330','GGS10330','TGS2600','TGS822' ]
          df.to_csv(file_name, mode='a', header=False, index=False)
          read_data()

     # Read data from arduino and split it into columns
     def generate_data():

          while True: # Write message if there is problem in connection of ENS160/BME280 sensor
               line = ser.readline().decode('utf-8').strip()

               if "failed to init chip, please check the chip connection" in line:  # Upload arduino then turn on supply
                    print("Please check the chip connection!")

               elif line:
                    splitted_line = line.split(',')  # Splits string
                    df = pd.DataFrame([splitted_line])  # Creates dataframe type
                    write_to_csv(df)  # Writes data to csv file in columns
                    
               yield

     # Updates data each frame
     def update_plot(frame):
          next(generate_data())  # Each frame update
     
     
     def read_data():
          # Reading data 
          
          data_python = pd.read_csv(file_name, header=None)
        
          # Extracting data
          time_data = data_python.iloc[:, 0]
          co2=data_python.iloc[:,1]
          tvoc=data_python.iloc[:,2]
          temp = data_python.iloc[:, 4]
          humidity = data_python.iloc[:, 3]
          sensors=data_python.iloc[:, 5:12]
          
          # Scaling Data
          scaled_data = StandardScaler().fit_transform(sensors)
         
          MQ3=scaled_data[:, 0]
          MQ135=scaled_data[:,1]
          GGS1330=scaled_data[:,2]
          GGS2330=scaled_data[:, 3]
          GGS10330=scaled_data[:, 4]
          TGS2600 =scaled_data[:, 5]
          TGS822=scaled_data[:, 6]

          # Plots data on ax1
          ax1.clear()
          ax1.plot(time_data / 60, MQ3,color='#0072BD',linewidth=2, label="MQ3")
          ax1.plot(time_data / 60, MQ135,color='#D95319',linewidth=2, label="MQ135")
          ax1.plot(time_data / 60, GGS1330,color='#EDB120',linewidth=2, label="GGS1330")
          ax1.plot(time_data / 60, GGS2330,color='#FF00FF',linewidth=2, label="GGS2330")
          ax1.plot(time_data / 60, GGS10330,color='#77AC30',linewidth=2, label="GGS10330")
          ax1.plot(time_data / 60, TGS2600,color='#4DBEEE',linewidth=2, label="TGS2600")
          ax1.plot(time_data / 60, TGS822,color='pink',linewidth=2, label="TGS822")
          
          # Customization
          ax1.set_xlabel('Time [min]')
          ax1.set_ylabel('Normalized Resistance')
          ax1.set_title('Sensor Resistance')
          ax1.legend(loc='upper left', bbox_to_anchor=(0.9, 1), labelcolor=['#0072BD','#D95319','#EDB120','#FF00FF','#77AC30','#4DBEEE','pink'])
          ax1.grid(True)
          
          
          # Plotting temperature and humidity
          ax2.clear()
          ax2.plot(time_data / 60, temp,color='#D95318',linewidth=2, label="Temperature[°C]")
          ax2.plot(time_data / 60, humidity,color='#0072BD',linewidth=2, label="Humidity[%]")
          ax2.set_xlabel('Time [min]')
          ax2.set_ylabel('Temperature & Humidity')
          ax2.set_title('Temperature and Humidity')
          ax2.legend(loc='upper left', bbox_to_anchor=(0.9, 1), labelcolor=['#D95319', '#0072BD'])
          ax2.grid(True)

          # Air quality
          aq_label.config(text="")
          CO2=co2.iloc[-1] # Taking only the last value
          TVOC=tvoc.iloc[-1]
          aq_label.config(text=f"CO2: {CO2} ppm  TVOC: {TVOC} ppb")

     def run_real_time():

          global fig_1, fig_2,ax2, ax1, anim1,anim2

          serial_connection()

          # Running animation so we can see in real time


          # Sensor resistance data
          fig_1 = Figure(figsize=(12, 5), dpi=85, edgecolor='black')
          ax1= fig_1.add_subplot(1, 1, 1)

          ax1.set_title('Sensor Resistance')
          ax1.set_xlabel('Time[min]')
          ax1.set_ylabel('Normalized Resistance')

          canvas = FigureCanvasTkAgg(fig_1, master=root)  # Get current figure
          canvas.draw()
          canvas.get_tk_widget().grid(row=2, column=0, padx=0)

          toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
          toolbar.update()
          toolbar.grid(row=3, column=0)
          
          anim1 = FuncAnimation(fig_1, update_plot, interval=3000, save_count=1000)

          # Temperature & Humidity Plot
          fig_2 = Figure(figsize=(12, 5), dpi=85, edgecolor='black')
          ax2 = fig_2.add_subplot(1, 1, 1)

          ax2.set_title('Temperature & Humidity')
          ax2.set_xlabel(f'Time[min]')
          
          canvas = FigureCanvasTkAgg(fig_2, master=root)  # Get current figure
          canvas.draw()
          canvas.get_tk_widget().grid(row=4, column=0, padx=0)

          toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
          toolbar.update()
          toolbar.grid(row=5, column=0)
          
          anim2 = FuncAnimation(fig_2, update_plot, interval=3000, save_count=1000)

     # To be able to close window, for some reason animation dont allow it
     root.protocol("WM_DELETE_WINDOW", on_close)

     if __name__ == "__main__":
          run_real_time()
     
# If user wants to stop plotting or discard measurements
def measurement_stop(): 
     if anim1:
          anim1.event_source.stop() # Stops animation
          anim2.event_source.stop()
          ser.close()    # Stops serial communication

def on_close(event=None):
          anim1.event_source.stop()
          root.destroy()
          ser.close()

# Function to import data
def import_file():
     
     global file_names, HandT, time_data, temperature_data, humidity_data, sensor_data

     file_names=" "

     # Open file dialog
     file_paths = filedialog.askopenfilenames(initialdir="C:/Users", title="Select Files", filetypes=(("CSV files", "*.csv"),)) # Open file dialog
     file_names = [os.path.basename(file) for file in file_paths] # Get the name of files that are selected
     
     show_file_name(file_names) # Print out selected file names
     
     # Reading in data from csv 
     HandT = pd.read_csv(str(file_names[0]), delimiter=',')
     
     # Reading out data
     time_data=HandT.iloc[:, 0]
     temperature_data=HandT.iloc[:, 4]
     humidity_data=HandT.iloc[:, 3]
     sensor_data = HandT.iloc[:, 5:12]
     co2=HandT.iloc[:,1]
     tvoc=HandT.iloc[:,2]
     
     CO2=co2.iloc[-1]
     TVOC=tvoc.iloc[-1]
     aq_label.config(text=f"CO2: {CO2}  TVOC: {TVOC}")

     # Button to plot data
     plot_button = Button(root, text="Plot data", font=("Helvetica", 12),command=lambda: resistance_plot( time_data,temperature_data,humidity_data,sensor_data))
     plot_button.grid(row=0,column=3, padx=10,pady=10)

def import_file_PCA():
     
     global file_names, HandT, time_data, temperature_data, humidity_data, sensor_data
     file_names=" "

     # Open file dialog
     file_paths = filedialog.askopenfilenames(initialdir="C:/Users", title="Select Files", filetypes=(("CSV files", "*.csv"),)) # Open file dialog
     file_names = [os.path.basename(file) for file in file_paths] # Get the name of files that are selected
     
     show_file_name(file_names) # Print out selected file names
     
     # Reading in data from csv 
     HandT = pd.read_csv(str(file_names[0]), delimiter=',')
     
     # Reading out data
     time_data=HandT.iloc[:, 0]
     temperature_data=HandT.iloc[:, 4]
     humidity_data=HandT.iloc[:, 3]
     sensor_data = HandT.iloc[:, 5:12]
     co2=HandT.iloc[:,1]
     tvoc=HandT.iloc[:,2]
     
     CO2=co2.iloc[-1]
     TVOC=tvoc.iloc[-1]
     aq_label.config(text=f"CO2: {CO2}  TVOC: {TVOC}")

     # Button to plot data
     plot_button = Button(root, text="Plot data", font=("Helvetica", 12),command=lambda: pca_analysis( time_data,temperature_data,humidity_data,sensor_data))
     plot_button.grid(row=0,column=3, padx=10,pady=10)

# Show file name function
def show_file_name(file_names):
     global file_label_name
     
     # File name label
     file_label_name = Label(root, text=", ".join(file_names), font=("Helvetica", 12), background='white')
     file_label_name.grid(row=0, column=6)  # Display label in the root window

# Function to clear plots
def clear_data():
    
    global file_names, file_label_name
    file_label_name=" "
    file_names=" "
    initial_figures() 

# Save figure function
def figure_save(name1,name2):
     
     # Open dialog and save figure and then open again to save second figure
     save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")]) 
     if save_path:
          name1.savefig(save_path)
          save_fig=True
     if save_fig:
          save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")]) 
          name2.savefig(save_path)
          save_fig=False
     
def resistance_plot(time_data,temperature_data,humidity_data,sensor_data):
     global fig_1, fig_2
     plt.close()

     # Scaling data
     scaled_data = StandardScaler().fit_transform(sensor_data)
         
     MQ3=scaled_data[:, 0]
     MQ135=scaled_data[:,1]
     GGS1330=scaled_data[:,2]
     GGS2330=scaled_data[:, 3]
     GGS10330=scaled_data[:, 4]
     TGS2600 =scaled_data[:, 5]
     TGS822=scaled_data[:, 6]

     time_data_min=time_data/60

     # PCA Plot
     fig_1=plt.figure(figsize=(12, 5), dpi=85,edgecolor='black') # Creates a figure
     
     plt.plot(time_data / 60, MQ3,color='#0072BD',linewidth=2, label="MQ3")
     plt.plot(time_data / 60, MQ135,color='#D95319',linewidth=2, label="MQ135")
     plt.plot(time_data / 60, GGS1330,color='#EDB120',linewidth=2, label="GGS1330")
     plt.plot(time_data / 60, GGS2330,color='#FF00FF',linewidth=2, label="GGS2330")
     plt.plot(time_data / 60, GGS10330,color='#77AC30',linewidth=2, label="GGS10330")
     plt.plot(time_data / 60, TGS2600,color='#4DBEEE',linewidth=2, label="TGS2600")
     plt.plot(time_data / 60, TGS822,color='pink',linewidth=2, label="TGS822")
          
     canvas = FigureCanvasTkAgg(fig_1, master=root) # gcf - get current figure
     canvas.draw()
     canvas.get_tk_widget().grid(row=2,column=0, padx=0)

     toolbar=NavigationToolbar2Tk(canvas, root, pack_toolbar=False)  # Adds a toolbar
     toolbar.update()
     toolbar.grid(row=3,column=0)

     plt.xlabel('Time [min]')
     plt.ylabel('Normalized Resistance')
     plt.title('Sensor Resistance')
     plt.legend(loc='upper left', bbox_to_anchor=(0.9, 1), labelcolor=['#0072BD','#D95319','#EDB120','#FF00FF','#77AC30','#4DBEEE','pink'])
     plt.grid(True)

     # Temperature and humidity over time plot
     fig_2=plt.figure(figsize=(12, 5), dpi=85,edgecolor='black')
     plt.plot(time_data_min,temperature_data,color='#D95319', label="Temperature[°C]",linewidth=2) # Temperature
     plt.plot(time_data_min,humidity_data,color='#0072BD', label="Humidity[%]",linewidth=2) # Plots the data
     plt.legend(loc='upper right',bbox_to_anchor= (1.1, 1), labelcolor=['#D95319', '#0072BD'])

     canvas = FigureCanvasTkAgg(fig_2, master=root) # gcf - get current figure
     canvas.draw()
     canvas.get_tk_widget().grid(row=4,column=0, padx=0)

     toolbar=NavigationToolbar2Tk(canvas, root, pack_toolbar=False)  
     toolbar.update()
     toolbar.grid(row=5, column=0)
   
# PCA analysis function
def pca_analysis(time_data,temperature_data,humidity_data,sensor_data):

     global fig_1, fig_2
     plt.close()

     # Scaling data for PCA
     scaled_data = StandardScaler().fit_transform(sensor_data)

     # Perform PCA
     pca = IncrementalPCA(n_components=2,batch_size=100)
     pca.fit(scaled_data)
     pca_data = pca.transform(scaled_data)

     # Calculate explained variance ratio
     per_var = np.round(pca.explained_variance_ratio_ * 100, decimals=1)
     labels = [f'PC{x}' for x in range(1, len(per_var) + 1)]

     pca_df = pd.DataFrame(pca_data, columns=labels)
     feature_names = ["MQ3", "MQ135", "S1330", "S2330", "S10330", "TGS2600", "TGS822"]
     time_data_min=time_data/60

     # PCA Plot
     fig_1=plt.figure(figsize=(12, 5), dpi=85,edgecolor='black') # Creates a figure

     for i in range(len(time_data_min)): # Usually measurement is done for 15min air and 40min tree, so the difference can be seen use different colors
          if time_data_min[i] <15:
               plt.scatter(pca_df.PC1[i],pca_df.PC2[i],color="#D95319") # Plots the data
          else:
               plt.scatter(pca_df.PC1[i],pca_df.PC2[i],color="#0072BD") # Plots the data
   
     canvas = FigureCanvasTkAgg(fig_1, master=root) # gcf - get current figure
     canvas.draw()
     canvas.get_tk_widget().grid(row=2,column=0, padx=0)

     toolbar=NavigationToolbar2Tk(canvas, root, pack_toolbar=False)  # Adds a toolbar
     toolbar.update()
     toolbar.grid(row=3,column=0)

     plt.title('PCA Graph')
     plt.xlabel(f'PC1 - {per_var[0]}%')
     plt.ylabel(f'PC2 - {per_var[1]}%')
     legend=plt.legend(("Initialization","Measurement"),loc='upper left', bbox_to_anchor=(0.9, 1), labelcolor=['#D95319', '#0072BD'])
     legend.legend_handles[0].set_color("#D95319")  
     legend.legend_handles[1].set_color("#0072BD")  

     # Temperature and humidity over time plot
     fig_2=plt.figure(figsize=(12, 5), dpi=85,edgecolor='black')
     plt.plot(time_data_min,temperature_data,color='#D95319', label="Temperature[°C]",linewidth=2) # Temperature
     plt.plot(time_data_min,humidity_data,color='#0072BD', label="Humidity[%]",linewidth=2) # Plots the data
     plt.legend(loc='upper right',bbox_to_anchor= (1.1, 1), labelcolor=['#D95319', '#0072BD'])

     canvas = FigureCanvasTkAgg(fig_2, master=root) # gcf - get current figure
     canvas.draw()
     canvas.get_tk_widget().grid(row=4,column=0, padx=0)

     toolbar=NavigationToolbar2Tk(canvas, root, pack_toolbar=False)  
     toolbar.update()
     toolbar.grid(row=5, column=0)
     

def initial_figures():
         
    global fig_1, fig_2 ,file_names
    plt.close()

    # Initial figures

    # Sensor resistance
    fig_1=plt.figure(figsize=(12, 5), dpi=85,edgecolor='black') # Creates a figure
    plt.scatter([],[]) # Plots the data

    canvas = FigureCanvasTkAgg(fig_1, master=root) # gcf - get current figure
    canvas.draw()
    canvas.get_tk_widget().grid(row=2,column=0, padx=0)

    plt.title('Sensor Resistance')
    plt.xlabel('Time[min]')
    plt.ylabel('Normalized Resistance')

    # Temperature and humidity over time
    fig_2=plt.figure(figsize=(12, 5), dpi=85,edgecolor='black')
    plt.plot([],[],color="#D95319", label="Temperature[°C]") # Temperature
    plt.plot([],[],color="#0072BD", label="Humidity[%]") # Plots the data

    canvas = FigureCanvasTkAgg(fig_2, master=root) # gcf - get current figure
    canvas.draw()
    canvas.get_tk_widget().grid(row=4,column=0, padx=0)

    plt.title("Temperature & Humidity")
    plt.xlabel("Time[min]")
    plt.legend(loc='upper right',bbox_to_anchor= (1.1, 1), labelcolor=['#D95319', '#0072BD'])

# Buttons used in measurement mode
def show_measurement_buttons():

     global create_file,aq_label

     # Destroys all widgets on the window so they dont interact with previous ones
     for widget in root.winfo_children():
          if isinstance(widget, (Button,Label,Entry,Frame)):
            widget.destroy()

     # Stops measurement
     stop_measurement = Button(root, text="Stop measurement", font=("Helvetica", 12), command = measurement_stop)
     stop_measurement.grid(row=0,column=3,padx=10,pady=10)

     # Clear plots
     clear_button=Button(root, text="Clear plots", font=("Helvetica", 12), command =clear_data)
     clear_button.grid(row=0,column=4,padx=10,pady=10)

     # Air quality
     aq_label=Label(root, text="CO2:         TVOC:       ", font=("Helvetica", 12), background='white',width=30)
     aq_label.grid(row=1, column=2,padx=10,pady=10)

     # File name create label
     create_file_label=Label(root,text="Measurement name: ",font=("Helvetica", 12), background='white')
     create_file_label.grid(row=1,column=3,padx=10,pady=10)

     # This just makes sure user has typed in file name 
     def check_file_name(event=None):
      if create_file.get().strip() != "":
        start_measurement.config(state=NORMAL)
      else:
        start_measurement.config(state=DISABLED)

     create_file = Entry(root, width=20, fg='grey', font=("Helvetica", 12), background='white')
     create_file.grid(row=1, column=4, pady=10)
     create_file.insert(0, "Enter file name...")
     create_file.bind("<FocusIn>", lambda event: create_file.delete(0, "end"))
     create_file.bind("<FocusOut>", lambda event: check_file_name())
     create_file.bind("<KeyRelease>", check_file_name)  # Bind to any key release event

     # Start measurement button
     start_measurement = Button(root, text="Start measurement", font=("Helvetica", 12), state=DISABLED, command=measurement_start)
     start_measurement.grid(row=0, column=2, padx=0)

     section_label=Label(root, text="New Measurement", font=("Helvetica", 16), background='white')
     section_label.grid(row=0,column=0,padx=10)

# Buttons ised in import mode
def show_import_buttons():

     global aq_label

     # Destroys all widgets
     for widget in root.winfo_children():
        if isinstance(widget, (Button,Label,Entry,Frame)):
            widget.destroy()

     # Plot button
     plot_button = Button(root, text="Plot data", font=("Helvetica", 12),state=DISABLED)
     plot_button.grid(row=0,column=3,padx=10,pady=10)

     # Clear button
     clear_button=Button(root, text="Clear plots", font=("Helvetica", 12), command =clear_data)
     clear_button.grid(row=0,column=4,padx=10,pady=10)

     # Import file button
     import_button=Button(root, text="Import file", font=("Helvetica", 12), command =import_file)
     import_button.grid(row=0,column=2,padx=10,pady=10)
     
     # File label
     file_label=Label(root, text="Imported files: ", font=("Helvetica", 12), background='white')
     file_label.grid(row=0, column=5,pady=10)

     # Air quality button
     aq_label=Label(root, text="CO2:         TVOC:       ", font=("Helvetica", 12), background='white',width=30)
     aq_label.grid(row=1, column=5,padx=10)

     section_label=Label(root, text="Data Import", font=("Helvetica", 16), background='white')
     section_label.grid(row=0,column=0,padx=10)

def show_import_buttons_PCA():

     global aq_label

     # Destroys all widgets
     for widget in root.winfo_children():
        if isinstance(widget, (Button,Label,Entry,Frame)):
            widget.destroy()

     # Plot button
     plot_button = Button(root, text="Plot PCA", font=("Helvetica", 12),state=DISABLED)
     plot_button.grid(row=0,column=3,padx=10,pady=10)

     # Clear button
     clear_button=Button(root, text="Clear plots", font=("Helvetica", 12), command =clear_data)
     clear_button.grid(row=0,column=4,padx=10,pady=10)

     # Import file button
     import_button=Button(root, text="Import file", font=("Helvetica", 12), command =import_file_PCA)
     import_button.grid(row=0,column=2,padx=10,pady=10)
     
     # File label
     file_label=Label(root, text="Imported file: ", font=("Helvetica", 12), background='white')
     file_label.grid(row=0, column=5,pady=10)

     # Air quality button
     aq_label=Label(root, text="CO2:         TVOC:       ", font=("Helvetica", 12), background='white',width=30)
     aq_label.grid(row=1, column=5,padx=10)

     section_label=Label(root, text="PCA Analysis", font=("Helvetica", 16), background='white')
     section_label.grid(row=0,column=0,padx=10)

def select_folder_LDA():
    folder_path = filedialog.askdirectory(title="Select Folder Containing CSV Files")

    # Just add LDA to the end of file
    new_folder_path = folder_path + "LDA"
    os.makedirs(new_folder_path, exist_ok=True)
    
    # Get a list of all CSV files in the specified directory
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    
    # Loop through each CSV file
    for file_name in csv_files:
        # Read the CSV file
        file_path = os.path.join(folder_path, file_name)
        df = pd.read_csv(file_path)
        
        # Remove data from columns 0 to 5 and leave data from columns 5 to 12
        df = df.iloc[:, 5:12]
        
        # Write the modified dataframe to a new CSV file in the new folder
        new_file_path = os.path.join(new_folder_path, file_name)
        df.to_csv(new_file_path, index=False)
       
    
    # Call the function to read the last row of each CSV file and save to Data_for_LDA.csv
    read_LDA_data(new_folder_path)

def read_LDA_data(new_folder_path):
    
    # Get a list of all CSV files in the new folder directory
    plt.close()
    csv_files = [file for file in os.listdir(new_folder_path) if file.endswith('.csv')]

    # Create an empty list to store the results
    result = []

    # Iterate through each CSV file
    for file in csv_files:
        file_path = os.path.join(new_folder_path, file)
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            last_line = None
            for line in reader:
                last_line = line  # Read all data from the last row
            if last_line:
                result.append([''] + last_line)  # Start with an empty column for labels
                

    # Add the labels to the first column
    for i in range(len(result)):
        result[i][0] = csv_files[i]
        
    # Write the results to a new CSV file
    output_file = os.path.join(new_folder_path, 'Data_for_LDA.csv')
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(result)

    test_size_set = Entry(root, width=5, fg='grey', font=("Helvetica", 12), background='white')
    test_size_set.grid(row=1, column=3, pady=0)

    if  output_file:
        plot_button = Button(root, text="Plot LDA", font=("Helvetica", 12),state=NORMAL,command=lambda: LDA_function(output_file,test_size_set.get()))
        plot_button.grid(row=0,column=3,padx=10,pady=10)
        

def LDA_function(csv_file_path,test_size_set):
    
   # Create an empty list to store the CSV data 
    csv_data = []

    # Read the CSV file and store its contents in the list
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            modified_row = row[1:]
            csv_data.append(modified_row)

    # Convert the numerical values to float
    numerical_rows = [[float(value) for value in row] for row in csv_data]

    # Normalize the numerical values using MinMaxScaler
    scaler = MinMaxScaler()
    normalized_rows = scaler.fit_transform(numerical_rows)

    # Labels for LDA, depending on the amount of data we got this will change, also on the number of features we have
    y = [0] * 10 +  [1] * 15 + [2] * 10   + [3] * 15 + [4] * 17 + [5] * 15 + [6] * 10 + [7] * 10 + [8] * 15

    # Splitting data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(normalized_rows, y, test_size=float(test_size_set)/100)

    # Initializing and training the LDA model
    lda = LinearDiscriminantAnalysis()
    lda.fit(X_train, y_train)

    # Transforming the data and plotting the transformed data
    X_train_transformed = lda.transform(X_train)

    labelss = ['3-Carene', 'Air', 'Alpha pinene', 'D-limonene', 'Ethanol', 'EVerbanol', 'Methyl', 'Mixture', 'Verbenol']
    colors = ['g', 'pink', 'b', 'orange', 'm', 'y', 'r', 'k', 'c']
    fig_1 = plt.figure(figsize=(12, 5), dpi=85, edgecolor='black')
    ax1 = fig_1.add_subplot(111)
    for i in range(len(labelss)):
        indices = np.where(np.array(y_train) == i)[0]
        ax1.scatter(X_train_transformed[indices, 0], X_train_transformed[indices, 1], label=labelss[i], color=colors[i])

    canvas = FigureCanvasTkAgg(fig_1, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=2, column=0, padx=0)

    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()
    toolbar.grid(row=3, column=0)

    ax1.set_xlabel('LDA Component 1')
    ax1.set_ylabel('LDA Component 2')
    ax1.set_title('LDA Transformed Data (Training Set)')
    ax1.legend(loc='upper left', bbox_to_anchor=(0.9, 1))

    # Computing the mean accuracy of classification on the training data
    accuracy_train = lda.score(X_train, y_train)
    
    # Applying the trained LDA model to the testing data
    X_test_transformed = lda.transform(X_test)

    # Plotting the transformed data for the testing set
    fig_2 = plt.figure(figsize=(12, 5), dpi=85, edgecolor='black')
    ax2 = fig_2.add_subplot(111)
    for i in range(len(labelss)):
        indices = np.where(np.array(y_test) == i)[0]
        ax2.scatter(X_test_transformed[indices, 0], X_test_transformed[indices, 1], label=labelss[i], color=colors[i])
    
    canvas = FigureCanvasTkAgg(fig_2, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=4, column=0, padx=0)

    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()
    toolbar.grid(row=5, column=0)

    ax2.set_xlabel('LDA Component 1')
    ax2.set_ylabel('LDA Component 2')
    ax2.set_title('LDA Transformed Data (Testing Set)')
    ax2.legend(loc='upper left', bbox_to_anchor=(0.9, 1))

    # Computing the accuracy of classification on the testing data
    accuracy_test = lda.score(X_test, y_test)
    
    training_label.config(text=f"Training accuracy: {round(accuracy_train,2)}  Testing accuracy: {round(accuracy_test,2)}")

def show_import_buttons_LDA():

     global aq_label
     global training_label
     # Destroys all widgets
     for widget in root.winfo_children():
        if isinstance(widget, (Button,Label,Entry,Frame)):
            widget.destroy()

     # Plot button
     plot_button = Button(root, text="Plot LDA", font=("Helvetica", 12),state=DISABLED)
     plot_button.grid(row=0,column=3,padx=10,pady=10)

     # Clear button
     clear_button=Button(root, text="Clear plots", font=("Helvetica", 12), command =clear_data)
     clear_button.grid(row=0,column=4,padx=10,pady=10)

     # Import file button
     select_button=Button(root, text="Select folder", font=("Helvetica", 12), command = select_folder_LDA)
     select_button.grid(row=0,column=2,padx=10,pady=10)
     
     # Air quality button
     training_label=Label(root, text="Training accuracy:       Testing accuracy:       ", font=("Helvetica", 12), background='white',width=40)
     training_label.grid(row=0, column=5,padx=0)

     section_label=Label(root, text="LDA Analysis", font=("Helvetica", 16), background='white')
     section_label.grid(row=0,column=0,padx=10)

     test_size_label=Label(root, text="Test Size [%]:   ", font=("Helvetica", 12), background='white',width=20)
     test_size_label.grid(row=1,column=2,padx=0)

     
def menu_init():
     # Creates menu
     menu_bar = Menu(root)
     root.config(menu=menu_bar)

     # Create a "File" menu
     file_menu = Menu(menu_bar,tearoff=0)
     menu_bar.add_cascade(label="File", menu=file_menu, font=("Helvetica", 12))

     # Add options to the "File" menu
     file_menu.add_command(label="New Measurement",command=show_measurement_buttons,font=("Helvetica", 11))
     file_menu.add_command(label="Import Data", command=show_import_buttons,font=("Helvetica", 11))
     file_menu.add_command(label="PCA Analysis", command=show_import_buttons_PCA,font=("Helvetica", 11))
     file_menu.add_command(label="LDA Analysis", command=show_import_buttons_LDA,font=("Helvetica", 11))
     


menu_init()
initial_figures()
root.mainloop() 