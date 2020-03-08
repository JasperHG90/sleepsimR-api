###########
# Schemas #
###########

from pydantic import BaseModel
from typing import List

# Incoming request for simulation parameters
# The docker container sends its unique id
class Parameter_req(BaseModel):
    uid: str 

# POST request with simulation results
class Simulation_res(BaseModel):
    uid: str 
    scenario_uid: str
    iteration_uid: str 
    emiss_mu_bar: List[List[float]]
    gamma_int_bar: List[float]
    emiss_var_bar: List[List[float]]
    emiss_varmu_bar: List[List[float]]
