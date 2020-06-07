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

import os
import pandas as pd
from pointers import WEATHER_DATA_FOLDER_PATH


def parse_scenario_name(scenario):
    mapa = {'A1B': 'Medium Impact',
            'A2': 'High Impact',
            'B1': 'Low Impact'
            }
    name = scenario.split('_')[-2]
    return mapa[name]

def read_weather_data_scenario(city, scenario):
    # Quantities
    weather_file_name = city.split(",")[0] + "_" + city.split(", ")[-1] + "-hour.dat"
    weather_file_name = weather_file_name.replace(" ", "_")
    weather_file_location = os.path.join(WEATHER_DATA_FOLDER_PATH, scenario, weather_file_name)
    weather_file = pd.read_csv(weather_file_location, sep='\s+', header=2, skiprows=0)
    temperatures_out_C = weather_file["Ta"].values[:8760]
    relative_humidity_percent = weather_file["RH"].values[:8760]

    return temperatures_out_C, relative_humidity_percent