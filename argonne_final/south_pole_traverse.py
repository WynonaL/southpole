"""
South Pole Logistics Emisssions Calculator Module

This module provides a set of functions designed to calculate the emissions from different modes of transport
under various conditions. It is aimed at evaluating environmental impacts of transporting goods via trucks,
tankers, and other vehicles, as well as from fuel consumption and production of renewable energy components to the South Pole.

Author: Wynona Lam
Role: SULI Intern
Date: April 2024

Repository with Paper: [GitHub Repository](https://github.com/WynonaL/southpole)

Functions:
- calculate_truck_emissions(miles, cargo_weight_in_tons, quantity): Calculates the emissions from a truck
  carrying cargo over a specified distance for a specified number of round trips.
  
- calculate_co2_equivalent(emissions_dictionary): Converts the emissions of different greenhouse gases into
  CO2 equivalents using global warming potentials over a 100-year timeline.
  
- calculate_tanker_emissions(miles, cargo_weight, number_of_tankers): Calculates emissions for ocean tankers
  over a round trip, considering both the loaded journey and the empty return.
  
- calculate_fuelused_emissions(miles_ocean_tanker, miles_truck): Estimates the combined emissions from fuel
  consumption for an ocean tanker and a truck.
  
- calculate_emissions_from_diesel(gallons_diesel): Calculates emissions resulting from the production of
  a specified amount of diesel fuel.
  
- embodied_renewable_emissions(target_solar, target_wind, target_bess_energy, target_diesel): Estimates
  the embodied emissions from the production of renewable energy components and diesel fuel.
  
- sum_emissions(*emission_dicts): Sums up emissions from multiple emission dictionaries into a single
  dictionary detailing total emissions for each pollutant.
  
- consolidate_scenario_emissions(transport_emissions, additional_emissions): Consolidates emissions data from
  various sources into total values for CO2, CH4, and N2O.
  
- transportation_scenario_emissions(target_solar, turbine_power, target_wind, target_bess_power,
  target_bess_energy, target_diesel): Calculates total emissions for transporting solar panels, wind turbines,
  battery storage units, and diesel based on assumed weight and transportation mode emissions.
"""


def calculate_truck_emissions(miles, cargo_weight_in_tons, quantity):
    """
    Calculate the emissions from a truck transporting cargo over a specified distance, 
    accounting for both loaded and empty trips.

    Parameters:
    - miles (float): The total distance of the round trip in miles.
    - cargo_weight_in_tons (float): The weight of the cargo in tons during the loaded trip.
    - quantity (int): The number of trips made.

    Returns:
    - dict: A dictionary containing the total emissions for CO2, CH4, and N2O in grams, 
            calculated over the specified number of round trips.

    Note:
    - This function calculates truck emissions based on energy intensity values for loaded and empty trips.
    - Energy intensity for the loaded trip is given in Btu per ton-mile, reflecting the energy used per ton of cargo per mile.
    - The energy consumption for the empty return trip is specified directly in Btu per mile.
    - Emissions are calculated using the Btu values converted to gallons of diesel burned per mile, then multiplied by the emissions factors for each pollutant per mmBtu of diesel consumed.
    - The function sums the emissions from the loaded and empty trips, then multiplies by the number of trips to give total emissions for the journey.

    Example:
    emissions = calculate_truck_emissions(1000, 20, 5)
    print("Total emissions for 5 round trips with 20 tons cargo over 1000 miles:")
    for pollutant, total in emissions.items():
        print(f"{pollutant}: {total} grams")
    """

    btu_per_gallon_diesel = 138700  # Btu per gallon of diesel (approximate, from EPS website)

    #Truck's energy intensity for the journey from origin to destination (Btu/ton-mile, per GREET)
    energy_intensity_truck_origin_to_destination = 684
    btu_per_mile_empty = 13567  # Btu/mile for the empty trip (given by GREET)

    #Emissions factors for the truck (grams per mmBtu, per GREET)
    emissions_factors_truck = {
        "CO2": 89.77044869,
        "CH4": 0.109408298,
        "N2O": 0.000355609
    }

    #Calculate BTU per mile for the loaded truck
    btu_per_mile_truck_origin_to_destination = energy_intensity_truck_origin_to_destination * cargo_weight_in_tons

    #Convert BTU per mile to gallons per mile for the loaded trip
    gallons_per_mile_truck_origin_to_destination = btu_per_mile_truck_origin_to_destination / btu_per_gallon_diesel

    #Use the btu_per_mile_empty for the empty trip
    gallons_per_mile_empty = btu_per_mile_empty / btu_per_gallon_diesel

    #Initialize a dictionary to hold total emissions for the trip
    total_emissions = {}

    #Calculate total emissions for the trip
    for emission, factor in emissions_factors_truck.items():
        #Emissions for the loaded trip to the destination
        emissions_origin_to_destination = factor * gallons_per_mile_truck_origin_to_destination * btu_per_gallon_diesel / 1e6 * miles
        #Emissions for the empty trip back to origin
        emissions_empty_back = factor * gallons_per_mile_empty * btu_per_gallon_diesel / 1e6 * miles
        #Sum up both emissions and multiply by the quantity of trips
        total_emissions[emission] = (emissions_origin_to_destination + emissions_empty_back) * quantity

    return total_emissions


def calculate_co2_equivalent(emissions_dictionary):
    """
    Calculate the CO2-equivalent emissions for given masses of CO2, CH4, and N2O over a 100-year timeline using AR6 Global Warming Potentials (GWP100).

    Parameters:
    - emissions (dict): Dictionary containing the mass of CO2, CH4, and N2O emissions in kilograms.
      The dictionary should have keys 'CO2', 'CH4', and 'N2O'.

    Returns:
    - float: The total CO2-equivalent emissions in kilograms.

    Note:
    - This function calculates CO2-equivalent emissions using the Global Warming Potentials (GWP100) from the AR6 report.
    - The GWP100 values used are 1 for CO2, 29.8 for CH4, and 273 for N2O.
    - CO2-equivalent emissions are calculated by multiplying the mass of each gas by its respective GWP100 value and summing the results.
    - The function returns the total CO2-equivalent emissions in kilograms.

    Example:
    emissions_data = {'CO2': 233759086.75851363, 'CH4': 1922227.9395642178, 'N2O': 4325.249834421531}
    total_co2_eq = calculate_co2_equivalent(emissions_data)
    print(total_co2_eq)  # Output: Total CO2-equivalent emissions for the given masses
    """
    
    co2_eq_co2 = emissions_dictionary['CO2'] * 1
    co2_eq_ch4 = emissions_dictionary['CH4'] * 29.8
    co2_eq_n2o = emissions_dictionary['N2O'] * 273
    total_co2_eq = co2_eq_co2 + co2_eq_ch4 + co2_eq_n2o

    return total_co2_eq


def calculate_tanker_emissions(miles, cargo_weight, number_of_tankers):
    """
    Calculate the total emissions for an ocean tanker transporting cargo, considering both the loaded and the empty return journeys.

    Parameters:
    - miles (float): Total one-way distance in miles that the tanker will travel.
    - cargo_weight (float): Weight of the cargo in tons that the tanker will carry on its loaded journey.
    - number_of_tankers (int): Number of tankers making the trip.

    Returns:
    - dict: A dictionary containing the cumulative emissions of CO2, CH4, and N2O in grams for the round trip, multiplied by the number of tankers.

    Note:
    - The function calculates emissions based on different fuel consumption rates when the tanker is loaded versus when it returns empty.
    - Energy intensity (Btu per ton-mile) is used for the loaded trip, and a reduced energy consumption (based on a load factor) is used for the empty trip.
    - Emissions are calculated using the Global Warming Potentials (GWP100) from the AR6 report, where CO2 is 1, CH4 is 0.293135661 grams per mmBtu, and N2O is 0.006037729 grams per mmBtu.
    - The function returns the total emissions for both the trip to the destination and the return trip, accounting for the number of tankers involved in the operation.

    Example:
    emissions = calculate_tanker_emissions(5000, 300, 2)
    print("Emissions for 2 tankers on a 5000-mile journey with 300 tons cargo:")
    for pollutant, emissions in emissions.items():
        print(f"{pollutant}: {emissions} grams")
    """

    btu_per_gallon_residual_oil = 149700  # Approximate Btu per gallon of residual oil (per Google, source: EPA [5])

    #Ocean tanker's energy intensity for the journey from origin to destination (Btu/ton-mile)
    energy_intensity_tanker_origin_to_destination = 43

    #Ocean tanker's load factor for the empty back-haul
    load_factor_tanker_back_haul = 0.70  # 70% of the hp is used

    #Hard-coded ocean tanker's horsepower and average speed
    hp_tanker = 19170  #Horsepower for the ocean tanker
    average_speed_tanker = 20  #Average speed in miles per hour for the ocean tanker (GREET)

    #Ocean tanker's energy consumption (Btu/hphr)
    energy_consumption_tanker = 5439

    #Emissions factors for the ocean tanker (grams per mmBtu)
    emissions_factors_tanker = {
        "CO2": 262.9991694,
        "CH4": 0.293135661,
        "N2O": 0.006037729
    }

    #Calculate BTU per mile for the loaded ocean tanker using Btu/ton-mile
    btu_per_mile_tanker_origin_to_destination = energy_intensity_tanker_origin_to_destination * cargo_weight

    #Calculate Btu per mile for the empty ocean tanker using energy consumption, load factor, and average speed
    btu_per_mile_tanker_back_haul = (energy_consumption_tanker * hp_tanker * load_factor_tanker_back_haul) / average_speed_tanker

    #Convert Btu per mile to gallons per mile for the ocean tanker
    gallons_per_mile_tanker_origin_to_destination = btu_per_mile_tanker_origin_to_destination / btu_per_gallon_residual_oil
    gallons_per_mile_tanker_back_haul = btu_per_mile_tanker_back_haul / btu_per_gallon_residual_oil

    #Calculate total emissions for the trip for one tanker
    total_emissions = {}
    for pollutant, factor in emissions_factors_tanker.items():
        emissions_origin_to_destination = factor * gallons_per_mile_tanker_origin_to_destination * btu_per_gallon_residual_oil / 1e6 * miles
        emissions_back_haul = factor * gallons_per_mile_tanker_back_haul * btu_per_gallon_residual_oil / 1e6 * miles
        total_emissions[pollutant] = (emissions_origin_to_destination + emissions_back_haul) * number_of_tankers

    return total_emissions


def calculate_fuelused_emissions(miles_ocean_tanker, miles_truck):
    """
    Calculate the combined emissions from fuel consumption for an ocean tanker and a truck.

    Parameters:
    - miles_ocean_tanker (float): The total distance traveled by the ocean tanker in miles.
    - miles_truck (float): The total distance traveled by the truck in miles.

    Returns:
    - dict: A dictionary containing the combined emissions from fuel consumption for the ocean tanker and the truck, broken down by pollutant.
    """
    
    #Constants
    btu_per_gallon_diesel = 138700  #BTU per gallon for diesel per EPA
    btu_per_gallon_resid = 149700  #BTU per gallon for resid 
    energy_consumption_btu_hphr = 5439  
    engine_efficiency = 0.50  #Assumed average engine efficiency for the tanker (Googled, Source: C2E2, typically 45-52%)
    average_speed_mph_tanker = 20  
    mpg_truck = 5.6 #Average MPG for trucks (Googled, Source: EPA)

    #Calculate gallons of fuel consumed per hour per horsepower for the tanker
    gallons_per_hour_per_hp_tanker = energy_consumption_btu_hphr / (btu_per_gallon_resid * engine_efficiency)
    mpg_tanker = average_speed_mph_tanker / gallons_per_hour_per_hp_tanker

    #Gallons per mile (inverse of MPG for calculation purposes)
    gallons_per_mile_tanker = 1.0 / mpg_tanker
    gallons_per_mile_truck = 1.0 / mpg_truck

    #Calculate total fuel consumption in gallons for each vehicle
    total_fuel_consumption_tanker = miles_ocean_tanker * gallons_per_mile_tanker
    total_fuel_consumption_truck = miles_truck * gallons_per_mile_truck

    #Convert total fuel consumption to mmBtu
    total_fuel_consumption_mmBtu_tanker = total_fuel_consumption_tanker * btu_per_gallon_resid / 1e6
    total_fuel_consumption_mmBtu_truck = total_fuel_consumption_truck * btu_per_gallon_diesel / 1e6

    #Emissions factors for fuel production (grams per mmBtu)
    emissions_factors = {
        'diesel': {
            'CO2': 12747.98, 
            'CH4': 109.519,  
            'N2O': 0.233,  
        },
        'resid': {
            'CO2': 9670.93,
            'CH4': 100.419,
            'N2O': 0.162,
        }
    }

    #Initialize a dictionary to hold the combined emissions
    combined_emissions = {'CO2': 0, 'CH4': 0, 'N2O': 0}

    #Calculate combined emissions for each pollutant
    for pollutant in combined_emissions:
        combined_emissions[pollutant] = (
            total_fuel_consumption_mmBtu_tanker * emissions_factors['resid'][pollutant] +
            total_fuel_consumption_mmBtu_truck * emissions_factors['diesel'][pollutant]
        )

    return combined_emissions


def calculate_emissions_from_diesel(gallons_diesel):
    """
    Calculate the emissions from the production of diesel fuel.

    Parameters:
    - gallons_diesel (float): The total amount of diesel fuel used in gallons.

    Returns:
    - dict: A dictionary containing the emissions from the production of diesel fuel, broken down by pollutant.

    Note:
    - This function calculates emissions from the production of diesel fuel based on the amount of diesel used and emissions factors for diesel production.
    - Emissions factors are provided for CO2, CH4, and N2O emissions per mmBtu of diesel produced.
    - Emissions are calculated in grams for each pollutant emitted during the production of the specified amount of diesel fuel.
    - The function returns a dictionary containing emissions for each pollutant emitted during the production of diesel fuel.

    Example:
    emissions = calculate_emissions_from_diesel(124000)
    for pollutant, total in emissions.items():
        print(f"Emissions of {pollutant} from the production of diesel: {total} grams")
    """
    
    btu_per_gallon_diesel = 138700

    #Emissions factors for diesel production (grams per mmBtu)
    emissions_factors_diesel = {
        'CO2': 12747.98, 
        'CH4': 109.519,  
        'N2O': 0.233,  
    }

    #Convert total gallons of diesel to mmBtu
    total_energy_mmBtu = gallons_diesel * btu_per_gallon_diesel / 1e6
    emissions_from_diesel_fuel_used = {pollutant: total_energy_mmBtu * factor for pollutant, factor in emissions_factors_diesel.items()}

    return emissions_from_diesel_fuel_used


def embodied_renewable_emissions(target_solar, target_wind, target_bess_energy, target_diesel):
    """
    Calculate the embodied emissions from the production of renewable energy components and diesel fuel.

    Parameters:
    - target_solar (float): The target capacity of solar panels in kWp.
    - target_wind (float): The target capacity of wind turbines in kW.
    - target_bess_energy (float): The target energy capacity of lithium-ion battery energy storage systems in kWh.
    - target_diesel (float): The target amount of diesel fuel used in gallons.

    Returns:
    - dict: A dictionary containing the embodied emissions for each component (solar, wind, BESS, diesel), broken down by pollutant.

    Note:
    - This function calculates the embodied emissions from the production of renewable energy components (solar panels, wind turbines, lithium-ion battery energy storage systems) and diesel fuel.
    - Emissions factors are provided for each component's production in kilograms of CO2 equivalent per unit of capacity (kWp for solar, kW for wind, kWh for BESS).
    - Emissions are calculated based on the target capacities and energy capacities of each component.
    - Emissions from diesel fuel production are calculated separately using the calculate_emissions_from_diesel function.
    - The function returns a dictionary containing embodied emissions for each component and pollutant emitted during their production.

    Example:
    embodied_emissions = embodied_renewable_emissions(180, 570, 3410, 5600)
    for component, emissions in embodied_emissions.items():
        if component != 'diesel':
            print(f"{component.capitalize()} production emissions: {emissions} g CO2E")
        else:
            print(f"{component.capitalize()} production emissions:")
            for pollutant, amount in emissions.items():
                print(f"  {pollutant}: {amount} g CO2E")
    """
    
    #Emissions factors in kg CO2E per unit capacity
    emissions_factor_bess = 220000  #g CO2E per kWh of lithium ion storage (From paper, Source: [6])
    emissions_factor_solar = 1100000  #g CO2E per kWp of solar panel capacity
    emissions_factor_wind = 683700  #g CO2E per kW of wind turbine capacity

    embodied_emissions_bess = target_bess_energy * emissions_factor_bess 
    embodied_emissions_solar = target_solar * emissions_factor_solar  
    embodied_emissions_wind = target_wind * emissions_factor_wind  

    #Diesel production emissions in grams, convert to kg
    embodied_emissions_diesel = calculate_emissions_from_diesel(target_diesel)
    embodied_emissions_diesel = {pollutant: total for pollutant, total in embodied_emissions_diesel.items()}

    total_embodied_emissions = {
        'bess': embodied_emissions_bess,
        'solar': embodied_emissions_solar,
        'wind': embodied_emissions_wind,
        'diesel': embodied_emissions_diesel
    }

    return total_embodied_emissions


def sum_emissions(*emission_dicts):
    """
    Aggregates emissions data from multiple dictionaries into a single dictionary.

    This function is designed to sum up the emissions values for the same pollutants from different
    transportation scenarios or legs. It takes any number of emission dictionaries and combines their
    contents, summing values for identical pollutant keys.

    Parameters:
    *emission_dicts (dict): Variable number of dictionary arguments where each dictionary represents
                            emissions data for a specific transportation scenario or leg. Each dictionary
                            should have pollutant names as keys and emission values as numeric values.

    Returns:
    dict: A dictionary containing the summed emissions for each pollutant across all provided dictionaries.
          Pollutant names are the keys and the summed values are the numeric values.

    Note:
    - The function does not check the type of values in the dictionaries; it assumes all values associated with pollutants
      are numeric and summable.
    - Pollutants not present in all dictionaries are included in the output with their available summed values.
    - This function does not modify the input dictionaries.
    
    Example Usage:
    emissions_dict1 = {'CO2': 100, 'NOx': 50}
    emissions_dict2 = {'CO2': 200, 'SOx': 30}
    total_emissions = sum_emissions(emissions_dict1, emissions_dict2)
    #Output: {'CO2': 300, 'NOx': 50, 'SOx': 30}

    """

    total_emissions = {}
    for emissions in emission_dicts:
        for pollutant, amount in emissions.items():
            if pollutant in total_emissions:
                total_emissions[pollutant] += amount
            else:
                total_emissions[pollutant] = amount
    return total_emissions


def consolidate_scenario_emissions(transport_emissions, additional_emissions):
    """
    Consolidate emissions data from various sources into total values for CO2, CH4, and N2O.

    Parameters:
    - transport_emissions (dict): A dictionary containing emissions data for various transport units,
      where each key represents a transport unit and the value is another dictionary with pollutants as keys.
    - additional_emissions (dict): A dictionary containing emissions data for other categories like bess, solar,
      wind, and a nested dictionary for diesel which includes CO2, CH4, and N2O emissions.

    Returns:
    - dict: A dictionary with total emissions for CO2, CH4, and N2O across all categories.
    """
    
    # Initialize totals for each pollutant
    total_emissions = {'CO2': 0, 'CH4': 0, 'N2O': 0}
    
    # Sum up emissions from the transport emissions dictionary
    for unit_emissions in transport_emissions.values():
        for pollutant, amount in unit_emissions.items():
            total_emissions[pollutant] += amount

    # Sum up emissions from the additional emissions dictionary
    for key, value in additional_emissions.items():
        if isinstance(value, dict):
            # If the value is a dictionary, it contains emissions for diesel including CO2, CH4, and N2O
            for pollutant, amount in value.items():
                total_emissions[pollutant] += amount
        else:
            # Otherwise, it's directly a CO2 value for bess, solar, or wind
            total_emissions['CO2'] += value

    return total_emissions


def transportation_scenario_emissions(target_solar, turbine_power, target_wind, target_bess_power, target_bess_energy, target_diesel):
    """
    Calculates the total emissions from transporting various energy components: solar panels,
    wind turbines, battery energy storage systems (BESS), and diesel. This function estimates
    emissions for each component based on assumed weight and transportation mode emissions.

    Parameters:
    - target_solar (float): Target capacity of solar panels in kW.
    - turbine_power (float): Power rating of each wind turbine in kW.
    - target_wind (float): Total targeted wind power in kW.
    - target_bess_power (float): Power capacity of each BESS unit in kW (not directly used).
    - target_bess_energy (float): Total energy capacity required for BESS units in kWh.
    - target_diesel (float): Total diesel volume in gallons.

    Returns:
    dict: A dictionary containing total emissions for transporting each component type, keyed by
          the component type. Each value is a dictionary of pollutant emissions.

    Usage:
    emissions = transportation_scenario_emissions(5000, 1000, 20000, 500, 10000, 2000)
    print(emissions)

    The emissions calculations assume the inclusion of different transport phases such as tanker and
    truck trips, where each phase contributes to the total emissions for a given energy component.
    """

    #Solar Panels
    pv_g_kw = 160  #Assumed from paper

    #For 20 ft container from MicroGreen
    bess_container_weight_kg = 18000
    bess_energy_capacity_kwh = 1240

    #For the Nps100c-24 wind turbine
    nps_100c_24_weight = 19.8  #Weight of one wind turbine in tons (Googled, Source: 10)
    
    #Number of wind turbines needed + weight
    num_turbines = target_wind / turbine_power
    total_weight_turbines = num_turbines * nps_100c_24_weight
    
    #Total grams for PV systems
    total_grams_pv = target_solar * pv_g_kw
    #Convert total grams to tons (assuming 1 ton = 907,185 grams)
    total_tons_pv = total_grams_pv / 907185
    
    #Calculate the number of BESS units required based on the required energy capacity
    num_bess_units = target_bess_energy / bess_energy_capacity_kwh
    #Total weight for BESS units in tons (assuming 1 ton = 1000 kg)
    total_weight_bess_tons = num_bess_units * (bess_container_weight_kg / 1000)
    
    total_weight_diesel_tons = (target_diesel * 6.5) / 2000  # Convert lbs to tons

    #Wind Trip Emissions, travels through LC-130
    wind_trip_emissions = sum_emissions(
        calculate_tanker_emissions(6900, total_weight_turbines, 1),
        #The icebreaker/second tanker holds no cargo for the second trip, thus the weight is "evenly" distributed amongst the 2
        calculate_tanker_emissions(2415, total_weight_turbines/2, 2),
        calculate_truck_emissions(1030, total_weight_turbines / (num_turbines * 7), num_turbines * 7)
    )

    #PV Trip Emissions, travels through SPoT
    pv_trip_emissions = sum_emissions(
        calculate_tanker_emissions(6900, total_tons_pv, 1),
        calculate_tanker_emissions(2415, total_tons_pv/2, 2),
        #The total cargo is split amongst all nine vehicles thus the division. The function is written in a way where the input cargo is assumed to be the weight carried
        #by each # of vehicles
        calculate_truck_emissions(1030, total_tons_pv/9, 9)
    )

    #BESS Trip Emissions, travels with LC-130
    bess_trip_emissions = sum_emissions(
        calculate_tanker_emissions(6900, total_weight_bess_tons, 1),
        calculate_tanker_emissions(2415, total_weight_bess_tons/2, 2),
        calculate_truck_emissions(100, total_weight_bess_tons / num_bess_units, num_bess_units)
    )

    #Diesel Trip Emissions, travels through SPoT
    diesel_trip_emissions = sum_emissions(
        calculate_tanker_emissions(6900, total_weight_diesel_tons, 1),
        calculate_tanker_emissions(2415, total_weight_diesel_tons/2, 2),
        calculate_truck_emissions(1030, total_weight_diesel_tons/9, 9)
    )

    total_emissions = {
        'wind_turbines_transport': wind_trip_emissions,
        'pv_panels_transport': pv_trip_emissions,
        'bess_units_transport': bess_trip_emissions,
        'diesel_transport': diesel_trip_emissions
    }

    return total_emissions
