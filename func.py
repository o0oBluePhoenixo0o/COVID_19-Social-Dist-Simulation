import numpy as np
import pandas as pd
import re

import datetime
from datetime import datetime, timedelta

# dplyr-style for python
from dppd import dppd
dp, X = dppd()
import itertools

_DEFAULT_TIME_SCALE = 12 * 3 * 31  # 36 months

"""
Preprocessing data
"""
def _get_latest_bed_estimate(row):
    """Try to estimate the lastest number of beds / 1000 people """
    non_empty_estimates = [float(x) for x in row.values if float(x) > 0]
    try:
        return non_empty_estimates[-1]
    except IndexError:
        return np.nan
    
def preprocess_bed_data(path):
    df = pd.read_csv(path)
    # Total hospital beds = HOPITBED
    # Total number of beds UNIT = NOMBRENB
    # No of beds per 1000 ppl UNIT = RTOINPNB
    df = (dp(df)
          .query("VAR == 'HOPITBED' & UNIT == 'NOMBRENB'")
          .select(["Country","Year","Value"])
          .pivot(index='Country',columns='Year',values='Value')
          .pd)
    # Beds are per 1000 people
    df["Latest Bed Estimate"] = df.apply(_get_latest_bed_estimate, axis=1)
    return df 

def get_latest_date(global_confirmed,
                    global_recovered,
                    global_death):
    # Get latest dates from all 3 datasets
    r_date = datetime.strptime(global_recovered.iloc[:,-1].name,'%m/%d/%y').date()
    c_date = datetime.strptime(global_confirmed.iloc[:,-1].name,'%m/%d/%y').date()
    d_date = datetime.strptime(global_death.iloc[:,-1].name,'%m/%d/%y').date()
    
    # If they are synchronized
    if r_date == c_date == d_date: 
        target_date = global_recovered.iloc[:,-1].name
    else:
        target_date = min(r_date, c_date, d_date)
        target_date = datetime.strftime(target_date,"%m/%d/%y")
        target_date = target_date[-(len(target_date)-1):]
        
    print('Latest cases data is captured on ' + str(target_date))
    
    return target_date

def prepare_historical_df(target_country,
                          target_date,
                          global_confirmed,
                          global_recovered,
                          global_death):

    # Convert and merge
    r = dp(global_recovered).query(target_country).assign(Type = "Recovered").pd
    c = dp(global_confirmed).query(target_country).assign(Type = "Confirmed").pd
    d = dp(global_death).query(target_country).assign(Type = "Death").pd

    historical_df = pd.concat([r,c,d])

    historical_df= (dp(historical_df)        
                     .select(["-Province/State",'-Lat','-Long','-Country'])
                     .set_index('Type')
                    .pd)
    confirmed = pd.DataFrame(historical_df.iloc[0]).rename_axis('Date').reset_index()
    confirmed['Date'] = pd.to_datetime(confirmed['Date']) 
    confirmed['Status'] = "Confirmed"
    confirmed.columns = ['Date', 'Number', 'Status']

    deaths = pd.DataFrame(historical_df.iloc[1]).rename_axis('Date').reset_index()
    deaths['Date'] = pd.to_datetime(confirmed['Date']) 
    deaths['Status'] = "Deaths"
    deaths.columns = ['Date', 'Number', 'Status']

    recovered = pd.DataFrame(historical_df.iloc[2]).rename_axis('Date').reset_index()
    recovered['Date'] = pd.to_datetime(confirmed['Date']) 
    recovered['Status'] = "Recovered"
    recovered.columns = ['Date', 'Number', 'Status']

    historical_df = confirmed.append(deaths).append(recovered)
    
    return historical_df


def get_cases_number(target_date,
                     target_country,
                     global_confirmed,
                     global_recovered,
                     global_death):
    """ Get the latest number of deaths, confirmed and recovered cases"""
    number_cases_deaths =(dp(global_death)
                         .select(['Country',target_date])
                         .query(target_country)
                         .pd).iloc[0][target_date]

    number_cases_confirmed =(dp(global_confirmed)
                         .select(['Country',target_date])
                         .query(target_country)
                         .pd).iloc[0][target_date]

    number_cases_recovered =(dp(global_recovered)
                     .select(['Country',target_date])
                     .query(target_country)
                     .pd).iloc[0][target_date]
    return (number_cases_deaths,number_cases_confirmed,number_cases_recovered)



"""
Model building
"""

# Credited to Christian Hubbs @https://www.datahubbs.com/
def seir_model_with_soc_dist(init_vals, params, t):
    """Susceptible - Exposed - Infected - Recovered
    """
    # Get initial values
    S_0, E_0, I_0, R_0 = init_vals
    S, E, I, R = [S_0], [E_0], [I_0], [R_0]
    delta, beta, gamma, social_dist = params
    
    # Total population = S + E + I + R
    N = S_0 + E_0 + I_0 + R_0
    
    for _ in t[1:]:
        next_S = S[-1] - (social_dist*beta*S[-1]*I[-1])/N
        next_E = E[-1] + (social_dist*beta*S[-1]*I[-1])/N - delta*E[-1]
        next_I = I[-1] + (delta*E[-1] - gamma*I[-1])
        next_R = R[-1] + (gamma*I[-1])
        next_H = 
        S.append(round(next_S))
        E.append(round(next_E))
        I.append(round(next_I))
        R.append(round(next_R))
    return np.stack([S, E, I, R]).T

#             # Forecast
#             s_t = S[-1] - self._infection_rate * I[-1] * S[-1] / population
#             i_t = (I[-1]+ self._infection_rate * I[-1] * S[-1] / population- (weighted_death_rate + self._recovery_rate) * I[-1])
#             r_t = R[-1] + self._recovery_rate * I[-1]
#             d_t = D[-1] + weighted_death_rate * I[-1]
#             h_t = self._hospitalization_rate * i_t



#         for t in range(num_days):
#             # There is an additional chance of dying if people are critically ill
#             # and have no access to the medical system.
#             if I[-1] > 0:
#                 underserved_critically_ill_proportion = (
#                     max(0, H[-1] - self._hospital_capacity) / I[-1]
#                 )
#             else:
#                 underserved_critically_ill_proportion = 0
#             weighted_death_rate = (self._normal_death_rate * (1 - underserved_critically_ill_proportion)
#                 + self._critical_death_rate * underserved_critically_ill_proportion)

#         # Days with no change in I
#         days_to_clip = [I[-i] == I[-i - 1] for i in range(1, len(I))]
#         index_to_clip = days_to_clip.index(False)
#         if index_to_clip == 0:
#             index_to_clip = 1
#         # Look at at least a few months
#         index_to_clip = min(index_to_clip, _DEFAULT_TIME_SCALE - 3 * 31)



def get_status_by_age_group(AGE_DATA, MortalityRate,
                            death_prediction: int, 
                            recovered_prediction: int):
    """
    @Credited to Element AI's team for this function
    
    Get outcomes segmented by age.
    We modify the original percentage death rates from data/age_data.csv to reflect a mortality rate that has been
    adjusted to take into account hospital capacity. The important assumption here is that age groups get infected at
    the same rate; that is, every group is equaly as likely to contract the infection.
    
    :param death_prediction: Number of deaths predicted.
    :param recovered_prediction: Number of recovered people predicted.
    :return: Outcomes by age in a DataFrame.
    """
    age_data = AGE_DATA
    infections_prediction = recovered_prediction + death_prediction

    # Effective mortality rate may be different than the one defined in data/constants.py because once we reach
    # hospital capacity, we increase the death rate. We assume the increase in death rate will be proportional, even
    # though it probably won't be since more old people require medical care, and thus will see increased mortality
    # when the medical system reaches capacity.
    effective_death_rate = death_prediction / infections_prediction
    death_increase_ratio = effective_death_rate / MortalityRate

    # Get outcomes by age
    age_data["Infected"] = (AGE_DATA.Proportion_DE_2020 * infections_prediction).astype(int)
    age_data["Need Hospitalization"] = (
        age_data["Hospitalization Rate"] * age_data.Infected
    )
    age_data["Dead"] = (
        age_data.Mortality * death_increase_ratio * age_data.Infected
    ).astype(int)
    age_data["Recovered"] = (age_data.Infected - age_data.Dead).astype(int)

    return age_data.iloc[:, -4:]