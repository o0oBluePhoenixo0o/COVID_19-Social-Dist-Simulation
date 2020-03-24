# COVID19-simulation
Social distancing simulation with time-lag factor. Here with the case of Germany acting as prime example with geospatial and demographics data enhancement.

A "poor-man" ported to fit basic needs from https://github.com/archydeberker/corona-calculator, in this version, I have done customizations as follow:

1. Update data sources:

      a. Demographic distribution from the age pyramid to get more accurate age group propotion for each country https://www.populationpyramid.net/

      b. Change data source of 'Confirmed / Deaths/ Recovered' to the global time series file at https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series
      
2. Allow changes in recovery rate / transmission rate to show simulation

## Plan for next update

1. Population density will affect differently on social distancing method
2. Time-lag reported confirmed case (+ 7 incubation days) to see changes in active infection curve
