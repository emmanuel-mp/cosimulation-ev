model vehicle

//*** THE MOTION OF THE VEHICLE CAN BE DESCRIBED BY THE FOLLOWING DIFF. EQUATION

  // M*der(v) = force_traction - [force_drag + force_rolling_resistance +- grade_resistance (due to slope)]
  // OR, GIVEN FORCE_TRACTION BY MOTOR THROUGH POWER DELIVERED, CAN FIND SPEED OF THE vehicle
  // POWER DELIVERED = SUM OF RESISTIVE FORCES ON VEHICLE * SPEED 
  
  // REFERENCE FOR EQUATIONS: https://www.fs.isy.liu.se/Edu/Courses/TSFS02/Lectures/lecture2.pdf
  // BOOK: THEORY OF GROUND VEHICLE http://160592857366.free.fr/joe/ebooks/Automative%20engineering%20books/Theory_of_ground_vehicles.pdf
  
  // car considered: Toyota Corolla 1300 DX (data provided in the book) + https://www.carfolio.com/toyota-corolla-1300-dx-262911

//***


input Real slope;
input Real power_source;



output Real speed_car (start = 1);
output Real acceleration (start = 0); //(start = 0);

Real Fd; //Force Drag
Real Fr; //Force Rolling Resistance
Real Fg; //Grade Resistance due to slope (+ uphill, - downhill)
Real W; //weight of the car

Real dT = 10;

parameter Real Mass_car = 930; //kg; kerb weight of the car: weight without occupants or baggage
parameter Real g = 9.81;
parameter Real rho = 1.225; //kg/m^3
parameter Real speed_wind = 0; //account for the speed of the wind
parameter Real cross_sect_area = 1.6 + 0.00056 * (Mass_car - 765); //See reference above
parameter Real drag_coef = 0.455; //average of range provided in book





equation
 
  acceleration = der(speed_car)*dT;
  
  Fd = rho * cross_sect_area * drag_coef * (speed_car - speed_wind)^2;
  
  Fr = Mass_car * g * Modelica.Math.cos(Modelica.Units.Conversions.from_deg(slope)) * ((0.006 + 0.23*10^(-6))*(speed_car*3.6)^2); 
  //rolling resistance coefficient with speed converted into km/h
  
  Fg = Mass_car * g * Modelica.Math.sin(Modelica.Units.Conversions.from_deg(slope)); 
  //the slope is positive when vehicle goes uphill (so gravitational force adds to the resistance) and negative downhill (i.e. gravitational force substracts from the resistance nd helps the motion of the vehicle)
  

  W = Mass_car * acceleration;
  
 
 
  power_source = (Fd + Fr + Fg + W) * speed_car;

  


end vehicle;
