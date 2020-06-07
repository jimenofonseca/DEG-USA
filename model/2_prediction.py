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

import time

import pandas as pd
from model.constants import MODEL_NAME
from model.auxiliary import parse_scenario_name, percentile
from pointers import METADATA_FILE_PATH, INTERMEDIATE_RESULT_FILE_PATH, FINAL_RESULT_FILE_PATH


def main():
    # local variables
    intermediate_result = INTERMEDIATE_RESULT_FILE_PATH
    output_path = FINAL_RESULT_FILE_PATH
    scenarios_array = pd.read_excel(METADATA_FILE_PATH, sheet_name='SCENARIOS')['SCENARIO'].values

    # group per scenario and building class and calculate mean and variance
    data_consumption = pd.read_csv(intermediate_result)
    data_consumption = data_consumption.groupby(["BUILDING_CLASS", "SCENARIO"],
                                                as_index=False).agg([percentile(50), percentile(2.5), percentile(97.5)])

    final_df = pd.DataFrame()
    for scenario in scenarios_array:
        ipcc_scenario_name = parse_scenario_name(scenario)
        year_scenario = scenario.split("_")[-1]
        for sector in ['Residential', 'Commercial']:
            use = "GFA_Bm2"
            mean_area= data_consumption.loc[sector, scenario][use, 'percentile_50']
            est_97_5 = data_consumption.loc[sector, scenario][use, 'percentile_97.5']
            est_2_5 = data_consumption.loc[sector, scenario][use, 'percentile_2.5']

            dict_mean = {'Model': MODEL_NAME,
                         'Region': 'USA',
                         'Unit': 'bn m2/yr',
                         'Variable': 'Energy Service|Buildings|' + sector +'|Floor Space',
                         'Scenario': ipcc_scenario_name + ' - 50th percentile',
                         'Year': year_scenario,
                         'Value': mean_area,
                         }
            dict_min = {'Model': MODEL_NAME,
                        'Region': 'USA',
                        'Unit': 'bn m2/yr',
                        'Variable': 'Energy Service|Buildings|' + sector +'|Floor Space',
                        'Scenario': ipcc_scenario_name + ' - 2.5th percentile',
                        'Year': year_scenario,
                        'Value': est_2_5,
                        }
            dict_max = {'Model': MODEL_NAME,
                        'Region': 'USA',
                        'Unit': 'bn m2/yr',
                        'Variable': 'Energy Service|Buildings|' + sector +'|Floor Space',
                        'Scenario': ipcc_scenario_name + ' - 97.5th percentile',
                        'Year': year_scenario,
                        'Value': est_97_5,
                        }
            dataframe = pd.DataFrame([dict_mean, dict_min, dict_max])
            final_df = pd.concat([final_df, dataframe], ignore_index=True)
            for name, use in zip(['Heating|Space', 'Cooling'],
                                 ['TOTAL_HEATING_EJ', 'TOTAL_COOLING_EJ']):
                mean_EJ = data_consumption.loc[sector, scenario][use, 'percentile_50']
                est_97_5_EJ = data_consumption.loc[sector, scenario][use, 'percentile_97.5']
                est_2_5_EJ = data_consumption.loc[sector, scenario][use, 'percentile_2.5']

                dict_mean = {'Model': MODEL_NAME,
                             'Region': 'USA',
                             'Unit': 'EJ/yr',
                             'Variable': 'Final Energy|Buildings|' + sector + '|' + name,
                             'Scenario': ipcc_scenario_name + ' - 50th percentile',
                             'Year': year_scenario,
                             'Value': mean_EJ,
                             }
                dict_min = {'Model': MODEL_NAME,
                            'Region': 'USA',
                            'Unit': 'EJ/yr',
                            'Variable': 'Final Energy|Buildings|' + sector + '|' + name,
                            'Scenario': ipcc_scenario_name + ' - 2.5th percentile',
                            'Year': year_scenario,
                            'Value': est_2_5_EJ,
                            }
                dict_max = {'Model': MODEL_NAME,
                            'Region': 'USA',
                            'Unit': 'EJ/yr',
                            'Variable': 'Final Energy|Buildings|' + sector + '|' + name,
                            'Scenario': ipcc_scenario_name + ' - 97.5th percentile',
                            'Year': year_scenario,
                            'Value': est_97_5_EJ,
                            }
                dataframe = pd.DataFrame([dict_mean, dict_min, dict_max])
                final_df = pd.concat([final_df, dataframe], ignore_index=True)
    result = pd.pivot_table(final_df, values='Value', columns='Year',
                            index=['Model', 'Scenario', 'Region', 'Variable', 'Unit'])
    result.to_csv(output_path)


if __name__ == "__main__":
    t0 = time.time()
    main()
    t1 = round((time.time() - t0) / 60, 2)
    print("finished after {} minutes".format(t1))
