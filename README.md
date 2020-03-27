<center><h1> COVID-19 social distancing simulation </h1></center>

<h1><center>When can we resume our normal lives (Germany scenario)?</h1></center>

## Acknowledgements

Insired from **Element AI** team's *corona-calculator* (https://corona-calculator.herokuapp.com/) and **Christian Hubbs**'s dynamic diffusion models for epidemiology (https://www.datahubbs.com/)

## Introduction

The purpose of this analysis is to make best "guess" on when is the time for us to get back to our normal lives in **Germany**.

Robert Koch Institute (RKI)'s estimation of "no social-distancing scenario" for **Germany** was used here as a benchmark for social distancing simulation. The report stated that the number of infected cases will rise to **~10 millions** in 3 months if no intervention is implemented (as of 19 Mar 2020). (https://www.iamexpat.de/expat-info/german-expat-news/rki-coronavirus-could-infect-10-million-people-germany)

Given the fact that society is now in a "lock-downed", I would like to create 5 different scenarios of social distancing using social demographics & disease data with simple epidemiological models in this first MVP.

The 5 scenarios are as follow:
     1. No social distancing at all
     2. 25% social distancing
     3. 50% social distancing
     4. 75% social distancing (which is the closest to reality)
     5. 100% social distancing (mimimum contact to any other human)
   
## Methodology

The whole project can be quickly summarized in this chart:
![COVID19_DE_chart](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/COVID%2019%20DE%20simulation.png?raw=true)

### Data inputs

 - Include "Incubation period" as a factor to capture the real "going to be reported" cases after lock-down initiated.
 
 - Transmission rate & basic reproduction rate (R0) parameters are recalculated based on means of all related researches on MIDAS network data (https://github.com/midas-network/COVID-19)
 
 
 - Recovery rate is obtained as "time from symptom onset to recovery" from Singapore and China research journals (using lognormal parametric survival methods & ratio of cumulative number of recovered/deaths and that of infected at time *t*)
 
 
 - Number of *Confirmed / Recovered / Death* data is obtained from Johns Hopkins University's repository (https://github.com/CSSEGISandData/COVID-19/)
 
 
 - Extra plots (part 6) data are obtained from **RKI repository** since RKI has broken down the number to specific territories in Germany. (https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0)
 
 
 - Age cohort mortality rates for **Germany** specifically (obtain age distribution in the population at https://www.populationpyramid.net/germany/2019/)
 
 
### Methodology

 - SEIR model with **vital dynamic** instead of SIR (as of 25.03, seems like the authors are also applying SEIR model).
     - E stands for "Exposed" - individuals that are infected but show no symptoms which become carriers
     
 - Lock-down (social distancing) initiated differently from each states:
     - Bavaria was the first state to start the partial lock-down since 20 March 2020
     - Nation wide partial lock-down followed from 23 March 2020 (after Chancellor Merkel's speech)
     
 - Since incubation period plays an important factor in this pandemic, the true cases after lock-down will have to incorporate this time-lag factor in


## Literature Reviews

### R0 - Basic reproduction rate
One of the metrics that people have been hearing everywhere these days is R0 ("R-naught") or "basic reproduction rate. 

R0 tells you the average number of people who will catch a disease from one contagious person. It specifically applies to a population of people who were previously free of infection and haven’t been vaccinated. If a disease has an R0 of 18, a person who has the disease will transmit it to an average of 18 other people, as long as no one has been vaccinated against it or is already immune to it in their community.

One way to calculate R0 is:

   **R0 = Probability of transmission x Number of Contacts per day x Number of infectious days**


![R0 example](https://miro.medium.com/max/648/1*kc4-Bv2nzIvb9xG6ELHuzA.png)
<i><center>Increasing R0 values indicate more infectious diseases (Source: [Healthline](https://www.healthline.com/health/r-nought-reproduction-number))</center></i>

### SIR model

The model asummes:
   - The population size is fixed (i.e., no births, deaths due to disease, or deaths by natural causes)
   - Incubation period of the infectious agent is instantaneous
   - Duration of infectivity is same as length of the disease
   - Completely homogeneous population with no age, spatial, or social structure
    
![SIR Model](https://upload.wikimedia.org/wikipedia/commons/8/8a/SIR.PNG)
![SIR func](http://idmod.org/docs/general/_images/math/7edd99664ee58dde174cfe47bf51ade942786541.png)

   **Where N (population) = S(Susceptible) + I (Infected)+ R (Recovered)*   
   
   The crucial factor governing disease spread is R0 (the basic reproduction rate), which is the **average number of people somebody with the disease infects.**
   
   The parameters , **β** (beta) and **γ** (gamma) are defined as follow:

   1. **β** = average contact rate in the population.
   
   Another way to defined **β** is:
    - **β** = Probability of transmission x Number of contacts
   
   2. **γ** = inverse of the mean infectious period (1/t_infectious). Or usually known as "recovery rate"
   
And R0 can be calculated to get those parameters:

<b><center>R0 = β/γ</center></b>


### SEIR model
![SEIR Model](https://upload.wikimedia.org/wikipedia/commons/3/3d/SEIR.PNG)
![SEIR func](http://idmod.org/docs/general/_images/math/5c34ba7654b6b1031ac83c60ea98007456d22ee3.png)

**Where N (population) = S(Susceptible) + E (Exposed) + I (Infected)+ R (Recovered)** 
   
   The 3rd parameter **δ** (delta) is calculated as follow:
   
   3. **δ** = inverse of the incubation period (1/t_incubation)
      
   Here we have another parameter to show those who are exposed (asymptomatic)
With vital dynamics (birth + death rate **μ** and **ν**)

![SEIR func vital](http://idmod.org/docs/general/_images/math/7a0619d75a08582ad67f21d3a0ffb938b8576920.png)
   
   - **μ** and **ν** represent the birth and death rates, respectively, and are assumed to be equal to maintain a constant population
