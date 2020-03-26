## Acknowledgements

This is a spin-off from **Element AI** team's *corona-calculator* (https://corona-calculator.herokuapp.com/).

### Modifications

I use Robert Koch Institute's estimation of "no social-distancing scenario" for Germany as a benchmark for social distancing simulation. The report states that the number of active cases will rise to ~ 10 millions in 3 months if no intervention is made as of 19 Mar 2020. (https://www.iamexpat.de/expat-info/german-expat-news/rki-coronavirus-could-infect-10-million-people-germany)

In this version, I have revised and made some modifications to fit my own analysis for the situation in **GERMANY**. Please feel free to port the codes and make changes to fit your requirements (*for example*: to analyze other countries situation). 

#### **Data inputs**

 - Include "Incubation period" as a factor to capture the real "going to be reported" cases after lock-down initiated.
 
 
 - Transmission rate & basic reproduction rate (R0) parameters are recalculated based on means of all related researches on MIDAS network data (https://github.com/midas-network/COVID-19)
 
 
 - Recovery rate is obtained as "time from symptom onset to recovery" from Singapore and China research journals (using lognormal parametric survival methods & ratio of cumulative number of recovered/deaths and that of infected at time *t*)
 
 
 - Number of *Confirmed / Recovered / Death* data is obtained from Johns Hopkins University's repository (https://github.com/CSSEGISandData/COVID-19/)
 
 
 - Extra plots (part 6) data are obtained from **RKI repository** since RKI has broken down the number to specific territories in Germany. (https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0)
 
 
 - Age cohort mortality rates for **Germany** specifically (obtain age distribution in the population at https://www.populationpyramid.net/germany/2019/)
 
 
#### **Methodology**

 - SEIR model with **vital dynamic** instead of SIR (as of 25.03, seems like the authors are also applying SEIR model).
     - E stands for "Exposed" - individuals that are infected but show no symptoms which become carriers
     
     
 - Lock-down (social distancing) initiated differently from each states:
     - Bavaria was the first state to start the partial lock-down since 20 March 2020
     - Nation wide partial lock-down followed from 23 March 2020 (after Chancellor Merkel's speech)
     
 - Since incubation period plays an important factor in this pandemic, the true cases after lock-down will have to incorporate this time-lag factor in
 
#### **Forecasting**
 - Forecasting models are based on 5 different scenarios:
     1. No social distancing at all
     2. 25% social distancing
     3. 50% social distancing
     4. 75% social distancing (which is the closest to reality)
     5. 100% social distancing
   
## Literature Reviews


1. **SIR model:**

![SIR Model](https://upload.wikimedia.org/wikipedia/commons/8/8a/SIR.PNG)

![SIR func](http://idmod.org/docs/general/_images/math/7edd99664ee58dde174cfe47bf51ade942786541.png)

    **Where N (population) = S + I + R**
    
    The model asummes:

    - The population size is fixed (i.e., no births, deaths due to disease, or deaths by natural causes)
    - Incubation period of the infectious agent is instantaneous
    - Duration of infectivity is same as length of the disease
    - Completely homogeneous population with no age, spatial, or social structure
    - The crucial factor governing disease spread is R0 (the basic reproduction rate), which is the **average number of people somebody with the disease infects.** This is a function of the number of susceptible people, the infection rate **β** and the recovery rate **γ**.

        **β = Probability of transmission x Number of contacts**

        **R0 = Probability of transmission x Number of Contacts per day x Number of infectious days**


2. **SEIR model:**

![SEIR Model](https://upload.wikimedia.org/wikipedia/commons/3/3d/SEIR.PNG)

![SEIR func](http://idmod.org/docs/general/_images/math/5c34ba7654b6b1031ac83c60ea98007456d22ee3.png)


With vital dynamics (birth + death rate)

![SEIR func vital](http://idmod.org/docs/general/_images/math/7a0619d75a08582ad67f21d3a0ffb938b8576920.png)

   **Where N = S + E + I + R**
    
   - Vital dynamic - incorporate birth and death rate of the population sample into the formula
   - **μ** and **ν** represent the birth and death rates, respectively, and are assumed to be equal to maintain a constant population
