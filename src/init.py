#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories.
The result of running this file is the creation of a signac workspace:
    - signac.rc file containing the project name
    - signac_statepoints.json summary for the entire workspace
    - workspace/ directory that contains a sub-directory of every individual statepoint
    - signac_statepoints.json within each individual statepoint sub-directory.

"""

import logging
from collections import OrderedDict
from itertools import product

import hoomd
import signac


def get_parameters():
    ''''''
    parameters = OrderedDict()

    ### SYSTEM GENERATION PARAMETERS ###
    parameters["system_type"] = [
            "pack",
            #"stack",
    ]
    parameters["density"] = [0.1] # float (g/cm^3)
    parameters["n_chains"] = [10] # int
    parameters["chain_lengths"] = [4] # int
    parameters["bead_length"] = [1] # float (angstroms) 
    parameters["bead_mass"] = [1] # float (amu)
    parameters["bond_length"] = [0.01] # float (angstroms) 
    parameters["box_constraints"] = [
            {"x": None, "y": None, "z": None}
	]
    parameters["kwargs"] = [
            {"box_expand_factor": 5},
            #{"n": 4, "y": 1.5, "y": 1.5, "vector": [1,0,0]}
            #{}
	]

    # SIMULATION PARAMETERS 
    parameters["epsilon"] = [1.0]
    parameters["lperp"] = [0.5] # Semi-axis length perpendicular to bead-bond
    parameters["lpar"] = [1.0] # 1/2 of the bead_length
    parameters["bond_k"] = [500]
    parameters["angle_k"] = [10]
    parameters["angle_theta"] = [2.0]
    parameters["dt"] = [0.0001]
    parameters["r_cut"] = [3.0] # Angstroms
    parameters["sim_seed"] = [42]
    parameters["gsd_write_period"] = [10000] # Num steps between GSD frames
    parameters["log_write_period"] = [10000] # Num steps between log lines

    # Set Shrink run parameters here
    # If all are None; not shrink step will be ran
    # If all are defined (i.e. not None or 0), shrink step will run
    parameters["init_shrink_kT"] = [None]
    parameters["final_shrink_kT"] = [None]
    parameters["shrink_steps"] = [None]
    parameters["shrink_period"] = [None]

    # Run related parameters
    # Set parameters required for the run functions added to project.py
    parameters["tau_kt"] = [0.1]
    parameters["tau_pressure"] = [0.1]
    parameters["neighbor_list"] = [hoomd.md.nlist.Cell]


    return list(parameters.keys()), list(product(*parameters.values()))


def main():
    project = signac.init_project()
    param_names, param_combinations = get_parameters()
    # Create the generate jobs
    for params in param_combinations:
        parent_statepoint = dict(zip(param_names, params))
        parent_job = project.open_job(parent_statepoint)
        parent_job.init()
        parent_job.doc.setdefault("done", False)

    project.update_cache()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
