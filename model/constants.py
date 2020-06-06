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

COP_cooling = 3.3
COP_heating = 3.0
RH_base_cooling_perc = 60
RH_base_heating_perc = 30
T_base_cooling_C = 18.5
T_base_heating_C = 18.5
ACH_Commercial = 6.0
ACH_Residential = 4.0
ZONE_NAMES = {"Hot-humid": ["1A", "2A", "3A"],
              "Hot-dry": ["2B", "3B"],
              "Hot-marine": ["3C"],
              "Mixed-humid": ["4A"],
              "Mixed-dry": ["4B"],
              "Mixed-marine": ["4C"],
              "Cold-humid": ["5A", "6A"],
              "Cold-dry": ["5B", "6B", "7"]}