import numpy as np
import pandas as pd
import re

import datetime
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# dplyr-style for python
from dppd import dppd
dp, X = dppd()
import itertools

_DEFAULT_TIME_SCALE = 12 * 3 * 31  # 36 months

"""
Preprocessing data
"""
# Convert string percentage to integer
def a(m):e=m.strip("%");f=float(e);return f/100if e!=m else str(f*100)+"%"

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
    confirmed = pd.DataFrame(historical_df.iloc[1]).rename_axis('Date').reset_index()
    confirmed['Date'] = pd.to_datetime(confirmed['Date']) 
    confirmed['Status'] = "Confirmed"
    confirmed.columns = ['Date', 'Number', 'Status']

    deaths = pd.DataFrame(historical_df.iloc[2]).rename_axis('Date').reset_index()
    deaths['Date'] = pd.to_datetime(confirmed['Date']) 
    deaths['Status'] = "Deaths"
    deaths.columns = ['Date', 'Number', 'Status']

    recovered = pd.DataFrame(historical_df.iloc[0]).rename_axis('Date').reset_index()
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

def hospitalized_case(I, AGE_DATA):
    """ Calculated hospitalization cases"""
    AGE_DATA['Snapshot_hospitalized'] = round(AGE_DATA['Proportion_DE_2020'] * 
                                          I * 
                                          AGE_DATA['Hospitalization Rate'])
    
    no_h = AGE_DATA['Snapshot_hospitalized'].sum()
    
    return no_h

def deaths_case(I_h2d,
                AGE_DATA,
                CDR, 
                no_hospital_beds):
    """ Calculated death cases, if active cases over capacity ==> use critical death rate"""
    
    if hospitalized_case(I_h2d, AGE_DATA) <= no_hospital_beds : # still not overloaded on day (t-h2d)
        # Number of deaths with hospitalization
        AGE_DATA['Snapshot_deaths'] = round(AGE_DATA['Proportion_DE_2020']
                                         * hospitalized_case(I_h2d, AGE_DATA) # actived cases (t-h2d) days ago will used
                                         * AGE_DATA['Mortality'])
        
        # Minus yesterday_deaths to get number of NEW deaths
        no_Snapshot_d = AGE_DATA['Snapshot_deaths'].sum()
        AGE_DATA['Total_Deaths'] = AGE_DATA['Total_Deaths'] + (AGE_DATA['Snapshot_deaths'])
        
    else: # active HOSPITALIZED case overloaded on day (t-h2d)
        # Number of critial cases on day (t-h2d) but no hospital beds available
        no_without_beds = hospitalized_case(I_h2d, AGE_DATA) - no_hospital_beds
        # Snapshots = amount of death cases on day (t)
        AGE_DATA['Snapshot_deaths_no_beds'] = round(AGE_DATA['Proportion_DE_2020'] * 
                                                    no_without_beds * 
                                                    CDR)
        # Number of deaths with hospitalization
        AGE_DATA['Snapshot_deaths'] = round(AGE_DATA['Proportion_DE_2020'] * 
                                            no_hospital_beds * # max number of beds have been used
                                            AGE_DATA['Mortality'])
        
        # Minus yesterday_deaths to get number of NEW deaths
        no_Snapshot_d = AGE_DATA['Snapshot_deaths'].sum() + AGE_DATA['Snapshot_deaths_no_beds'].sum()
        # Deaths due to no beds
        AGE_DATA['Total_Deaths_no_beds'] = AGE_DATA['Total_Deaths_no_beds'] + AGE_DATA['Snapshot_deaths_no_beds']
        AGE_DATA['Total_Deaths'] = AGE_DATA['Total_Deaths'] + (AGE_DATA['Snapshot_deaths'] + AGE_DATA['Snapshot_deaths_no_beds'])
    
    return no_Snapshot_d


# Modifed from Christian Hubbs @https://www.datahubbs.com/
def seir_model_with_soc_dist(init_vals, params, t):
    """Susceptible - Exposed - Infected - Recovered
    Infected cases here is the number of current active cases!
    """
    # Get initial values
    S_0, E_0, I_0, R_0, H_0, D_0, CD_0 = init_vals
    S, E, I, R, H, D, CD = [S_0], [E_0], [I_0], [R_0], [H_0], [D_0], [CD_0]
    
    (delta, beta, gamma, 
     no_hospital_beds, # healthcare capacity
     social_dist, # social distance factor
     CDR, #critical death rate without hospitalization
     AGE_DATA,
     target_country,
     global_confirmed,
     global_death,
     global_recovered,
     h_to_d) = params
    
    # Total population = S + E + I (active cases) + R + D
    N = S_0 + E_0 + I_0 + R_0 + D_0
        
    for _ in t[1:]:
        next_S = S[-1] - (social_dist*beta*S[-1]*I[-1])/N
        next_E = E[-1] + (social_dist*beta*S[-1]*I[-1])/N - delta*E[-1]
        
        # Current Infected cases 
        # = Yesterday infected cases + (new exposed cases - recovered - deaths)
        next_I = I[-1] + (delta*E[-1] - gamma*I[-1]) - D[-1]
        # Current recovered = new recovered - deaths
        next_R = R[-1] + (gamma*I[-1]) - D[-1]
        
        # Hospitalized case (part of current Infected cases)
        next_H = hospitalized_case(next_I, AGE_DATA)
        
        # Estimate death cases of day (t) with the hospitalized case on day (t -h2d) days ago
        try:
            next_D = deaths_case(I[-h_to_d], # active infected case on day (t-h2d) days
                                 AGE_DATA, CDR, no_hospital_beds)
        except:
            try:
                # if I[-h_to_d] is not exist yet before I_0
                # use historical active infected cases [h_to_d] days ago
                past_date = datetime.strftime(datetime.now() + timedelta(_) - timedelta(h_to_d),"%m/%d/%y")
                past_date = past_date[-(len(past_date) -1) :]
                past_h_to_d = get_cases_number(past_date,
                                                    target_country,
                                                    global_confirmed,
                                                    global_recovered,
                                                    global_death)
                # Get active infected case in the past
                past_I = past_h_to_d[1] - past_h_to_d[0] - past_h_to_d[2]
                next_D = D[0] + deaths_case(past_I,AGE_DATA,CDR, no_hospital_beds)
            except:
                # in the event of yesterday data was not updated --> temporary use yesterday data
                next_D = D[-1]
                
        next_CD = CD[-1] + next_D
        
        S.append(round(next_S))
        E.append(round(next_E))
        I.append(round(next_I))
        R.append(round(next_R))
        H.append(round(next_H))
        D.append(round(next_D))
        CD.append(round(next_CD))
        if (next_I <= 0): break
        
    return np.stack([S, E, I, R, H, D, CD]).T

"""
Graphics
"""

TEMPLATE = "plotly_white"
_SUSCEPTIBLE_COLOR = "rgba(230,230,230,.4)"
_RECOVERED_COLOR = "rgba(180,200,180,.4)"

COLOR_MAP = {
    "default": "#262730",
    "pink": "#E22A5B",
    "purple": "#985FFF",
    "susceptible": _SUSCEPTIBLE_COLOR,
    "recovered": _RECOVERED_COLOR,} 

def _set_legends(fig):
    fig.layout.update(legend=dict(x=-0.1, y=1.2))
    fig.layout.update(legend_orientation="h")


def plot_historical_data(df):
    fig = px.line(
        df, x="Date", y="Number", color="Status", template=TEMPLATE
    )
    
    fig.layout.update(
        xaxis_title="Date",
        font=dict(family="Arial", size=12))
    
    _set_legends(fig)

    return fig


def num_beds_occupancy_comparison_chart(num_beds_available, max_num_beds_needed):
    """
    A horizontal bar chart comparing # of beds available compared to 
    max number number of beds needed
    """
    num_beds_available, max_num_beds_needed = (
        int(num_beds_available),
        int(max_num_beds_needed),
    )

    df = pd.DataFrame(
        {
            "Label": ["Total Beds ", "Peak Occupancy "],
            "Value": [num_beds_available, max_num_beds_needed],
            "Text": [f"{num_beds_available:,}  ", f"{max_num_beds_needed:,}  "],
            "Color": ["b", "r"],
        }
    )
    fig = px.bar(
        df,
        x="Value",
        y="Label",
        color="Color",
        text="Text",
        orientation="h",
        opacity=0.7,
        template=TEMPLATE,
        height=300,
    )

    fig.layout.update(
        showlegend=False,
        xaxis_title="",
        xaxis_showticklabels=False,
        yaxis_title="",
        yaxis_showticklabels=True,
        font=dict(family="Arial", size=15, color=COLOR_MAP["default"]),
    )
    fig.update_traces(textposition="outside", cliponaxis=False)

    return fig
