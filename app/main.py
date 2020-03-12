# Small FastAPI application that handles parsing

# Logging
import sys
import os
import json
from fastapi import Depends, FastAPI, HTTPException, Header
from starlette import status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Union
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

# POST request for errors
@app.post("/error")
def report_error(records: Simulation_err):
    """
    Keep track of errors that occurred
    """
    # Get uid/error
    uid = records.uid
    err = records.error
    # Update the database
    sd.update_status(uid, status="error", msg=err)
