import numpy as np
import pandas as pd

from pointers import METADATA_FILE_PATH, INTERMEDIATE_RESULT_FILE_PATH, FINAL_RESULT_FILE_PATH


def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)

    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


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
            for name, use in zip(['Heating', 'Cooling'],
                                 ['TOTAL_HEATING_EJ', 'TOTAL_COOLING_EJ']):
                mean_EJ = data_consumption.loc[sector, scenario][use, 'percentile_50']
                est_97_5_EJ = data_consumption.loc[sector, scenario][use, 'percentile_97.5']
                est_2_5_EJ = data_consumption.loc[sector, scenario][use, 'percentile_2.5']

                dict_mean = {'Model': 'DEG-USA 1.0',
                             'Region': 'USA',
                             'Unit': 'EJ_yr',
                             'Variable': 'Final Energy|Buildings|' + sector + '|' + name + '|Space',
                             'Scenario': ipcc_scenario_name + ' - 50th percentile',
                             'Year': year_scenario,
                             'Value': mean_EJ,
                             }
                dict_min = {'Model': 'DEG-USA 1.0',
                            'Region': 'USA',
                            'Unit': 'EJ_yr',
                            'Variable': 'Final Energy|Buildings|' + sector + '|' + name + '|Space',
                            'Scenario': ipcc_scenario_name + ' - 2.5th percentile',
                            'Year': year_scenario,
                            'Value': est_2_5_EJ,
                            }
                dict_max = {'Model': 'DEG-USA 1.0',
                            'Region': 'USA',
                            'Unit': 'EJ_yr',
                            'Variable': 'Final Energy|Buildings|' + sector + '|' + name + '|Space',
                            'Scenario': ipcc_scenario_name + ' - 97.5th percentile',
                            'Year': year_scenario,
                            'Value': est_97_5_EJ,
                            }
                dataframe = pd.DataFrame([dict_mean, dict_min, dict_max])
                final_df = pd.concat([final_df, dataframe], ignore_index=True)
    result = pd.pivot_table(final_df, values='Value', columns='Year',
                            index=['Model', 'Scenario', 'Region', 'Variable', 'Unit'])
    result.to_csv(output_path)


def parse_scenario_name(scenario):
    mapa = {'A1B': 'Medium Impact',
            'A2': 'High Impact',
            'B1': 'Low Impact'
            }
    name = scenario.split('_')[-2]
    return mapa[name]


if __name__ == "__main__":
    main()
