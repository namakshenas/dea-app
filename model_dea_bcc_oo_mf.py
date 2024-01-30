import numpy as np
import pandas as pd
import pulp as pu
import logging
import time
import data_info
import os

cwd = os.getcwd()
path_to_cplex = os.path.join(cwd, r"assets\cplex\cplex.exe")


def solve_dea(target_dmu, p_inputs, p_outputs):
    n_inputs = p_inputs.shape[1]
    n_outputs = p_outputs.shape[1]
    n_dmu = len(p_inputs)

    s_input = range(n_inputs)
    s_output = range(n_outputs)
    s_dmu = range(n_dmu)

    p_target_dmu = target_dmu

    # decision variables
    v_win = pu.LpVariable.dicts("inputWeight", s_input, lowBound=0.00001)
    v_wout = pu.LpVariable.dicts("outputWeight", s_output, lowBound=0.00001)
    v_tolerance = pu.LpVariable("tolerance")

    # model definition
    model = pu.LpProblem("DEA_Problem", pu.LpMinimize)

    # model constraints
    for d in s_dmu:
        model += pu.lpSum(p_outputs[d][r] * v_wout[r] for r in s_output) + v_tolerance <= \
                 pu.lpSum(p_inputs[d][i] * v_win[i] for i in s_input)

    model += pu.lpSum([p_outputs[p_target_dmu][i] * v_wout[i] for i in s_output]) <= 1
    model += pu.lpSum([p_outputs[p_target_dmu][i] * v_wout[i] for i in s_output]) >= 0.99999

    # model objective
    model += pu.lpSum(p_inputs[p_target_dmu][r] * v_win[r] for r in s_input) - v_tolerance

    # PuLP's choice of Solver
    # solver = pu.COIN_CMD(path='/cbc/bin')
    # model.solve(solver)
    # model.solve(pu.PULP_CBC_CMD(msg=False))

    # path_to_cplex = r"C:\Users\Monash\PycharmProjects\dash-bootstrap\assets\cplex\cplex.exe"
    solver = pu.CPLEX_CMD(path=path_to_cplex, msg=False)
    model.solve(solver)

    # The status of the solution
    # print("Status:", pu.LpStatus[model.status])

    # Each of the variables is printed with it's resolved optimum value
    # for v in model.variables():
    #     print(v.name, "=", v.varValue)

    return pu.value(model.objective)


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

    o_efficiency_vec = 1 / o_efficiency_vec
    o_string_eff_vec = ['efficient' for i in s_dmu]
    for d in s_dmu:
        if o_efficiency_vec[d] < 0.999999:
            o_string_eff_vec[d] = 'inefficient'

    output_table = pd.DataFrame()
    output_table["DMU Index"] = np.array(s_dmu) + 1
    output_table["Value"] = np.round(o_efficiency_vec, 4)
    output_table["Efficiency Status"] = o_string_eff_vec

    return output_table, run_time
