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

@app.post('/fingerprint')
def fingerprint_articles(records: Records):

    # Retrieve records
    records_list = records.records
    records_uids = records.uids
    retina_name = records.retina_name

    # Checks
    if len(records_list) != len(records_uids):
        return({"message":"uids and records of different length"})

    # Make id + record in dict
    records_dict = {uid:rec for uid, rec in zip(records_uids, records_list)}

    # Get fingerprint for each text
    records_fingerprinted = FP(records_dict, retina_name)

    # Return
    return(records_fingerprinted)

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