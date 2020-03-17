# Small FastAPI application that handles parsing

# Logging
import sys
import os
import json
from fastapi import Depends, FastAPI, HTTPException, Header
from starlette import status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Dict, Union
import secrets

# Get env variables
try:
    usr = os.environ["SLEEPSIMR_USER"]
except KeyError:
    raise KeyError("'SLEEPSIMR_USER' username must be passed to the docker container as an environment variable")
try:
    pwd = os.environ["SLEEPSIMR_PWD"]
except KeyError:
    raise KeyError("'SLEEPSIMR_PWD' password must be passed to the docker container as an environment variable")

# Assert not empty
assert usr != "", "User not set in environment file"
assert pwd != "", "Password not set in environment file"

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

# Schema for a single emission MAP estimates
class MAP_value(BaseModel):
    mean: List[Union[float, int]]
    median: List[Union[float, int]]
    SE: List[Union[float, int]]

# Schema for all emission MAP estimates
class Emiss_map(BaseModel):
    EEG_mean_beta: MAP_value
    EOG_median_theta: MAP_value
    EOG_min_beta: MAP_value

# Schema for credible intervals of emission distributions
class Emiss_CI(BaseModel):
    EEG_mean_beta: List[Union[float, int]]
    EOG_median_theta: List[Union[float, int]]
    EOG_min_beta: List[Union[float, int]]

# Schema for credible intervals
class Credible_intervals(BaseModel):
    gamma_int_bar: List[Union[float, int]]
    emiss_mu_bar: Emiss_CI
    emiss_var_bar: Emiss_CI
    emiss_varmu_bar: Emiss_CI

# Schema used for rank-ordered state mean indices
class Ordering(BaseModel):
    EEG_mean_beta: List[int]
    EOG_median_theta: List[int]
    EOG_min_beta: List[int]

# POST request with simulation results
class Simulation_res(BaseModel):
    uid: str 
    scenario_uid: str
    iteration_uid: str 
    PD_subj: List[MAP_value]
    emiss_mu_bar: Emiss_map
    gamma_int_bar: MAP_value
    emiss_var_bar: Emiss_map
    emiss_varmu_bar: Emiss_map
    credible_intervals: Credible_intervals
    label_switch: List[Union[float, int]]
    state_order: Ordering

class Simulation_err(BaseModel):
    uid: str
    error: str

#################
# API endpoints #
#################

# Create the api
app = FastAPI(docs_url=None)

# Security scheme
security = HTTPBasic()

# Auth function
def auth_container(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, usr)
    correct_password = secrets.compare_digest(credentials.password, pwd)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"Auth": "Adv"},
        )
    return credentials.username

# GET request for number of processes currently running
@app.get("/info")
def return_info(username: str = Depends(auth_container)):
    # Get information from object
    inf = sd.info()
    return inf

# GET request for parameters
@app.get("/parameters")
def get_parameters(uid: str = Header(None), username: str = Depends(auth_container)):
    # Get the id of the container that is simulating this iteration
    cont_id = uid
    # If None, then error out
    if uid is None:
        raise HTTPException(
            status_code = 400,
            detail="ID not supplied",
            headers={"missing": "id"}
        )
    # Get a set of parameters
    out = sd.allocate(cont_id)
    # Return
    return out

# POST request for simulation results
@app.post('/results')
def save_results(records: Simulation_res, username: str = Depends(auth_container)):
    """
    Take simulation results and save to disk
    """
    # Get results
    res = records.dict()
    # Save results
    out_file = os.path.join(RESULTS_OUT, records.iteration_uid + ".json")
    with open(out_file, "w") as outFile:
        json.dump(res, outFile,
                  indent=4)
    # Update status
    sd.update_status(records.uid, status = "completed")
    # Return termination message
    return {"message":"terminate"}

# POST request for errors
@app.post("/error")
def report_error(records: Simulation_err, username: str = Depends(auth_container)):
    """
    Keep track of errors that occurred
    """
    # Get uid/error
    uid = records.uid
    err = records.error
    # Update the database
    sd.update_status(uid, status="error", msg=err)

# GET currently allocated IDs
@app.get("/active_workers")
def get_workers(username: str = Depends(auth_container)):
    """
    Get the IDs of all current active workers
    """
    return sd.get_active_workers()
