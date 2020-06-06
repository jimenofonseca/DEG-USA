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

    # navigate through the cities_array and scenarios_array
    specific_thermal_consumption_per_city_df = pd.DataFrame()
    for city in cities_array:
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
                                          "SCENARIO": scenario,
                                          "YEAR": year_scenario,
                                          "BUILDING_CLASS": sector,
                                          "Q_TOTAL_SPACE_HEATING_kWh_m2_yr": total_heating_kWhm2yr,
                                          "Q_TOTAL_SAPCE_COOLING_kWh_m2_yr": total_cooling_kWhm2yr}, index=[0])
                specific_thermal_consumption_per_city_df = pd.concat(
                    [specific_thermal_consumption_per_city_df, dict_data], ignore_index=True)
        print("city {} done".format(city))

    # now compute the means and the percentilles
    data_mean_per_scenario = specific_thermal_consumption_per_city_df.groupby(["YEAR", "BUILDING_CLASS", "SCENARIO"],
                                                                              as_index=False).agg('mean')
    data_final_df = pd.DataFrame()
    for scenario in scenarios_array:
        data_scenario = data_mean_per_scenario[data_mean_per_scenario["SCENARIO"] == scenario]
        year = data_scenario['YEAR'].values[0]
        data_floor_area_scenario = floor_area_predictions_df.loc[float(year)]
        for sector in ['Residential', 'Commercial']:
            # calculate totals
            total_heating_kWhm2yr = data_scenario[data_scenario["BUILDING_CLASS"] == sector]['Q_TOTAL_SPACE_HEATING_kWh_m2_yr'].values[0]
            total_cooling_kWhm2yr = data_scenario[data_scenario["BUILDING_CLASS"] == sector]['Q_TOTAL_SAPCE_COOLING_kWh_m2_yr'].values[0]

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
                                      "TOTAL_HEATING_EJ": total_heating_EJ,
                                      "TOTAL_COOLING_EJ": total_cooling_EJ})
            data_final_df = pd.concat([data_final_df, dict_data], ignore_index=True)
    data_final_df.to_csv(output_path, index=False)
    print("done")


if __name__ == "__main__":
    main()
