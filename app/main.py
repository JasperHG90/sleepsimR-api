# Small FastAPI application that handles parsing

# Logging
import sys
import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Import schemas
from dataclass import SimulationData

# Folder used to store data
FOLDER_OUT = "/var/sleepsimR"
RESULTS_OUT = os.path.join(FOLDER_OUT, "results")
# If not "results", then create
if "results" not in os.listdir(FOLDER_OUT):
    os.mkdir(RESULTS_OUT)

# If simulation data exists, load. Else start new
if "allocations.json" in os.listdir(FOLDER_OUT):
    sd = SimulationData.from_file(FOLDER_OUT)
else:
    sd = SimulationData(FOLDER_OUT)

###########
# Schemas #
###########

# Incoming request for simulation parameters
# The docker container sends its unique id
class Parameter_req(BaseModel):
    uid: str 

# POST request with simulation results
class Simulation_res(BaseModel):
    uid: str 
    scenario_uid: str
    iteration_uid: str 
    emiss_mu_bar: List
    gamma_int_bar: List
    emiss_var_bar: List
    emiss_varmu_bar: List
    credible_intervals: List

#################
# API endpoints #
#################

# Create the api
app = FastAPI()

# GET request for number of processes currently running
@app.get("/info")
def return_info():
    # Get information from object
    inf = sd.info()
    return inf

# POST request for parameters
@app.post("/parameters")
def get_parameters(records: Parameter_req):
    # Get the id of the container that is simulating this iteration
    cont_id = records.uid
    # Get a set of parameters
    out = sd.allocate(cont_id)
    # Return
    return out

# POST request for simulation results
@app.post('/results')
def save_results(records: Simulation_res):
    """
    Take simulation results and save to disk
    """
    # Get results
    res = {
        "container_uid": records.uid,
        "scenario_uid": records.scenario_uid,
        "emiss_mu_bar": records.emiss_mu_bar,
        "gamma_int_bar": records.gamma_int_bar,
        "emiss_var_bar": records.emiss_var_bar,
        "emiss_varmu_bar": records.emiss_varmu_bar,
        "credible_intervals": records.credible_intervals
    }
    # Save results
    out_file = os.path.join(RESULTS_OUT, records.iteration_uid + ".json")
    with open(out_file, "w") as outFile:
        json.dump(res, outFile)
    # Update status
    sd.update_status(records.uid, status = "completed")
    # Return termination message
    return {"message":"terminate"}
