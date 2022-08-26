"""
Created on Thu Jul 21, 2022

@author: EMMANUEL AF MOMPREMIER
CO-SIMULATION OF H2CAR WITH
    - SLOPE CALCULATOR/GPS TRACES MODEL
    - VEHICLE MODEL
    - ENERGY SOURCE MODEL
    - THROTTLE MODEL
"""



from scipy.signal import savgol_filter
from myFMU import myFMU
from numpy import random
from TrajectoryFileHandler import*
import numpy as np
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt 


## INDICATE NAME OF TXT FILE WITH GPS TRACES
## TXT File obtained from GPSVisualizer
trajectory_file = 'gps_ProvencalENSEM.txt'
trajectory_handler(trajectory_file) #file to be cleansed and slope to be extracted

#
#       CO-SIMULATION
#


#Import all the FMUs from OpenModelica
path1 = 'new_electric.fmu' 
path2 = 'throttle.fmu'


#Duration and timestep of the co-sim
startTime = 0
stop_time = maxTime = 15
time = startTime
step_size = deltaT = 0.1
stepNb=0 #to count each co-sim step

time_list = [] #storing the co-sim time


#Create a Sinusoidal Curve plot to represent the slope 
points = np.linspace(-np.pi, np.pi, int((stop_time/step_size)+1)) #the number of points to be created depend on the step_size
slope_1 = 5 * np.sin(points) #between -5 and 5 by inspection of the slope curve

#Sinusoidal driver acceleration
acceleration_sine = 0.7 * np.sin(points)


#------------- ELECTRIC MODEL: INPUTS(CURRENT DELIVERED); OUTPUTS(VOLTAGE SC, CURRENT SC) -----------------------------------------
electric_model = myFMU(path1)
electric_model.init(startTime, [('current_delivered', 0)])

#Store the results from the co-sim
soc_2 = []
voltage_2 = []
current_sc_2 = []
current_delivered = [] #current delivered to motor 
driver = []


#----------- Throttle: INPUTS (VOLTAGE, DRIVER ACCELERATION); OUTPUTS (THROTTLE, CURRENT SC, CURRENT GIVEN TO MOTOR) --------------
# THIS BOX USES THE RELATION I-V FOR SC GIVEN BY STEPHANE TO OUTPUT A THROTTLE INTENDED TO BE AN INPUT FOR THE 3D SIMULATOR

throttle = myFMU(path2)
throttle.init(startTime, [('driver_pedal', 0.4)])
throttle.init(startTime, [('voltage', 115)])

supercapa_current_delivered = []
supercapa_throttle = []
supercapa_currentsc = []




while time < stop_time:
    
    electric_model.doStep(time, step_size)

     
    #ASSIGN A DRIVER ACCELERATION WITH A STEPWISE FUNCTION   
    if time <= 3:
        driver.append(0)
                
    elif time <= 7:
        driver.append(0.5)
        
    elif time <=  10:
        driver.append(-0.5)
       
    else:
        driver.append(1)
        
    
    #ELECTRIC MODEL

    volt_val_2 = electric_model.get('voltage')      
    voltage_2.append(volt_val_2)
    soc_val_2 = electric_model.get('soc')      
    soc_2.append(soc_val_2)
    current_val_2 = electric_model.get('current_sc')
    current_sc_2.append(current_val_2)
    current_delivered_val = electric_model.get('current_delivered')      
    current_delivered.append(current_delivered_val)
      
    
    throttle.doStep(time, step_size)
    
    
    #throttle
    throttle.set('driver_pedal', driver[stepNb])
    throttle.set('voltage', voltage_2[stepNb]) #voltage_1[stepNb]
    
    supercapa_current_val = throttle.get('current_delivered')  
    supercapa_current_delivered.append(supercapa_current_val) 
    supercapa_throttle_val = throttle.get('throttle')  
    supercapa_throttle.append(supercapa_throttle_val)  
    supercapa_currentsc_val = throttle.get('current_sc')  
    supercapa_currentsc.append(supercapa_currentsc_val)
    
    electric_model.set('current_delivered', supercapa_current_delivered[stepNb]) #takes current_delivered from electric_model as input 
    
    
    time_list.append(time)
    time += step_size
    stepNb += 1
    
    


#SAVE THROTTLE AND DRIVER ACCELERATION IN CSV FILE

df = pd.DataFrame()
df['Time'] = time_list
df['Throttle'] = supercapa_throttle
df['Driver Acc'] = driver
df.to_csv('throttle.txt', header = True, index=False, sep= '\t')



#PLOTS Electric Model

plt.plot(time_list, current_delivered, color='green', label='Current Delivered')
plt.title('Current Delivered to Motor as a function of Time')
plt.xlabel('Time [s]')
plt.ylabel('Current [A]')
plt.legend()
plt.show()

plt.plot(time_list, soc_2, color='blue', label='SOC of SC')
plt.title('SOC of SC as a function of Time')
plt.xlabel('Time [s]')
plt.ylabel('SOC [%]')
plt.legend()
plt.show()

plt.plot(time_list, voltage_2, color='gray', label='Voltage of SC')
plt.title('Voltage of SC as a function of Time')
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')
plt.legend()
plt.show()

plt.plot(time_list, current_sc_2, color='orange', label = 'Current of SC')
plt.title('Current of SC as a function of Time')
plt.xlabel('Voltage [V]')
plt.ylabel('Current [A]')
plt.show()

plt.plot(time_list, driver, color='red', label='Driver Acceleration')
plt.title('Driver Acceleration as a function of Time')
plt.xlabel('Time [s]')
plt.ylabel('Acceleration')
plt.legend()
plt.show()




#PLOTS Throttle

plt.plot(time_list, supercapa_throttle, color='orange', label='Throttle')
plt.title('Throttle Sent to Motor as a function of Time')
plt.xlabel('Time [s]')
plt.ylabel('Throttle')
plt.legend()
plt.show()

plt.plot(time_list, supercapa_throttle, color='orange', label='Throttle')
plt.plot(time_list, driver, color='grey', label='Driver Acceleration')
plt.title('Throttle & Driver Acceleration as a function of Time')
plt.xlabel('Time [s]')
plt.ylabel('Throttle & Driver Acceleration')
plt.legend()
plt.show()

plt.plot(time_list, supercapa_currentsc, color='orange', label='Current sent by throttle')
plt.title('Current from SC as a function of Time')
plt.xlabel('Time [s]')
plt.ylabel('Current [A]')
plt.legend()
plt.show()

