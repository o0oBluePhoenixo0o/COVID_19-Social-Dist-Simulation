import numpy as np
import pandas as pd
import re

import datetime
from datetime import datetime, timedelta

# dplyr-style for python
from dppd import dppd
dp, X = dppd()
import itertools

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
    S_0, E_0, I_0, R_0 = init_vals
    S, E, I, R = [S_0], [E_0], [I_0], [R_0]
    delta, beta, gamma, social_dist = params
    dt = t[1] - t[0]
    for _ in t[1:]:
        next_S = S[-1] - (social_dist*beta*S[-1]*I[-1])*dt
        next_E = E[-1] + (social_dist*beta*S[-1]*I[-1] - delta*E[-1])*dt
        next_I = I[-1] + (delta*E[-1] - gamma*I[-1])*dt
        next_R = R[-1] + (gamma*I[-1])*dt
        S.append(next_S)
        E.append(next_E)
        I.append(next_I)
        R.append(next_R)
    return np.stack([S, E, I, R]).T