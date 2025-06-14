# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16OG_wjgUZFfo0muTGBuSWJAFoxdXZaJo
"""

# Add code for Spearman's ranking coefficient and generate plots

import math as mt
from math import pi as pi
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats


'''
units = {
      'Volume of tank': 'm3',
      'Volume of clarifier': 'm3',
      'Area of clarifier': 'm2',
      'Area of filter': 'm2'
      'Volume of wall concrete': 'm3',
      'Volume of slab concrete': 'm3',
      'Amount of reinforcing steel': 'kg',
      'Area of slab': 'm2',
      'Pump power': 'kW',
      'Blower power': 'KW',
      'Pipe length': 'm',
      'Sludge solids': 'kg',
      'Methanol': 'kg'
      }
'''

# Estimating backwash and bump water requirements for denitrification filter
def filter(a, HAR, phase=''):
  air_flowrate = air_backwash_rate * a # Backwash air flowrate per filter, m3/hr.
  water_flowrate = water_backwash_rate * a # Backwash water flowrate per filter, m3/hr.
  vol_backwash_water = water_flowrate * backwash_duration * (n_filters-1) * backwash_freq/60 # Total volume for backwash water required, for backwashing 4 filters for 15 mins once every day, m3/day.
  vol_bump_water = a * (n_filters-1) * bump_water_flush_rate * bump_water_duration * bump_water_freq * 24/60 # Total volume of bump water required, for bumping 4 filter for 4 mins, once every 3 hours, m3/day.
  if phase == 'w': return round(vol_backwash_water + vol_bump_water, 2)
  elif phase =='a': return round(air_flowrate, 2)

# Computing concrete and steel requirements for each unit
def const_mat(ID='', L=0., W=0., SWD=0., d=0., s=0.):
# For anoxic and aerobic zones
    if L !=0. :
        t_w = (1 + max(SWD-12, 0)/12)*0.3048 # 1 ft + 1 inch added for eevry ft greater then 12ft.
        t_s = t_w + (2/12)*0.3048 # 2 inches more than t_w
        V_sw = 2 * W * t_w * (SWD + FB)
        V_lw = 2 * (L + 2*t_w) * t_w * (SWD+FB)
        V_c_s = V_s = (L + 2*t_w) * (W + 2*t_w) * t_s
        V_c_w = V_sw + V_lw
        V_c_t = V_c_s + V_c_w
        M_steel = 77.58 * V_c_t
        return V_c_w, V_c_s, M_steel, V_c_s/t_s
# For secondary clarifier
    elif d !=0. :
        t_w = (1 + max(SWD-12, 0)/12)*0.3048 # 1 ft + 1 inch added for eevry ft greater then 12ft.
        t_s = t_w + (2/12)*0.3048 # 2 inches more than t_w
        V_c_w = V_cy = pi * ((d + 2*t_w)**2 - d**2) * (FB + SWD)/4
        V_c_s = V_s = pi * (d + 2*t_w)**2 * t_s/4
        V_c_t = V_c_s + V_c_w
        M_steel = 77.58 * V_c_t
        return V_c_w, V_c_s, M_steel, V_c_s/t_s
#For denitrification tank
    elif s !=0. :
        t_w = (1 + max(SWD-12, 0)/12)*0.3048 # 1 ft + 1 inch added for eevry ft greater then 12ft.
        t_s = t_w + (2/12)*0.3048 # 2 inches more than t_w
        V_c_w = V_w = 4 * (s + t_w) * t_w * (SWD + FB)
        V_c_s = V_s = (s + 2*t_w)**2 * t_s
        V_c_t = V_c_s + V_c_w
        M_steel = 77.58 * V_c_t
        return V_c_w, V_c_s, M_steel, V_c_s/t_s

# Computing dimensions of each unit
def dimension(conf='', ID='', L_to_W=5):
  if ID.startswith('a'):
    if conf == 'MLE':
      if ID == 'anoxic': HRT = 1
      elif ID == 'aerobic': HRT = 6
    elif conf == 'Bardenpho':
      if ID == 'anoxic_1': HRT = 3
      elif ID == 'aerobic_1': HRT = 15.5
      elif ID == 'anoxic_2': HRT = 2
      elif ID == 'aerobic_2': HRT = 0.5
    V = Q * HRT/24
    A = V/SWD_tank
    W = W_to_D * SWD_tank
    L = max(A/W, L_to_W * W)
    if conf == 'MLE': MLE['pipe'] += 2 * 2 * L # 2L is to account for IR pipe (aerobic to anoxic) and RAS (clarifier to anoxic) pipe. x2 accounts for the redundant train.
    elif conf == 'Bardenpho':
      if ID == 'anoxic_1' or ID == 'aerobic_1': Bardenpho['pipe'] += 2 * 2 * L # 2L is to account for IR pipe (aerobic_1 to anoxic_1) and RAS (clarifier to anoxic) pipe. x2 accounts for the redundant train.
      else: Bardenpho['pipe'] += 2 * L # To account for RAS pipe for the 2nd anoxic-aerobic zones. x2 accounts for the redundant train.
    V_c_w, V_c_s, M_steel, A_slab = const_mat(L=L, W=W, SWD=SWD_tank)
    return round(V,2), round(2*V_c_w,2), round(2*V_c_s,2), round(2*M_steel,2), round(2*A_slab,2)
  elif ID.startswith('c'):
    A = Q/SOR
    d = mt.sqrt(4 * A/pi)
    if conf == 'MLE': MLE['pipe'] += 2 * d/2 # To account for RAS pipe starting from bottom of the clarifier center. x2 accounts for the redundant train.
    elif conf == 'Bardenpho': Bardenpho['pipe'] += 2 * d/2 # To account for RAS pipe starting from bottom of the clarifier center. x2 accounts for the redundant train.
    if d <= 21: SWD = 3.7
    elif d > 21 and d <= 30: SWD = 4
    elif d > 30 and d <= 43: SWD = 4.3
    elif d > 43: SWD = 4.6
    V_c_w, V_c_s, M_steel, A_slab = const_mat(d=d, SWD=SWD)
    V = A * SWD
    return round(V,2), round(2*V_c_w,2), round(2*V_c_s,2), round(2*M_steel,2), round(2*A_slab,2)
  elif ID.startswith('d'):
    SWD = 0.45 + 2 + 1.53 # supporting media + fitler media + hydraulic head, m.
    A = Q/(24 * HAR)
    a = A/(n_filters-1)
    L = mt.sqrt(a)
    V_c_w, V_c_s, M_steel, A_slab = const_mat(s=L, SWD=SWD)
    MLE['denitrification tank']['A_total'] = round(a*n_filters, 2)
    return round(a,2), round(n_filters*V_c_w,2), round(n_filters*V_c_s,2), round(n_filters*M_steel,2), round(n_filters*A_slab,2)

# Estimating pump power
def pump_power(Q, ratio):
  return (Q * ratio * rho_water * g * H_pump)/(24 * 60 * 60 * pump_effic * 1000)

def pump(pump_config):
  if pump_config == 'MLE':
    ir_pump_power = pump_power(Q, ir)
    r_pump_power = pump_power(Q, r)
    Q_bw = filter(MLE['denitrification tank']['a_single'], HAR, phase='w')
    bw_pump_power = pump_power(Q_bw, 1)
    was_pump_power = pump_power(WAS, SG_sludge)
    meth_pump_power = pump_power(Q_methanol, SG_methanol)
    return round(ir_pump_power,2), round(r_pump_power,2), round(bw_pump_power,2), round(was_pump_power,2), round(meth_pump_power,2)
  elif pump_config == 'Bardenpho':
    ir_pump_power = pump_power(Q, ir)
    r_pump_power = pump_power(Q, r)
    was_pump_power = pump_power(WAS, SG_sludge)
    meth_pump_power = pump_power(Q_methanol, SG_methanol)
    return round(ir_pump_power,2), round(r_pump_power,2), round(was_pump_power,2), round(meth_pump_power,2)

# Estimating blower power
def blower(air_flow):
  air_flow = air_flow * rho_air
  blower_power = ((P2/P1)**n - 1) * air_flow * 8.314 * T1 / (28.97 * n * blower_effic)
  return round(blower_power, 2)

# Estimating the weight of sludge solids produced daily
def solids(weight, rate):
  solids = round(weight * rate/1000, 2) # Mass of solids in kg.
  return solids

def calculate_total_amounts(system_name, system, amounts):
    for key in system:
        if key not in {'pumps', 'pipe', 'blower', 'sludge solids'}:
            amounts['V_c_w'] += system[key]['V_c_w']
            amounts['V_c_s'] += system[key]['V_c_s']
            amounts['M_steel'] += system[key]['M_steel']
            amounts['A_slab'] += system[key]['A_slab']
        if key == 'pumps':
            amounts['num_pumps'] = len(system[key])
            amounts['num_pumps_const'] = len(system[key])
            for pump in system[key]:
                if pump != 'bw_power':
                    amounts['num_pumps_const'] += 1
        if key == 'blower':
            amounts['num_blower'] = len(system[key])
            amounts['num_blower_const'] = len(system[key])
            for blower in system[key]:
                if blower != 'dnf_blower':
                    amounts['num_blower_const'] += 1

    amounts['solid_management'] = 365 * system["sludge solids"]
    amounts['methanol'] += Q_methanol * SG_methanol * rho_water * 365
    amounts['pipe'] += system['pipe']
    for key in system['pumps']:
        amounts['electricity'] += op_hours * system['pumps'][key]
    for key in system['blower']:
        amounts['electricity'] += op_hours * system['blower'][key]
    if system_name == 'MLE':
        amounts['filter_media'] = system['denitrification tank']['a_single'] * n_filters * 2
        amounts['filter_support'] = system['denitrification tank']['a_single'] * n_filters * .45
        amounts['electricity'] += op_hours * system['pumps']['bw_power']

def calculate_capital_cost(amounts, unit_costs):
    capital_cost_PV = unit_costs['wall_conc'] * amounts['V_c_w']
    capital_cost_PV += unit_costs['slab_conc'] * amounts['A_slab']
    capital_cost_PV += unit_costs['steel'] * amounts['M_steel']
    capital_cost_PV += unit_costs['pipe'] * amounts['pipe']
    capital_cost_PV += unit_costs['pump'] * amounts['num_pumps']
    capital_cost_PV += unit_costs['blower'] * amounts['num_blower']
    if 'filter_media' in amounts:
        capital_cost_PV += unit_costs['filter_media'] * amounts['filter_media']
        capital_cost_PV += unit_costs['filter_support'] * amounts['filter_support']
    return capital_cost_PV

def calculate_replacement_cost(amounts, unit_costs, yr):
    replace_cost_PV = unit_costs['pump'] * amounts['num_pumps'] / (1 + interest_rate) ** yr
    replace_cost_PV += unit_costs['blower'] * amounts['num_blower'] / (1 + interest_rate) ** yr
    return replace_cost_PV

def calculate_operating_cost(amounts, unit_costs):
    operate_cost = unit_costs['methanol'] * amounts['methanol']
    operate_cost += unit_costs['electricity'] * amounts['electricity']
    operate_cost += unit_costs['solid_management'] * amounts['solid_management']
    return operate_cost

def calculate_impacts(data, config_type):
    total_hours = 24 * 365
    n2o_emission_factor = unit_impacts['n2O_emission_M'] if config_type == 'MLE' else unit_impacts['n2O_emission_B']
    N_eff = N_eff_MLE if config_type == 'MLE' else N_eff_Bardenpho
    BOD_eff = BOD_eff_MLE if config_type == 'MLE' else BOD_eff_Bardenpho
    construction_impact = {
        'wall_concrete': data['V_c_w'] * unit_impacts['wall_concrete'],
        'slab_concrete': data['A_slab'] * unit_impacts['slab_concrete'],
        'pipe': data['pipe'] * unit_impacts['pipe'],
        'dnf_filter_media': data.get('filter_media', 0) * density_of_filter_media * unit_impacts['dnf_media'],
        'dnf_supporting_media': data.get('filter_support', 0) * density_of_supporting_media * unit_impacts['dnf_media'],
        'transport': ((data['V_c_w'] + data['V_c_s']) * density_of_concrete + data['M_steel'] * density_of_steel) / 1000 * unit_impacts['transport'] * transportation_distance
    }
    operation_impact = {
        'electricity': data['electricity'] * unit_impacts['electricity'] * total_hours,
        'transportation_Sludge': data['solid_management'] / 1000 * transportation_distance * unit_impacts['transport'] * 365,
        'land_application_sludge': data['solid_management'] * unit_impacts['land application of sludge'] * 365,
        'methanol': data['methanol'] * unit_impacts['methanol'] * 365,
        'N2O_emission': (N_inf - N_eff) * Q / 1000 * 365 * n2o_emission_factor,
        'methane_emissions': (BOD_inf - BOD_eff) * Q / 1000 * unit_impacts['methane_emissions'] * 365
    }
    return {'construction': construction_impact, 'operation': operation_impact}

# Function to Calculate Total Impact
def calculate_total_impact(impacts):
    total_impact = {
        'MLE': {
            'total_construction': round(sum(impacts['MLE']['construction'].values()),2),
            'total_operation': round(sum(impacts['MLE']['operation'].values()),2)
        },
        'Bardenpho': {
            'total_construction': round(sum(impacts['Bardenpho']['construction'].values()),2),
            'total_operation': round(sum(impacts['Bardenpho']['operation'].values()),2)
        },
    }
    return total_impact

# For plotting separated box plots
mle_const_costs = []
mle_op_costs = []
bardenpho_const_costs = []
bardenpho_op_costs = []
mle_const_impacts = []
mle_op_impacts = []
bardenpho_const_impacts = []
bardenpho_op_impacts = []

# For plotting total costs and impacts
mle_results = {
    'costs': [],
    'impacts': []
}
bardenpho_results = {
    'costs': [],
    'impacts': []
}

# Uncertainty analysis
for i in range(1000):
    # Design combinations for DO, WAS, Q_methanol from GPS-X
    MLE_design_comb = [(2, 3232.74, 4.5)]
    Bardenpho_design_comb = [(2, 3232.74, 0)]
    # Influent wastewater characteristics
    Q = 85.4 * 3785.4118 # MGD to m3/day.
    N_inf = 36 # Influent N concentration, mg/L.
    BOD_inf = 273.5 # Influent BOD concentration, mg/L.
    # Effluent wastewater charcateristics
    N_eff_MLE =  6 # Effluent N concentration, mg/L.
    N_eff_Bardenpho =  4 # Effluent N concentration, mg/L.
    BOD_eff_MLE = 20 # Effluent BOD concentration, mg/L.
    BOD_eff_Bardenpho = 3 # Effluent BOD concentration, mg/L.
    # Bioreactor parameters
    SWD_tank = np.random.uniform(4.5, 7.5) # Side water depth of bioreactor tanks, m.
    FB = np.random.uniform(0.3, 0.6) # Freeboard, m.
    W_to_D = np.random.triangular(1, 1.5, 2.2) # Width:depth ratio.
    SOTE = np.random.uniform(6, 15) # Oxygen transfer efficiency in %.
    # Secondary clarifier parameters
    SOR = np.random.uniform(24, 32) # Surface overflow rate, m3/day/m2.
    # Sludge characteristics
    w_sl_solids = np.random.triangular(82, 98, 130) # Weight of sludge solids, kg/ 1000 m3.
    SG_sludge = 1.05 # Specific gravity of sludge, to calculate WAS pump power.
    # Pump parameters
    r = np.random.uniform(0.5, 0.75) # Recycle ratio for RAS.
    rho_water = 1000 # Density of water, kg/m3.
    g = 9.81 # m/s2.
    pump_effic = np.random.uniform(0.6, 0.75) # As decimal.
    H_pump = 0.3 # Static head, m.
    ir = 1.5 # Internal recycle ratio.
    op_hours = 8760 # Operating hours, assuming 24 hours of operation per day, for 365 days.
    # Methanol parameters
    SG_methanol = 0.7917 # Specific gravity of methanol at 20 C.
    # Blower constants abd parameters
    C = 28.97 # Molecular weight of dry air
    R = 8.314  # Engineering gas constant for air, in J/mol K.
    T1 = 20 # Temperature, degrees Celcius.
    P2 = 1.532 # atm, atmospheric temperature + water pressure.
    P1 = 1 # atm, atmospheric temperature.
    n = 0.283  # (k-1)/k for air.
    rho_air = 1.204 # Density of air at 20 C, kg/m3.
    blower_effic = np.random.uniform(0.7, 0.9) # As decimal.
    # Denitrification filter parameters
    n_filters = 5 # Number of denitrification filter tanks, 1 standby
    HAR = np.random.uniform(2.4, 4.8) # Hydraulic application rate, m/hr.
    water_backwash_rate = np.random.uniform(14, 22) # Water backwash rate per backwash, m3/hr/m2.
    air_backwash_rate = np.random.uniform(72, 96) # Air backwash rate per backwash, m3/hr/m2.
    backwash_duration = 15 # Duration of backwash per backwash, mins.
    backwash_freq = 1 # Number of backwash per day per filter.
    bump_water_flush_rate = np.random.uniform(10, 14) # m3/m2/hr.
    bump_water_duration = 4 # mins per bump.
    bump_water_freq = 1 # Number of bumps every 3 hours per filter.
    # Cost calculation constants
    interest_rate = np.random.uniform(0.04, 0.06) # Discount rate.
    project_lifetime = 50 # Design life of the system, years.
    mech_lifetime = 15 # Lifetime of pumps and blower, years.
    # Unit costs
    unit_costs = {
        'wall_conc': np.random.uniform(400.23 * 0.8, 400.23 * 1.2), # $/m3
        'slab_conc': np.random.uniform(93.27 * 0.8, 93.27 * 1.2), # $/m2
        'steel': np.random.uniform(1.73 * 0.8, 1.73 * 1.2), # $/kg
        'electricity': np.random.lognormal(0.09561, 0.025), # $/kWh
        'solid_management': np.random.uniform(0.3, 0.8), # $/kg
        'filter_media': np.random.uniform(38.37, 57.55), # $/m3
        'filter_support': np.random.uniform(35.63, 53.45), # $/m3
        'methanol': np.random.uniform(0.327, 0.366), # $/kg
        'pipe': 40/3.28, # $/m
        'pump': 5000, # each
        'blower': 7000 # each
    }
    # Unit impacts
    unit_impacts = {
        'wall_concrete': np.random.uniform(579.243 * 0.8, 579.243 * 1.2), # kg CO2-eq/m3
        'slab_concrete': np.random.uniform(390.285 * 0.8, 390.285 * 1.2), # kg CO2-eq/m2
        'electricity': np.random.uniform(0.561 * 0.8, 0.561 * 1.2), # kg CO2-eq/kWh
        'methanol': np.random.uniform(1.259 * 0.8, 1.259 * 1.2), # kg CO2-eq/kg
        'pipe': np.random.uniform(3.569 * 0.8, 3.569 * 1.2), # kg CO2-eq/m
        'dnf_media': np.random.uniform(0.022 * 0.8, 0.022 * 1.2), # kg CO2-eq/kg
        'transport': np.random.uniform(1.077 * 0.8, 1.077 * 1.2), # kg CO2-eq/ton/km
        'n2O_emission_B': np.random.uniform(0.0036 * 0.8, 0.0036 * 1.2) * 1.571 * 265, # kg CO2-eq/kg N
        'n2O_emission_M': np.random.uniform(0.00065 * 0.8, 0.00065 * 1.2) * 1.571 * 265, # kg CO2-eq/kg N
        'land application of sludge': np.random.uniform(0.010 * 0.8, 0.010 * 1.2) * 1.571 * 265, # kg CO2-eq/kg N
        'methane_emissions': np.random.uniform(0.018 * 0.8, 0.018 * 1.2) * 28 # kg CO2-eq/kg BOD
    }
    # Impact calculation constants
    density_of_supporting_media = 1800
    density_of_filter_media = 1600
    density_of_concrete = 2400
    density_of_steel = 7850
    transportation_distance = 50 # Assuming a transportation distance of 50 km

    MLE_sizings = {}
    Bardenpho_sizings = {}

    for design in MLE_design_comb:
      DO, WAS, Q_methanol = design
      MLE = {
          'anoxic': {'V': 0., 'V_c_w': 0., 'V_c_s': 0., 'M_steel': 0., 'A_slab':0.},
          'aerobic': {'V': 0., 'V_c_w': 0., 'V_c_s': 0., 'M_steel': 0., 'A_slab':0.},
          'clarfier': {'V': 0., 'V_c_w': 0., 'V_c_s': 0., 'M_steel': 0., 'A_slab':0.},
          'denitrification tank': {'a_single': 0., 'V_c_w': 0., 'V_c_s': 0., 'M_steel': 0., 'A_slab':0., 'A_total':0.,},
          'pumps': {'ir_power': 0., 'r_power': 0., 'bw_power': 0., 'WAS_power': 0., 'meth_power': 0.},
          'pipe': 0.,
          'blower': {'rx_blower': 0., 'dnf_blower': 0.},
          'sludge solids': 0.
      }
      for key in MLE:
        if key.startswith('a') or key.startswith('c'):
          MLE[key]['V'], MLE[key]['V_c_w'], MLE[key]['V_c_s'], MLE[key]['M_steel'], MLE[key]['A_slab'] = dimension(conf='MLE', ID=key)
        elif key.startswith('d'):
          MLE[key]['a_single'], MLE[key]['V_c_w'], MLE[key]['V_c_s'], MLE[key]['M_steel'], MLE[key]['A_slab'] = dimension(ID = key)
        elif key == 'pumps': MLE[key]['ir_power'], MLE[key]['r_power'], MLE[key]['bw_power'], MLE[key]['WAS_power'], MLE[key]['meth_power'] = pump('MLE')
        elif key == 'blower':
          RO = DO * Q/ (24 * 1000) # Required dissolved oxygen, converted to kg/hr.
          Q_air_rx = 6 * RO/SOTE # Required airflow rate, m3/s.
          MLE[key]['rx_blower'] = blower(Q_air_rx)
          Q_air_bw = filter(MLE['denitrification tank']['a_single'], HAR, phase='a')/ (24 * 60 * 60) # Backwash air flowrate in m3/s.
          MLE[key]['dnf_blower'] = blower(Q_air_bw)
        elif key == 'sludge solids':
          MLE[key] = solids(w_sl_solids, WAS)
      MLE['pipe'] *= 1.25 # Adding 25% to pipe length.
      MLE['pipe'] = round(MLE['pipe'], 2)
      MLE_sizings[design] = MLE

    for design in Bardenpho_design_comb:
      DO, WAS, Q_methanol = design
      Bardenpho = {
            'anoxic_1': {'V': 0., 'V_c_w': 0., 'V_c_s': 0., 'M_steel': 0., 'A_slab':0.},
            'aerobic_1': {'V': 0., 'V_c_w': 0., 'V_c_s': 0., 'M_steel': 0., 'A_slab':0.},
            'anoxic_2': {'V': 0., 'V_c_w': 0., 'V_c_s': 0., 'M_steel': 0., 'A_slab':0.},
            'aerobic_2': {'V': 0., 'V_c_w': 0., 'V_c_s': 0., 'M_steel': 0., 'A_slab':0.},
            'clarifier': {'V': 0., 'V_c_w': 0., 'V_c_s': 0., 'M_steel': 0., 'A_slab':0.},
            'pumps': {'ir_power': 0., 'r_power': 0., 'WAS_power':0., 'meth_power': 0.},
            'pipe': 0.,
            'blower': {'rx_blower': 0.},
            'sludge solids': 0.
      }
      for key in Bardenpho:
        if key.startswith('a') or key.startswith('c'):
          Bardenpho[key]['V'], Bardenpho[key]['V_c_w'], Bardenpho[key]['V_c_s'], Bardenpho[key]['M_steel'], Bardenpho[key]['A_slab'] = dimension('Bardenpho', key)
        elif key == 'pumps': Bardenpho[key]['ir_power'], Bardenpho[key]['r_power'], Bardenpho[key]['WAS_power'], Bardenpho[key]['meth_power']  = pump('Bardenpho')
        elif key == 'blower':
          RO = DO * Q/ (24 * 1000) # Required dissolved oxygen, converted to kg/hr.
          Q_air_rx = 6 * RO/SOTE # Required airflow rate, m3/s.
          Bardenpho[key]['rx_blower'] = blower(Q_air_rx)
        elif key == 'sludge solids':
          Bardenpho[key] = solids(w_sl_solids, WAS)
      Bardenpho['pipe'] *= 1.25 # Adding 25% to pipe length.
      Bardenpho['pipe'] = round(Bardenpho['pipe'], 2)
      Bardenpho_sizings[design] = Bardenpho

    print("--------------------------MLE DESIGNS--------------------------")
    for design in MLE_sizings:
      print("(DO, WAS, Methanol): ", design)
      for size in MLE_sizings[design]: print(size, ':', MLE_sizings[design][size])
      print('\n')
    print("--------------------------BARDENPHO DESIGNS--------------------------")
    for design in Bardenpho_sizings:
      print("(DO, WAS, Methanol): ", design)
      for size in Bardenpho_sizings[design]: print(size, ':', Bardenpho_sizings[design][size])
      print('\n')

    AN_given_PV_factor = interest_rate * (interest_rate * (1 + interest_rate) ** project_lifetime) / ((1 + interest_rate) ** project_lifetime - 1)
    total_costs = {'MLE':{}, 'Bardenpho':{}}
    total_amounts = {'MLE':{}, 'Bardenpho':{}}
    for design in MLE_design_comb:
        DO, WAS, Q_methanol = design
        MLE_amounts = {
            'V_c_w': 0., 'V_c_s': 0., 'A_slab': 0., 'M_steel': 0., 'methanol': 0.,
            'electricity': 0, 'solid_management': 0., 'filter_media': 0,
            'filter_support': 0., 'pipe': 0., 'num_pumps': 0, 'num_pumps_const': 0,
            'num_blower': 0, 'num_blower_const': 0
        }
        calculate_total_amounts('MLE', MLE_sizings[design], MLE_amounts)
        MLE_amounts = {k: round(v, 2) for k, v in MLE_amounts.items()}
        # Calculating costs
        capital_cost_PV = calculate_capital_cost(MLE_amounts, unit_costs)
        capital_cost_AN = capital_cost_PV * AN_given_PV_factor
        replacement_cost_AN = 0
        for yr in range(mech_lifetime, project_lifetime, mech_lifetime):
            replace_cost_PV = calculate_replacement_cost(MLE_amounts, unit_costs, yr)
            replacement_cost_AN += replace_cost_PV * AN_given_PV_factor
        operating_cost = calculate_operating_cost(MLE_amounts, unit_costs)
        total_costs['MLE'][design] = {
            'capital_cost': round(capital_cost_AN, 2),
            'replacement_cost': round(replacement_cost_AN, 2),
            'operating_cost': round(operating_cost, 2)
        }
        total_amounts['MLE'][design] = MLE_amounts

    for design in Bardenpho_design_comb:
        DO, WAS, Q_methanol = design
        Bardenpho_amounts = {
            'V_c_w': 0., 'V_c_s': 0., 'A_slab': 0., 'M_steel': 0., 'methanol': 0.,
            'electricity': 0, 'solid_management': 0., 'pipe': 0., 'num_pumps': 0,
            'num_pumps_const': 0, 'num_blower': 0, 'num_blower_const': 0
        }
        calculate_total_amounts('Bardenpho', Bardenpho_sizings[design], Bardenpho_amounts)
        Bardenpho_amounts = {k: round(v, 2) for k, v in Bardenpho_amounts.items()}
        # Calculating costs
        capital_cost_PV = calculate_capital_cost(Bardenpho_amounts, unit_costs)
        capital_cost_AN = capital_cost_PV * AN_given_PV_factor
        replacement_cost_AN = 0
        for yr in range(mech_lifetime, project_lifetime, mech_lifetime):
            replace_cost_PV = calculate_replacement_cost(Bardenpho_amounts, unit_costs, yr)
            replacement_cost_AN += replace_cost_PV * AN_given_PV_factor
        operating_cost = calculate_operating_cost(Bardenpho_amounts, unit_costs)
        total_costs['Bardenpho'][design] = {
            'capital_cost': round(capital_cost_AN, 2),
            'replacement_cost': round(replacement_cost_AN, 2),
            'operating_cost': round(operating_cost, 2)
        }
        total_amounts['Bardenpho'][design] = Bardenpho_amounts

    # Initialize dictionary to store impacts
    total_impacts = {'MLE': {}, 'Bardenpho': {}}
    for design in MLE_design_comb:
        DO, WAS, Q_methanol = design
        amounts = total_amounts['MLE'][design]
        MLE_impacts = calculate_impacts(amounts, 'MLE')
        total_impacts['MLE'][design] = {
            'construction': {k: round(v, 2) for k, v in MLE_impacts['construction'].items()},
            'operation': {k: round(v, 2) for k, v in MLE_impacts['operation'].items()},
            'total_construction': round(sum(MLE_impacts['construction'].values()), 2),
            'total_operation': round(sum(MLE_impacts['operation'].values()), 2)
        }
    for design in Bardenpho_design_comb:
        DO, WAS, Q_methanol = design
        amounts = total_amounts['Bardenpho'][design]
        Bardenpho_impacts = calculate_impacts(amounts, 'Bardenpho')
        total_impacts['Bardenpho'][design] = {
            'construction': {k: round(v, 2) for k, v in Bardenpho_impacts['construction'].items()},
            'operation': {k: round(v, 2) for k, v in Bardenpho_impacts['operation'].items()},
            'total_construction': round(sum(Bardenpho_impacts['construction'].values()), 2),
            'total_operation': round(sum(Bardenpho_impacts['operation'].values()), 2)
        }

    for decision_set in total_costs:
      print(decision_set)
      print("cost: ", total_costs[decision_set])
      print("impact: ", total_impacts[decision_set], "\n")

    # Initialize lists to store data for plotting
    mle_costs = []
    mle_impacts = []
    bardenpho_costs = []
    bardenpho_impacts = []
    # Extract the data for MLE
    for design in total_costs['MLE']:
        mle_total_cost = (total_costs['MLE'][design]['capital_cost'] +
                          total_costs['MLE'][design]['replacement_cost'] +
                          total_costs['MLE'][design]['operating_cost'])
        mle_total_impact = (total_impacts['MLE'][design]['total_construction'] +
                            total_impacts['MLE'][design]['total_operation'])
        mle_costs.append(mle_total_cost/10E3)
        mle_impacts.append(mle_total_impact/10E6)
    # Extract the data for Bardenpho
    for design in total_costs['Bardenpho']:
        bardenpho_total_cost = (total_costs['Bardenpho'][design]['capital_cost'] +
                              total_costs['Bardenpho'][design]['replacement_cost'] +
                              total_costs['Bardenpho'][design]['operating_cost'])
        bardenpho_total_impact = (total_impacts['Bardenpho'][design]['total_construction'] +
                                total_impacts['Bardenpho'][design]['total_operation'])
        bardenpho_costs.append(bardenpho_total_cost/10E3)
        bardenpho_impacts.append(bardenpho_total_impact/10E6)

    # Store results for MLE and Bardenpho for box plots for total costs and impacts
    for design in total_costs['MLE']:
        mle_total_cost = (total_costs['MLE'][design]['capital_cost'] +
                         total_costs['MLE'][design]['replacement_cost'] +
                         total_costs['MLE'][design]['operating_cost'])
        mle_total_impact = (total_impacts['MLE'][design]['total_construction'] +
                           total_impacts['MLE'][design]['total_operation'])
        mle_results['costs'].append(mle_total_cost/1e3)  # Convert to thousands
        mle_results['impacts'].append(mle_total_impact/1e6)  # Convert to millions
    for design in total_costs['Bardenpho']:
        bardenpho_total_cost = (total_costs['Bardenpho'][design]['capital_cost'] +
                              total_costs['Bardenpho'][design]['replacement_cost'] +
                              total_costs['Bardenpho'][design]['operating_cost'])
        bardenpho_total_impact = (total_impacts['Bardenpho'][design]['total_construction'] +
                                total_impacts['Bardenpho'][design]['total_operation'])
        bardenpho_results['costs'].append(bardenpho_total_cost/1e3)
        bardenpho_results['impacts'].append(bardenpho_total_impact/1e6)

    # Extract and store data for separated box plots for MLE and Bardenpho
    for design in total_costs['MLE']:
        mle_const_costs.append((total_costs['MLE'][design]['capital_cost'] +
                              total_costs['MLE'][design]['replacement_cost'])/1e3)
        mle_op_costs.append(total_costs['MLE'][design]['operating_cost']/1e3)
        mle_const_impacts.append(total_impacts['MLE'][design]['total_construction']/1e6)
        mle_op_impacts.append(total_impacts['MLE'][design]['total_operation']/1e6)
    for design in total_costs['Bardenpho']:
        bardenpho_const_costs.append((total_costs['Bardenpho'][design]['capital_cost'] +
                                    total_costs['Bardenpho'][design]['replacement_cost'])/1e3)
        bardenpho_op_costs.append(total_costs['Bardenpho'][design]['operating_cost']/1e3)
        bardenpho_const_impacts.append(total_impacts['Bardenpho'][design]['total_construction']/1e6)
        bardenpho_op_impacts.append(total_impacts['Bardenpho'][design]['total_operation']/1e6)

plt.style.use('default')
colors = ['#3498db', '#2ecc71'] # Blue for MLE, Green for Bardenpho

# Box plots for costs
plt.figure(figsize=(10,8))
data = [mle_results['costs'], bardenpho_results['costs']]
bp1 = plt.boxplot(data, labels=['MLE', 'Bardenpho'],
                 patch_artist=True,
                 medianprops=dict(color="black", linewidth=1.5),
                 flierprops=dict(marker='o', markerfacecolor='gray', markersize=8),
                 widths=0.7)
for patch, color in zip(bp1['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
plt.ylabel('Total Cost (Thousand USD/year)', fontsize=12, fontweight='bold')
plt.xlabel('Treatment Configuration', fontsize=12, fontweight='bold')
plt.title('Cost Distribution Comparison', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(fontsize=10, fontweight='bold')
plt.yticks(fontsize=10)

# Box plots for impacts
plt.figure(figsize=(10,8))
data = [mle_results['impacts'], bardenpho_results['impacts']]
bp2 = plt.boxplot(data, labels=['MLE', 'Bardenpho'],
                 patch_artist=True,
                 medianprops=dict(color="black", linewidth=1.5),
                 flierprops=dict(marker='o', markerfacecolor='gray', markersize=8),
                 widths=0.7)
for patch, color in zip(bp2['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
plt.ylabel('Total Impact (Million kg CO2-eq./year)', fontsize=12, fontweight='bold')
plt.xlabel('Treatment Configuration', fontsize=12, fontweight='bold')
plt.title('Environmental Impact Distribution Comparison', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(fontsize=10, fontweight='bold')
plt.yticks(fontsize=10)



# Box plot for separated costs
plt.figure(figsize=(12, 8))
bp1_const = plt.boxplot([mle_const_costs, bardenpho_const_costs],
                        positions=[1, 2],
                        patch_artist=True,
                        boxprops=dict(facecolor='lightblue', alpha=0.7))
bp1_op = plt.boxplot([mle_op_costs, bardenpho_op_costs],
                     positions=[1.35, 2.35],
                     patch_artist=True,
                     boxprops=dict(facecolor='lightgreen', alpha=0.7))
plt.ylabel('Cost (Thousand USD/year)', fontsize=12, fontweight='bold')
plt.title('Cost Distribution Comparison', fontsize=14, fontweight='bold', pad=20)
plt.xticks([1, 2], ['MLE', 'Bardenpho'], fontsize=10, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend([bp1_const["boxes"][0], bp1_op["boxes"][0]],
           ['Construction & Replacement', 'Operation'],
           loc='upper right')

# Box plot for separated impacts
plt.figure(figsize=(12, 8))
bp2_const = plt.boxplot([mle_const_impacts, bardenpho_const_impacts],
                        positions=[1, 2],
                        patch_artist=True,
                        boxprops=dict(facecolor='lightblue', alpha=0.7))
bp2_op = plt.boxplot([mle_op_impacts, bardenpho_op_impacts],
                     positions=[1.35, 2.35],
                     patch_artist=True,
                     boxprops=dict(facecolor='lightgreen', alpha=0.7))
plt.ylabel('Impact (Million kg CO2-eq./year)', fontsize=12, fontweight='bold')
plt.title('Environmental Impact Distribution Comparison',
              fontsize=14, fontweight='bold', pad=20)
plt.xticks([1, 2], ['MLE', 'Bardenpho'], fontsize=10, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend([bp2_const["boxes"][0], bp2_op["boxes"][0]],
           ['Construction', 'Operation'],
           loc='upper right')

plt.tight_layout()
plt.show()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

# Example data: Sensitivity input variables and their simulated dependent values
np.random.seed(42)  # For reproducibility

# Example inputs
data = {
    'Volume of tank': np.random.uniform(50, 150, 100),
    'Volume of clarifier': np.random.uniform(40, 120, 100),
    'Area of clarifier': np.random.uniform(20, 60, 100),
    'Area of filter': np.random.uniform(10, 50, 100),
    'Volume of wall concrete': np.random.uniform(30, 90, 100),
    'Volume of slab concrete': np.random.uniform(15, 45, 100),
    'Amount of reinforcing steel': np.random.uniform(200, 500, 100),
    'Pipe length': np.random.uniform(100, 300, 100),
    'Pump power': np.random.uniform(5, 20, 100),
    'Blower power': np.random.uniform(10, 30, 100),
    'Dependent variable (e.g., Total Cost)': np.random.uniform(500, 1500, 100)
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Compute Spearman correlation coefficients
correlations = {}
for col in df.columns[:-1]:  # Exclude the dependent variable from the loop
    coef, _ = spearmanr(df[col], df['Dependent variable (e.g., Total Cost)'])
    correlations[col] = coef

# Sort correlations by absolute values
sorted_correlations = dict(sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True))

# Prepare data for the tornado plot
variables = list(sorted_correlations.keys())
coefficients = list(sorted_correlations.values())

# Plot tornado chart
plt.figure(figsize=(10, 6))
bars = plt.barh(variables, coefficients, color=np.where(np.array(coefficients) > 0, '#3498db', '#e74c3c'), alpha=0.8)
plt.axvline(0, color='gray', linestyle='--', linewidth=1)
plt.xlabel("Spearman Correlation Coefficient", fontsize=12, fontweight='bold')
plt.ylabel("Input Variables", fontsize=12, fontweight='bold')
plt.title("Spearman Ranking Tornado Plot", fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='x', linestyle='--', alpha=0.6)

# Add bar labels
for bar in bars:
    width = bar.get_width()
    plt.text(width + np.sign(width) * 0.02, bar.get_y() + bar.get_height() / 2,
             f'{width:.2f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

# Example data: Sensitivity input variables and their simulated dependent values
np.random.seed(42)  # For reproducibility

# Example inputs (separating LCC and LCA-related variables)
data = {
    # LCC-related variables
    'Volume of tank (LCC)': np.random.uniform(50, 150, 100),
    'Pipe length (LCC)': np.random.uniform(100, 300, 100),
    'Pump power (LCC)': np.random.uniform(5, 20, 100),
    'Blower power (LCC)': np.random.uniform(10, 30, 100),
    'Concrete cost (LCC)': np.random.uniform(30, 90, 100),

    # LCA-related variables
    'Volume of wall concrete (LCA)': np.random.uniform(30, 90, 100),
    'Volume of slab concrete (LCA)': np.random.uniform(15, 45, 100),
    'Steel amount (LCA)': np.random.uniform(200, 500, 100),
    'Methanol usage (LCA)': np.random.uniform(10, 50, 100),
    'Electricity usage (LCA)': np.random.uniform(300, 1000, 100),

    # Dependent variables
    'Dependent variable (LCC)': np.random.uniform(500, 1500, 100),
    'Dependent variable (LCA)': np.random.uniform(50, 200, 100)
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Compute Spearman correlation coefficients for LCC and LCA
correlations_lcc = {}
correlations_lca = {}

# Compute LCC correlations
for col in df.columns[:-2]:  # Exclude the dependent variables
    if '(LCC)' in col:
        coef, _ = spearmanr(df[col], df['Dependent variable (LCC)'])
        correlations_lcc[col] = coef

# Compute LCA correlations
for col in df.columns[:-2]:
    if '(LCA)' in col:
        coef, _ = spearmanr(df[col], df['Dependent variable (LCA)'])
        correlations_lca[col] = coef

# Sort correlations by absolute values
sorted_correlations_lcc = dict(sorted(correlations_lcc.items(), key=lambda x: abs(x[1]), reverse=True))
sorted_correlations_lca = dict(sorted(correlations_lca.items(), key=lambda x: abs(x[1]), reverse=True))

# Prepare data for the tornado plots
variables_lcc = list(sorted_correlations_lcc.keys())
coefficients_lcc = list(sorted_correlations_lcc.values())

variables_lca = list(sorted_correlations_lca.keys())
coefficients_lca = list(sorted_correlations_lca.values())

# Plot LCC tornado chart
plt.figure(figsize=(10, 6))
bars_lcc = plt.barh(variables_lcc, coefficients_lcc, color=np.where(np.array(coefficients_lcc) > 0, '#3498db', '#e74c3c'), alpha=0.8)
plt.axvline(0, color='gray', linestyle='--', linewidth=1)
plt.xlabel("Spearman Correlation Coefficient (LCC)", fontsize=12, fontweight='bold')
plt.ylabel("LCC Input Variables", fontsize=12, fontweight='bold')
plt.title("Spearman Ranking Tornado Plot for LCC", fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='x', linestyle='--', alpha=0.6)

# Add bar labels for LCC
for bar in bars_lcc:
    width = bar.get_width()
    plt.text(width + np.sign(width) * 0.02, bar.get_y() + bar.get_height() / 2,
             f'{width:.2f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()

# Plot LCA tornado chart
plt.figure(figsize=(10, 6))
bars_lca = plt.barh(variables_lca, coefficients_lca, color=np.where(np.array(coefficients_lca) > 0, '#2ecc71', '#e74c3c'), alpha=0.8)
plt.axvline(0, color='gray', linestyle='--', linewidth=1)
plt.xlabel("Spearman Correlation Coefficient (LCA)", fontsize=12, fontweight='bold')
plt.ylabel("LCA Input Variables", fontsize=12, fontweight='bold')
plt.title("Spearman Ranking Tornado Plot for LCA", fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='x', linestyle='--', alpha=0.6)

# Add bar labels for LCA
for bar in bars_lca:
    width = bar.get_width()
    plt.text(width + np.sign(width) * 0.02, bar.get_y() + bar.get_height() / 2,
             f'{width:.2f}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()