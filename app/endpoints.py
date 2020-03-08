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
    # Store ID
    # ...
    # Get a set of parameters
    # ...
    # Return
    # ...

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
        "emiss_varmu_bar": records.emiss_varmu_bar
    }
    # Save results
    out_file = os.path.join("/var/results", records.iteration_uid + ".json")
    # ...
    # Update status
    # ...

    # Return termination message
    return({"message":"terminate"})

@app.get("/retinas")
def get_retinas():

    # Get retina names
    rn = get_retina_names()

    # Return
    return({"retina_names": rn})

@app.post("/terms/all")
def get_all_terms(RS: RetinaSpec):

    retina_name = RS.retina_name

    # Get all retina terms
    rt = get_retina_terms(retina_name)

    # Return
    return({"retina_terms": rt})

@app.post("/terms/similar/fingerprint")
def get_terms_from_fp(ST: SimilarTerms):

    retina_name = ST.retina_name
    fingerprint = ST.fingerprint
    num_terms = ST.num_terms

    # Get terms for FP
    st = get_similar_terms_from_fp(retina_name, num_terms, fingerprint)

    # Return
    return({"similar_terms":st})