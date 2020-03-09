# This class manages the simulation scenarios and their iterations
import json
import pandas as pd
import os

class SimulationData:

    def __init__(self, path):
        self.path = path
        # Load CSV with scenarios
        self.scen = pd.read_csv("data/scenarios.csv.gz")
        self.scen["allocated"] = False
        self.scen.astype("bool")
        # Set up dict for allocations
        self.allocations = {}
        self.allocations_inv = {}

    def allocate(self, container_id: str):
        """
        Allocate a container to a set of simulation parameters
        """
        # Check if already allocated
        if self.allocations.get(container_id) is not None:
            return self.scen[self.scen["iteration_id"] == self.allocations[container_id]["iteration_id"]].to_dict(orient="list")
        params = self.scen[self.scen.allocated == False].sample(n=1)
        # Set allocation to true
        self.scen.loc[self.scen["iteration_id"] == params.iteration_id.values[0], "allocated"] = True
        # Save in allocations
        self.allocations[container_id] = {"iteration_id": params.iteration_id.values[0],
                                          "status": "working"}
        # Save in inverse mapping
        self.allocations_inv[params.iteration_id.values[0]] = container_id
        # Save allocations to disk
        self.save_allocations()
        # Return values as dict
        par_return = params.to_dict(orient = "list")
        # Set json columns to json
        par_return["start_gamma"] = json.loads(par_return["start_gamma"][0])
        par_return["start_emiss"] = json.loads(par_return["start_emiss"][0])
        return par_return

    def info(self):
        """
        Return the number of processes allocated and finished
        """
        alloc = len(self.allocations)
        finish = sum([True if rec["status"] == "completed" else False for rec in self.allocations.values()])
        return {"allocated": alloc, "finished": finish}

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
        del self.allocations[container_id]
        del self.allocations_inv[itid]

    def update_status(self, container_id: str, status = "completed"):
        """
        Update status for a container
        """
        self.allocations[container_id]["status"] = status
        self.save_allocations()

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
            else:
                # If status is completed, then set pandas allocated column to true
                cls_init.scen.loc[cls_init.scen["iteration_id"] == cls_init.allocations[k]["iteration_id"], "allocated"] = True
        # Save allocations
        cls_init.save_allocations()
        # Return the updated class
        return cls_init
