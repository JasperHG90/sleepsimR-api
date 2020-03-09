# Small FastAPI application that handles parsing

# Logging
import logging
import daiquiri
import sys
import os

# Import schemas
from dataclass import SimulationData

# If simulation data exists, load. Else start new
if "allocations.json" in os.listdir():
    sd = SimulationData.from_file()
else:
    sd = SimulationData()

# Set up daiquiri
daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)

# Log both to stdout and as JSON in a file called /dev/null. (Requires
# `python-json-logger`)
daiquiri.setup(level=logging.INFO, outputs=(
    daiquiri.output.Stream(sys.stdout),
    daiquiri.output.File("sleepsimR_log.json",
                         formatter=daiquiri.formatter.JSON_FORMATTER),
    ))
# Emit
logger.info("Started simulation API ...")

#################
# API endpoints #
#################

# Import modules
from fastapi import FastAPI
from schemas import Parameter_req, Simulation_res
# Create the api
app = FastAPI()

# GET request for parameters
@app.get("/parameters")
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
    out_file = os.path.join("/var/results", records.iteration_uid + ".json")
    # ...
    # Update status
    sd.update_status(records.uid, status = "completed")

    # Return termination message
    return({"message":"terminate"})
