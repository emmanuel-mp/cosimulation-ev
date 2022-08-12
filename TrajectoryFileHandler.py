
"""
Created on Tue Jul 19 2022
@author: EMMANUEL ANIOS FILS MOMPREMIER
OBJECTIVE: HANDLE TXT FILE CONTAINING VEHICLE'S TRAJECTORY DATA
"""



import numpy as np
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
import math
from scipy.signal import savgol_filter



##'gps_Monteebrabois.txt'


delta_height = [] #contains the difference of heights between 2 consecutive data points
delta_distance = [] #contains the difference of distances between 2 consecutive data points
total_distance = [] #increments of the distance as to find the total distance between points A & B
#slope_filtered = []

#

def trajectory_handler(trajectory_file): #the trajectory_file is passed when fct called during co-sim

    """
    The function "trajectory_handler" is called by the co-simulation master file
    with the txt file as an argument.
    
    The function cleanses the txt file downloaded from the internet
    and performs calculations such as difference of altitude between 2 consecutive data points,
    distance between the 2 points and the slope between these points.
    
    The slope is then transferred to the co-sim master file to feed other subsystems. 
    """


    with open(trajectory_file, 'r') as file_in:
        lines = file_in.readlines()
        arrival = lines[2]
        file_in.seek(0)
        #file_in.truncate()
        
        
    with open('gps_ProvencalENSEM_new.txt', 'w+') as file_out:
      
        for index, content in enumerate(lines):
            
    #rewrite all the content of the input file to a new txt file
    #while deleting all the blank lines and unnecessary data imported
    #can do that because downloaded file comes in a standard format  
    
            if index not in [0, 2, 3, 4] : 
                file_out.write(content)
        file_out.write(arrival)
                
    #rewrite the data in a new file and in a new format that facilitates the subsequent computations  
    f = open('gps_ProvencalENSEM_new.txt', 'r')
    g = open('gps_ProvencalENSEM_new_new.txt', 'w')
             
    for line in f:
        if line.strip():
            g.write('\t'.join(line.split()[1:4]) + '\n')
                                 
    f.close()
    g.close()
        
    
    
    
    """
    #STEPS UNDERTOOK IN THE FOLLOWING SECTION
    
    ## 1. FIND DISTANCE BETWEEN 2 POINTS IN THE GPS TRACES
    ## FORMULA FROM H. BARBILLON P.15
    ## Dab = SQRT[(LATb - LATa)^2 + (LONb - LONa)^2]
    
    ## 2. FIND DISTANCE BETWEEN 2 ALTITUTES IN THE GPS TRACES
    ## ALTITUDE b - ALTITUDE a
    
    ## 3. CALCULATE SLOPE ALPHA = ATAN(DELTA height / DELTA distance)
    
    """
    
    
    latitude = []
    longitude = []
    elevation = []
    total_distance.insert(0, 0) #create 1st point = 0
    total_dist = 0
    
    slope_radians = []
    slope_degrees = []
    
    #import file with formatted data to extract each column and perform computations
    myFile = open('gps_ProvencalENSEM_new_new.txt', 'r')
    for y in myFile:
        lat_val = y.split()[0] #latitude column
        long_val = y.split()[1] #longitude column
        elev_val = y.split()[2] #elevation column
        
        latitude.append(float(lat_val))
        longitude.append(float(long_val))
        elevation.append(float(elev_val))
        
    myFile.close()
    
   
    def distance(lat1, lat2, lon1, lon2):
        # Computation of the distances between 2 points using the Haversine formula  
        #Calculate the great circle distance in kilometers between two points 
        #on the earth (specified in decimal degrees)
        
        #Doc: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
        #Doc: https://www.movable-type.co.uk/scripts/latlong.html
        
    	#Converts from degrees to radians.
    	lon1 = math.radians(lon1)
    	lon2 = math.radians(lon2)
    	lat1 = math.radians(lat1)
    	lat2 = math.radians(lat2)
    	
    	# Haversine formula
    	dlon = lon2 - lon1
    	dlat = lat2 - lat1
    	a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    
    	c = 2 * math.asin(math.sqrt(a))
    	
    	# Radius of earth in kilometers. Use 3956 for miles
    	r = 6371
    	
    	# calculate the result
    	return(c * r)
    	
    
    
    
    for i, j, k in zip(range(len(latitude) - 1), range(len(longitude) - 1), range(len(elevation) - 1)): #-1 to account for the lack of ultimate data point 
        total_dist +=  distance(latitude[i], latitude[i+1], longitude[j], longitude[j+1]) #Use Haversine formula to calculate the distance
        total_distance.append(total_dist*1000) #Convert from km to m
        
    for i, j in zip(range(len(total_distance) -1), range(len(elevation) - 1)):
        #Compute the gradients of distance, elevation thus find slope
        dist = (total_distance[i+1] - total_distance[i])
        delta_distance.append(dist)
        
        elev = (elevation[j+1] - elevation[j])
        delta_height.append(elev)
        
        
        #To avoid zerodivision error
        if dist != 0:
            slope = math.atan(elev/dist)          
        else:
            slope = math.pi/2 #Arctan Limit close to +∞	
            

        slope_radians.append(slope) #slope in radians
        
        slope_deg = math.degrees(slope) #slope in degrees
        slope_degrees.append(slope_deg)
  
    
    #Store all the computation results in a new txt file that can be used later on  
    df = pd.DataFrame()
     
    delta_distance.insert(0, 0.01)
    delta_height.insert(0, 0)
    slope_radians.insert(0, 0)
    slope_degrees.insert(0, 0)
    #slope_filtered.insert(0, 0)
       
    #Reformatting the results to have datapoints with two decimals floating points
    #This step is not critical and can be discarded
    #It helps to have a more uniform and "good-looking" txt file
    latitude = ["%.2f" % member for member in latitude]
    longitude = ["%.2f" % member for member in longitude]
    elevation_formatted = ["%.2f" % member for member in elevation]
    
    total_distance_formatted = ["%.2f" % member for member in total_distance]
    slope_degrees_formatted = ["%.2f" % member for member in slope_degrees]
    slope_radians = ["%.2f" % member for member in slope_radians]
    delta_distance_formatted = ["%.2f" % member for member in delta_distance]
    delta_height_formatted = ["%.2f" % member for member in delta_height]
    
    #Attaching the formatted results to the txt file    
    df['Delta h (m)'] = delta_height_formatted
    df['Delta d (m)'] = delta_distance_formatted
    df['Slope (radians)'] = slope_radians
    df['Slope (degrees)'] = slope_degrees_formatted
    
    #Apply a filter to the slope to avoid the sharp variations
    """
    DOCUMENTATION FOR APPLYING a Savitzky-Golay filter to an array
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html
    """
    slope_filtered = savgol_filter(slope_degrees, 51, 3) # window size 51, polynomial order 3
  
    
    slope_filtered.tolist()
    #print(slope_filtered)

   
    #Creation of the new txt file
    df.to_csv('gps_data_formatted.txt', header = True, index=False, sep= '\t')
    
        
    # total_distance.pop(-1)
    # elevation.pop(-1)
    # slope_degrees.pop(-1) 
    
    
    print('Number of data points in GPS file: ', len(latitude)) #to know how many points were obtained from the online GPS tool
    
    #style of the plots
    sns.set_theme(style="darkgrid") #whitegrid #dark #ticks
    #colors doc: https://matplotlib.org/stable/gallery/color/named_colors.html

    #Plots
    plt.plot(total_distance, elevation, color='goldenrod')
    plt.title('Altitude as a function of Position of Vehicle')
    plt.xlabel('Position of Vehicle [m]')
    plt.ylabel('Road Altitude [m]')
    plt.show()
    
    plt.plot(total_distance, slope_degrees, color='lightgreen', label = 'Slope with Noise')
    plt.plot(total_distance, slope_filtered, color='lightslategray', label = 'Filtered Slope')
    plt.title('Slope as a function of Position of Vehicle')
    plt.xlabel('Position of Vehicle [m]')
    plt.ylabel('Slope [deg]')
    plt.legend()
    plt.show()
    
    return slope_filtered
    
    
    
              


