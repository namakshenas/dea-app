import numpy as np
import pandas as pd
from gurobipy import Model, GRB
import logging
import time
import data_info
from gurobipy import Model, GRB

def solve_dea(target_dmu, p_inputs, p_outputs):
    n_inputs = p_inputs.shape[1]
    n_outputs = p_outputs.shape[1]
    n_dmu = len(p_inputs)

    s_input = range(n_inputs)
    s_output = range(n_outputs)
    s_dmu = range(n_dmu)

    p_target_dmu = target_dmu

    # Create a Gurobi model
    model = Model("DEA_Problem")
    
    # Decision variables
    v_win = model.addVars(s_input, lb=0.00001)
    v_wout = model.addVars(s_output, lb=0.00001)
    v_tolerance = model.addVar()
    
    # Model constraints
    for d in s_dmu:
        model.addConstr(
            quicksum(p_outputs[d][r] * v_wout[r] for r in s_output) + v_tolerance <=
            quicksum(p_inputs[d][i] * v_win[i] for i in s_input)
        )
    
    model.addConstr(
        quicksum(p_inputs[p_target_dmu][i] * v_win[i] for i in s_input) <= 1,
    )
    model.addConstr(
        quicksum(p_inputs[p_target_dmu][i] * v_win[i] for i in s_input) >= 0.99999,
    )
    
    # Model objective
    model.setObjective(
        quicksum(p_outputs[p_target_dmu][r] * v_wout[r] for r in s_output) + v_tolerance,
        GRB.MAXIMIZE
    )
    
    # Solve the model
    model.optimize()
    
    # Get the objective value

    return model.objVal


def run_model(uploadDataFrame):
    n_inputs, n_outputs, n_dmu = data_info.get_data_info(uploadDataFrame)

    s_dmu = range(n_dmu)

    p_inputs = uploadDataFrame.iloc[:, list(range(n_inputs))].to_numpy()
    p_outputs = uploadDataFrame.iloc[:, list(range(n_inputs, n_inputs + n_outputs))].to_numpy()

    o_efficiency_vec = np.zeros(n_dmu)

    logging.info("waiting for solver!")
    start_time_solver = time.time()
    for d in s_dmu:
        o_efficiency_vec[d] = solve_dea(d, p_inputs, p_outputs)
    end_time_solver = time.time()
    run_time = np.round(end_time_solver - start_time_solver, 2)
    logging.info("The model was solved w.r.t. all DMUs in " + str(
        run_time) + " seconds!")

    # Sorting garages in descending efficiency number
    # o_sorted_efficiency_value = np.flip(np.sort(o_efficiency_vec))
    # o_sorted_efficiency_index = np.flip(np.argsort(o_efficiency_vec))

    # o_efficient = o_sorted_efficiency_index[o_sorted_efficiency_value >= 0.99999]
    # o_inefficient = o_sorted_efficiency_index[o_sorted_efficiency_value < 0.99999]

    o_string_eff_vec = ['efficient' for i in s_dmu]
    for d in s_dmu:
        if o_efficiency_vec[d] < 0.999999:
            o_string_eff_vec[d] = 'inefficient'

    output_table = pd.DataFrame()
    output_table["DMU Index"] = np.array(s_dmu) + 1
    output_table["Value"] = np.round(o_efficiency_vec, 4)
    output_table["Efficiency Status"] = o_string_eff_vec

    return output_table, run_time
