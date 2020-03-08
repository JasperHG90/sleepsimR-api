# This class manages the simulation scenarios and their iterations
import json
import pandas as pd

class SimulationData:

    def __init__(self):
        # Load CSV with scenarios
        # ...
        # Load json file with allocations 
        # ...
        # (pod_id: {iteration_id, finished: True/False})
        # On startup --> all pods that are not on finished are removed from overview
        # ...
        # Invert index
        # {iteration_id: pod_id}
        # ...
        None

    def allocate(self, container_id: str):
        """
        Allocate a container to a set of simulation parameters
        """
        None

    def save_allocations(self):
        """
        Save the current overview of allocations to disk
        """
        None 

    def load_allocations(self):
        """
        Load the allocation from disk
        """
        None

    def load_scenarios(self):
        """
        Load the scenarios from disk
        """
        None

    def pop_allocation(self, container_id: str):
        """
        Remove an allocation from the allocation overview
        """
        None

    def update_status(self, container_id: str, status = "completed"):
        """
        Update status for a container
        """
        None
        # If status is not completed, then pop it

    @classmethod
    def from_file(cls):
        """
        Load an allocation from file
        """
        None

    

    
