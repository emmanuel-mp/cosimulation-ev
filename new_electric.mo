model new_electric


input Real current_delivered;

output Real voltage (start = 115);
output Real current_sc;


Real C = 85;
Real Vmax = 120;
Real current_fc = 60; //from Stephane data, max current_fc = 120A, take 60 as constant output of FC
Real power_source;
Real soc;



equation



//ELECTRICAL MODELING

der(voltage) = current_sc / (-1 * C);

when {voltage > 120}   then
reinit(voltage, 119);
end when;

when {voltage < 60}   then
reinit(voltage, 61);
end when;

soc = (voltage / Vmax);
current_sc = current_delivered - current_fc; // behavior of system
power_source = current_delivered * voltage;






end new_electric;
