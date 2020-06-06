'''
MIT License

Copyright (c) 2020 Jimeno A. Fonseca

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import numpy as np
import pandas as pd
from enthalpygradients import EnthalpyGradient

from model.auxiliary import read_weather_data_scenario
from model.constants import COP_cooling, COP_heating, RH_base_cooling_perc, RH_base_heating_perc, T_base_cooling_C, \
    T_base_heating_C, ACH_Commercial, ACH_Residential
from pointers import METADATA_FILE_PATH, INTERMEDIATE_RESULT_FILE_PATH


def main():

    # local variables
    output_path = INTERMEDIATE_RESULT_FILE_PATH
    scenarios_array = pd.read_excel(METADATA_FILE_PATH, sheet_name='SCENARIOS')['SCENARIO'].values
    cities_array = pd.read_excel(METADATA_FILE_PATH, sheet_name='CITIES')['CITY'].values
    floor_area_predictions_df = pd.read_excel(METADATA_FILE_PATH, sheet_name="FLOOR_AREA").set_index('year')
    climate_region_array = pd.read_excel(METADATA_FILE_PATH, sheet_name='CITIES')['Climate Region'].values
    floor_area_climate_df = pd.read_excel(METADATA_FILE_PATH, sheet_name="FLOOR_AREA_CLIMATE").set_index('Climate Region')


    # calculate specific energy consumption per major city
    specific_thermal_consumption_per_city_df = calc_specific_energy_per_major_city(cities_array,
                                                                                   climate_region_array,
                                                                                   floor_area_climate_df,
                                                                                   scenarios_array)

    # calculate weighted average per scenario
    data_weighted_average_df = calc_weighted_average_per_scenario(specific_thermal_consumption_per_city_df)


    # calculate the energy consumption per scenario incorporating variance in built areas
    data_final_df = calc_total_energy_consumption_per_scenario(data_weighted_average_df, floor_area_predictions_df,
                                                               scenarios_array)

    #save the results to disk
    data_final_df.to_csv(output_path, index=False)
    print("done")


def calc_total_energy_consumption_per_scenario(data_weighted_average_df, floor_area_predictions_df, scenarios_array):
    data_final_df = pd.DataFrame()
    for scenario in scenarios_array:
        data_scenario = data_weighted_average_df[data_weighted_average_df["SCENARIO"] == scenario]
        year = data_scenario['YEAR'].values[0]
        data_floor_area_scenario = floor_area_predictions_df.loc[float(year)]
        for sector in ['Residential', 'Commercial']:
            # calculate totals
            total_heating_kWhm2yr = \
            data_scenario[data_scenario["BUILDING_CLASS"] == sector]['TOTAL_HEATING_kWh_m2_yr'].values[0]
            total_cooling_kWhm2yr = \
            data_scenario[data_scenario["BUILDING_CLASS"] == sector]['TOTAL_COOLING_kWh_m2_yr'].values[0]

            # add uncertainty in total built area
            mean_m2 = data_floor_area_scenario['GFA_mean_' + sector + '_m2']
            std_m2 = data_floor_area_scenario['GFA_sd_' + sector + '_m2']
            GFA_m2 = np.random.normal(mean_m2, std_m2, 100)

            total_heating_EJ = GFA_m2 * total_heating_kWhm2yr * 3.6E-12
            total_cooling_EJ = GFA_m2 * total_cooling_kWhm2yr * 3.6E-12

            # list of fields to extract
            dict_data = pd.DataFrame({"SCENARIO": scenario,
                                      "YEAR": year,
                                      "BUILDING_CLASS": sector,
                                      "TOTAL_HEATING_kWh_m2_yr": total_heating_kWhm2yr,
                                      "TOTAL_COOLING_kWh_m2_yr": total_cooling_kWhm2yr,
                                      "TOTAL_HEATING_EJ": total_heating_EJ,
                                      "TOTAL_COOLING_EJ": total_cooling_EJ})
            data_final_df = pd.concat([data_final_df, dict_data], ignore_index=True)
    return data_final_df


def calc_weighted_average_per_scenario(specific_thermal_consumption_per_city_df):
    data_mean_per_scenario = specific_thermal_consumption_per_city_df.groupby(
        ["YEAR", "BUILDING_CLASS", "SCENARIO", "CLIMATE"],
        as_index=False).agg('mean')
    data_mean_per_scenario["TOTAL_HEATING_kWh_m2_yr"] = data_mean_per_scenario["TOTAL_HEATING_kWh_m2_yr"] * \
                                                        data_mean_per_scenario["WEIGHT"]
    data_mean_per_scenario["TOTAL_COOLING_kWh_m2_yr"] = data_mean_per_scenario["TOTAL_COOLING_kWh_m2_yr"] * \
                                                        data_mean_per_scenario["WEIGHT"]
    data_weighted_average = data_mean_per_scenario.groupby(["YEAR", "BUILDING_CLASS", "SCENARIO"], as_index=False).agg(
        'sum')
    return data_weighted_average


def calc_specific_energy_per_major_city(cities_array, climate_region_array, floor_area_climate_df, scenarios_array):
    specific_thermal_consumption_per_city_df = pd.DataFrame()
    for city, climate in zip(cities_array, climate_region_array):
        floor_area_climate = floor_area_climate_df.loc[climate]
        for scenario in scenarios_array:
            # read wheater data
            T_outdoor_C, RH_outdoor_perc = read_weather_data_scenario(city, scenario)

            # get the scanario year
            year_scenario = scenario.split("_")[-1]
            for sector, ACH in zip(['Residential', 'Commercial'], [ACH_Residential, ACH_Commercial]):
                # calculate energy use intensities

                # calculate specific energy consumption with daily enthalpy gradients model
                eg = EnthalpyGradient(T_base_cooling_C, RH_base_cooling_perc)
                sensible_cooling_kWhm2yr = eg.specific_thermal_consumption(T_outdoor_C, RH_outdoor_perc, type='cooling',
                                                                           ACH=ACH, COP=COP_cooling)
                latent_cooling_kWhm2yr = eg.specific_thermal_consumption(T_outdoor_C, RH_outdoor_perc,
                                                                         type='dehumidification', ACH=ACH,
                                                                         COP=COP_cooling)

                eg = EnthalpyGradient(T_base_heating_C, RH_base_heating_perc)
                sensible_heating_kWhm2yr = eg.specific_thermal_consumption(T_outdoor_C, RH_outdoor_perc, type='heating',
                                                                           ACH=ACH, COP=COP_heating)
                latent_heating_kWhm2yr = eg.specific_thermal_consumption(T_outdoor_C, RH_outdoor_perc,
                                                                         type='humidification', ACH=ACH,
                                                                         COP=COP_heating)

                # calculate specific totals
                total_heating_kWhm2yr = sensible_heating_kWhm2yr + latent_heating_kWhm2yr
                total_cooling_kWhm2yr = sensible_cooling_kWhm2yr + latent_cooling_kWhm2yr

                # list of fields to extract
                dict_data = pd.DataFrame({"CITY": city,
                                          "CLIMATE": climate,
                                          "WEIGHT": floor_area_climate['GFA_mean_' + sector + '_perc'],
                                          "SCENARIO": scenario,
                                          "YEAR": year_scenario,
                                          "BUILDING_CLASS": sector,
                                          "TOTAL_HEATING_kWh_m2_yr": total_heating_kWhm2yr,
                                          "TOTAL_COOLING_kWh_m2_yr": total_cooling_kWhm2yr}, index=[0])
                specific_thermal_consumption_per_city_df = pd.concat(
                    [specific_thermal_consumption_per_city_df, dict_data], ignore_index=True)
        print("city {} done".format(city))
    return specific_thermal_consumption_per_city_df


if __name__ == "__main__":
    main()
