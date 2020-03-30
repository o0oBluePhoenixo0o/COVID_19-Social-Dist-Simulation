## Introduction

The purpose of this analysis is to make best "guess" on when is the time for us to get back to our normal lives in **Germany**.

Robert Koch Institute (RKI)'s estimation of "no social-distancing scenario" for **Germany** was used here as a benchmark for social distancing simulation. The report stated that the number of infected cases will rise to **~10 millions** in 3 months if no intervention is implemented (as of 19 Mar 2020). (https://www.iamexpat.de/expat-info/german-expat-news/rki-coronavirus-could-infect-10-million-people-germany)

Given the fact that society is now in a "lock-downed", I would like to simulate 5 different scenarios of social distancing using social demographics & disease data with simple epidemiological models in this first try-out.

The 5 scenarios are as follow:
 1. No social distancing at all
 2. 10% social distancing
 3. 25% social distancing
 4. 50% social distancing
 5. 90% social distancing
   
## Overview

The whole project can be quickly summarized in this chart:
![COVID19_DE_chart](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/COVID%2019%20DE%20simulation.png?raw=true)

## Data Input

### MIDAS research networks: (https://github.com/midas-network/COVID-19)


- **Incubation period** - time elapsed between exposure and when symptoms and signs are first apparent
- **Recovery rate** - "time from symptom onset to recovery", obtained from Singapore and China research journals (using lognormal parametric survival methods & ratio of cumulative number of recovered/deaths and that of infected at time *t*).
- **Basic reproduction rate (R0)** - the average number of people who will catch a disease from one contagious person. It specifically applies to a population of people who were previously free of infection and haven’t been vaccinated. If a disease has an R0 of 18, a person who has the disease will transmit it to an average of 18 other people, as long as no one has been vaccinated against it or is already immune to it in their community.

     One way to calculate R0 is:

    **R0 = Probability of transmission x Number of Contacts per day x Number of infectious days**


![R0 example](https://miro.medium.com/max/648/1*kc4-Bv2nzIvb9xG6ELHuzA.png)
<i><center>Increasing R0 values indicate more infectious diseases (Source: [Healthline](https://www.healthline.com/health/r-nought-reproduction-number))</center></i>


- **Asymtompmatic case probability** - Proportion of true cases showing no symptoms. The number comes from a study led on passengers of the Diamond Princess Cruise, in Japan https://www.eurosurveillance.org/content/10.2807/1560-7917.ES.2020.25.10.2000180
- **Reporting Rate** - the latest research with confidence interval up to 95% states that the real reporting rate for COVID-19 cases is 75% (as of 29 Mar 2020)


To calculate increase deaths rate per day, I use the following parameters:
- **Critical death rate** - case fatality rate is ~ 12% if the patients is not able to get hospitalized. This is the max reported from Wuhan: [Estimating Risk for Death from 2019 Novel Coronavirus Disease, China, January–February 2020](https://wwwnc.cdc.gov/eid/article/26/6/20-0233_article)
- **Time from hospitalization to death** - this parameter is used to calculate the Snapshot increased death cases for those who have been hospitalized.
    
    ### JHU (Johns Hopkins University) and RKI (Robert Koch Institute) repositories
 - Number of *Confirmed / Recovered / Death* world data is obtained from Johns Hopkins University's repository (https://github.com/CSSEGISandData/COVID-19/)- this data is only contained the numbers on country-level.
  
 - State-level numbers from RKI (https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0)
 
 ### Social demographics data
 - Age distribution for **Germany** - pyramid age (https://www.populationpyramid.net/germany/2019/). The other countries data can also be collected at this page (up to 2018 for some countries)
 - Number of available hospital beds and health care staffs from OECD databank (https://data.oecd.org/healtheqt/hospital-beds.htm)
 - For mortality rates per age cohort, I use data from ["Imperial College COVID-19 Response Team"](https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf) report on 16 Mar 2020. The table below shows the mortality rates for each age cohorts:
 ![Mortality Rate](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/mortality_rate_1603.PNG?raw=true)
 <center><i>Source: Imperial College COVID-19 Response Team</i></center>
 
 ## Models


### SIR

The model asummes:
   - The population size is fixed (i.e., no births, deaths due to disease, or deaths by natural causes)
   - Incubation period of the infectious agent is instantaneous
   - Duration of infectivity is same as length of the disease
   - Completely homogeneous population with no age, spatial, or social structure
    
![SIR Model](https://upload.wikimedia.org/wikipedia/commons/8/8a/SIR.PNG)
![SIR func](http://idmod.org/docs/general/_images/math/7edd99664ee58dde174cfe47bf51ade942786541.png)

   **Where N (population) = S(Susceptible) + I (Infected)+ R (Recovered)**   
   
   The crucial factor governing disease spread is R0 (the basic reproduction rate), which is the **average number of people somebody with the disease infects.**
   
   The parameters , **β** (beta) and **γ** (gamma) are defined as follow:

   1. **β** = average contact rate in the population.
   
   Another way to defined **β** is:
    - **β** = Probability of transmission x Number of contacts
   
   2. **γ** = inverse of the mean infectious period (1/t_infectious). Or usually known as "recovery rate"
   
And R0 can be calculated to get those parameters:

<b><center>R0 = β/γ</center></b>


### SEIR 
![SEIR Model](https://upload.wikimedia.org/wikipedia/commons/3/3d/SEIR.PNG)
![SEIR func](http://idmod.org/docs/general/_images/math/5c34ba7654b6b1031ac83c60ea98007456d22ee3.png)


**Where N (population) = S(Susceptible) + E (Exposed) + I (Infected)+ R (Recovered)** 
   
   **Exposed** means the population has been exposed to the disease but not yet show any symptom nor infectious (a.k.a - still in incubation period). Thus, the 3rd parameter **δ** (delta) is calculated as follow:
   
   3. **δ** = inverse of the incubation period (1/t_incubation)
      
<!--    Here we have another parameter to show those who are exposed (asymptomatic)
With vital dynamics (birth + death rate **μ** and **ν**)

![SEIR func vital](http://idmod.org/docs/general/_images/math/7a0619d75a08582ad67f21d3a0ffb938b8576920.png)
   
   - **μ** and **ν** represent the birth and death rates, respectively, and are assumed to be equal to maintain a constant population -->
   
### SEIR + DH 
   - Here I include another 2 factors **D** & **H** which account for number of death cases and number of hospitalized cases. 
   ![SEIR_DH](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/SEIRDH.png?raw=true)
   
   **Where N (population) = S(Susceptible) + E (Exposed) + I (Infected)+ R (Recovered) + D (Deaths)** 
   
   The 2 numbers are calculated as follow:
   
   **Hospitalized cases (on day t) = Hospitalization rate (per age cohort) * Active infected cases (on day t)**
   
   
   - To calculate number of death cases, I use the **Time from hospitalization to death** to get the past hospitalized cases (in the event health care system is not overloaded) and estimate the total death cases on day(t).
   
   
   ![Death rate](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/death_rate.png?raw=true)
   
   - For critical death rate, I used the value from this report [Estimating Risk for Death from 2019 Novel Coronavirus Disease, China, January–February 2020](https://wwwnc.cdc.gov/eid/article/26/6/20-0233_article)
   
   ## Simulation

Before moving to the simulation, let's take a look at historical data of Germany. As of 28 Mar 2020, Germany has nearly 60k confirmed cases with ~ 9k recovered and close to 500 deaths.
![Historical_df](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/Historical_280320.png?raw=true)

Let's try to forecast what would happen in the next 180 days ( 6 months). Since mortality rates used in this simulation are reported from current researches (not yet final), the dynamic might change in the future when we have more accurated number.

#### No social distancing
For the first case where there is no social contact. Since RKI forecasts the total active infected cases in Germany will reach 10 millions in the next 3 months, let's take that 10 millions as a benchmark for "no social distancing". 

The estimation for the social distancing parameter here is **1.2** which leads us to 10 millions active infected case by **Jun 19 2020**

![No_social_dist](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/1_No_social_dist.png?raw=true)

In this scenario, the model predicts that Germany will reach its peak occupancy around **mid July** where ~1.25 millions active cases are needed to be hospitalized but only half of them get the treatment. As a result, the "Total Deaths" curve increases significantly after this period (time from hospitalization to death on average is 10 days).

By the end of this forecast period (6 months), the total number of deaths would be **2.5 millions**

![No_social_dist_bed](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/1_No_social_dist_beds.png?raw=true)

#### 10% social distancing
In this scenario, Germany applies social distancing method starting from 23 Mar 2020 (after the speech of Chancellor Merkel). As can be seen, the infected cases drops a little bit compare to no social distancing scenario. And the total number of predicted death cases is not so different from the first case (**~2.3 millions deaths**).

Also Germany will overload its health care capacity a little bit later than the 1st scenario, this time it will reach its peak at the **beginning of August**.

![10pct](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/2_10pct_social_dist.png?raw=true)
![10pct_beds](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/2_10pct_social_dist_beds.png?raw=true)

#### 25% social distancing
Next, we assume that Germany applies **25%** social distancing method starting from 23 Mar 2020.

As can be seen, the infected cases drops **significantly** compare to the other 2 scenarios above. In this case, the total of death cases after 180 days is around **1.3 millions** (which is still a lot) and the country health care system will still be overloaded (with peak around **end of August**). 
![25pct](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/3_25pct_social_dist.png?raw=true)
![25pct_beds](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/3_25pct_social_dist_beds.png?raw=true)

#### 50% social distancing
We have "flatten the curve", but not so much. Now let's see if everyone obeys the rule of social distancing to **50%** (from 23 Mar 2020)

As can be seen, the infected cases drops **dramatically** compare to the 3 scenarios above. In this case, the total of death cases after 180 days is only **70k** and the country health care system will still not be overloaded (with peak around **mid of September**). 

![50pct](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/4_50pct_social_dist.png?raw=true)
![50pct_beds](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/4_50pct_social_dist_beds.png?raw=true)

#### 90% social distancing
The scenario above seems "good enough", but what if we really follow the social distancing rule to the extreme? Let's try to simulate the situation if everyone follows social distancing to **90%**.

As you can see, if everyone really follows the rules, the total number of deaths after 180 days will be lower to **12.5k** and Germany healthcare system will not be overloaded at all! 

![90_pct](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/5_90pct_social_dist.png?raw=true)
![90pct_beds](https://github.com/o0oBluePhoenixo0o/COVID_19-Social-Dist-Simulation/blob/master/img/5_90pct_social_dist_beds.png?raw=true)

## Acknowledgements

Inspired from **Element AI** team's *corona-calculator* (https://corona-calculator.herokuapp.com/) and **Christian Hubbs**'s dynamic diffusion models for epidemiology (https://www.datahubbs.com/)
## Closing up...

I am not an epidemiologist so I can't guarantee 100% that the scenarios above will become reality. However, I believe the charts I created would somehow explain the impact of "social distancing" to this pandemic and hopefully everyone would follow the guideline. Please keep in mind that this is a simple SEIR+DH model and the available data used to train the model was limited in the moment of writing the article. 

Furthermore, I hope this will inspire people to explore more on the numbers and models beside sticking to just mainstream medias and potentially not-so-reliable news.
