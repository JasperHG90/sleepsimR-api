# This class manages the simulation scenarios and their iterations
import json
import pandas as pd
import numpy as np
import os
import datetime

class SimulationData:

    def __init__(self, path):
        self.path = path
        # Load CSV with scenarios
        self.scen = pd.read_csv("data/scenarios.csv.gz")
        self.scen["allocated"] = False
        self.scen.allocated.astype("bool")
        # Set up dict for allocations
        self.allocations = {}
        self.allocations_inv = {} 

    def allocate(self, container_id: str):
        """
        Allocate a container to a set of simulation parameters
        """
        # Check if already allocated
        if self.allocations.get(container_id) is not None:
            par_return = self.scen[self.scen["iteration_id"] == self.allocations[container_id]["iteration_id"]].iloc[0].to_dict()
        else:
            # Get the rows where allocated == False
            params = self.scen[self.scen.allocated == False]
            # If n rows is 0, then finished
            if params.shape[0] == 0:
                return {"message": "simulation finished"}
            # Get first row
            params = params.iloc[0]
            # Set allocation to true
            self.scen.loc[self.scen["iteration_id"] == params.iteration_id, "allocated"] = True
            # Save in allocations
            self.allocations[container_id] = {"iteration_id": params.iteration_id,
                                              "status": "working",
                                              "ts_request": datetime.datetime.now().timestamp()}
            # Save in inverse mapping
            self.allocations_inv[params.iteration_id] = container_id
            # This is deeply unsatisfying and bad, bad coding practice.
            # It may occur that while the program is saving the allocations
            # another thread changes the allocations while json is encoding
            # the file. This leads to an http error, which I'd like to avoid.
            # Therefore, I am happy if it get saved *most* of the time, and
            # I will disregard this error for now. Perhaps I could move to
            # a proper database solution?
            try:
                # Save allocations to disk
                self.save_allocations()
            except RuntimeError:
                e = None
            # Return values as dict
            par_return = params.to_dict()
        # Make sure that the data is serializable (i.e. not of numpy data types.)
        for k, v in par_return.items():
            if isinstance(v, np.int64):
                par_return[k] = int(v)
            elif isinstance(v, np.float64):
                par_return[k] = float(v)
            elif isinstance(v, np.bool_):
                par_return[k] = bool(v)
            else:
                continue
        # Set json columns to json
        par_return["start_gamma"] = json.loads(par_return["start_gamma"])
        par_return["start_emiss"] = json.loads(par_return["start_emiss"])
        # Remove first column (index)
        del par_return["Unnamed: 0"]
        del par_return["allocated"]
        # Return
        return par_return

    def info(self):
        """
        Return the number of processes allocated and finished
        """
        alloc = len(self.allocations)
        finish = sum([*map(lambda x: True if x["status"] == "completed" else False, self.allocations.values())])
        errored = sum([*map(lambda x: True if x["status"] == "error" else False, self.allocations.values())])
        total = self.scen.shape[0]
        # Compute number of records completed in past day
        timediff = (datetime.datetime.now() - datetime.timedelta(hours=24))
        completed_past_day = sum([*map(lambda x: self.completed_last_day(x, timediff), self.allocations.values())])
        return {"total_iterations": total, "allocated": alloc - finish - errored, 
                "finished": finish,  "finished_past_day": completed_past_day, 
                "errors": errored}

    @staticmethod
    def completed_last_day(record, timediff):
        """
        Evaluates whether or not the input record has been completed in the past 24 hours
        """
        if record.get("ts_finished") is None: return False 
        if record.get("status") is not "completed": return False
        if timediff < datetime.datetime.fromtimestamp(record["ts_finished"]):
            return True
        else:
            return False

    def save_allocations(self):
        """
        Save the current overview of allocations to disk
        """
        with open(os.path.join(self.path, "allocations.json"), "w") as outFile:
            json.dump({"allocations": self.allocations,
                       "allocations_inv": self.allocations_inv},
                       outFile,
                       indent=4) 

    def load_allocations(self):
        """
        Load the allocation from disk
        """
        with open(os.path.join(self.path, "allocations.json"), "r") as inFile:
            all_ok = json.load(inFile)
            self.allocations = all_ok["allocations"]
            self.allocations_inv = all_ok["allocations_inv"]

    def pop_allocation(self, container_id: str):
        """
        Remove an allocation from the allocation overview
        """
        # Get iteration id
        itid = self.allocations[container_id]["iteration_id"]
        # Pop from allocations and inverse
        try:
            del self.allocations[container_id]
        except KeyError:
            print("Keyerror. Container id not found ...")
        try:
            del self.allocations_inv[itid]
        except KeyError:
            print("Keyerror. Iteration ID not found ...")

    def update_status(self, container_id: str, status = "completed", **kwargs):
        """
        Update status for a container
        """
        self.allocations[container_id]["status"] = status
        self.allocations[container_id]["ts_finished"] = datetime.datetime.now().timestamp()
        if status == "error":
            self.allocations[container_id]["msg"] = kwargs.get("msg")
        # See comment above
        try:
            # Save allocations to disk
            self.save_allocations()
        except RuntimeError:
            e = None

    def get_active_workers(self):
        """
        Get the ID of all workers whose status is 'active'
        """
        return [k for k,v in self.allocations.items() if v["status"] == "working"]

    @classmethod
    def from_file(cls, path):
        """
        Load an allocation from file
        """
        # Set up the class
        cls_init = cls(path)
        # Load allocations
        cls_init.load_allocations()
        # Check which allocations are still open
        # Pop these from the stack
        for k in list(cls_init.allocations.keys()):
            if cls_init.allocations[k]["status"] == "working":
                cls_init.pop_allocation(k)
            elif cls_init.allocations[k]["status"] == "completed":
                # If status is completed, then set pandas allocated column to true
                cls_init.scen.loc[cls_init.scen["iteration_id"] == cls_init.allocations[k]["iteration_id"], "allocated"] = True
            else:
                # Error occurred
                # TODO: depending on type of error, send the iteration back to the pool
                cls_init.scen.loc[cls_init.scen["iteration_id"] == cls_init.allocations[k]["iteration_id"], "allocated"] = True
        # Save allocations
        cls_init.save_allocations()
        # Return the updated class
        return cls_init
