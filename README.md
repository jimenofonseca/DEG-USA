# DEG-USA-1.0 ![GitHub license](https://img.shields.io/github/license/JIMENOFONSECA/DEG-USA)
 
Forecasting model of building energy consumption for the USA (part of the 6th IPCC report on Climate Change (2021)).

## How does it work

The forecasting model is based on the publication of [`Fonseca et al., 2020`](https://doi.org/10.1016/j.apenergy.2019.114458) which includes forecasts for over 100 cities across the United States and for multiple scenarios of climate change.

This repository includes some post-processing steps needed to aggregate the original results of `Fonseca et al., 2020` at the national level (as requested by the IPCC database). These included:

1. Estimation of a weighted average of specific thermal energy consumption across different climatic regions. The weight is the built area per region. This estimation is carried out for every scenario of climate change described in `Fonseca et al., 2020`.
2. Montecarlo simulation of the built area for commercial and residential areas in the united states. The montecarlo simulation is carried out based on mean and standard errors of built area provided by the U.S. governmnet.
3. Multiplication of the results of 1 and 2 and estimation of the 50th, 2.5th and 97.5th percentiles for every climate change scenario.

## Installation

- Clone this repository
- Install dependencies in setup.py (EnthalpyGradients==1.0, numpy, pandas)

## FAQ

- Where are the resultsstored? A: the results are inside the results folder / final_results.csv
- Where is the orginal database of built areas? A: It is publicly available for commercial and residential buildings [`here`](https://www.eia.gov/consumption/commercial/data/2012/) and [`here`](https://www.eia.gov/consumption/residential/data/2015/)
- Where is the orginal weather data? A: it is not available to the public. It was obtained from the private vendor [`Meteonorm`](https://meteonorm.com/en/)

## Cite

J. A. Fonseca and A. Schlueter, Daily enthalpy gradients and the effects of climate change on the thermal 
energy demand of buildings in the United States, Appl. Energy, vol. 262, no. September 2019, p. 114458, 2020.
https://doi.org/10.1016/j.apenergy.2019.114458
