model throttle



input Real voltage;
input Real driver_pedal;

output Real throttle;
output Real current_sc;
output Real current_delivered;

Real current_sc_max = 400;
Real voltage_sc_max = 120;
Real voltage_sc_min = 60;

Real current_fc_max = 120;
Real current_fc = 60;


Real volt_top1 = voltage_sc_max/2;
Real volt_top2 = voltage_sc_max;


equation


if driver_pedal > 0 then //positive driver acceleration means current positive --> 1st half of the plot

voltage = (voltage_sc_max / (2 * current_sc_max))*current_sc + volt_top1;
current_delivered = current_fc + current_sc;
throttle = current_delivered / (current_sc_max + current_fc); //use current_fc or current_fc_max ???



elseif driver_pedal == 0 then 

current_sc = 0;
current_delivered = 0; //current_fc + current_sc;
throttle = current_delivered / (current_sc_max + current_fc); //use current_fc or current_fc_max ???



else

voltage = (voltage_sc_max / (2 * current_sc_max))*current_sc + volt_top2;
current_delivered = current_fc + current_sc;
throttle = current_delivered / (current_sc_max + current_fc_max); //use current_fc or current_fc_max ???



end if;


end throttle;
