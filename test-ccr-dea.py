import numpy as np
import pandas as pd
import pulp as pu

def solve_dea(target_dmu):
    p_target_dmu = target_dmu

    # decision variables
    v_win = pu.LpVariable.dicts("inputWeight", s_input, lowBound=0.001, upBound=1)
    v_wout = pu.LpVariable.dicts("outoutWeight", s_output, lowBound=0.001, upBound=1)

    # model definition
    model = pu.LpProblem("DEA_CCR_Problem", pu.LpMaximize)

    # model constraints
    for d in s_dmu:
        model += pu.lpSum(p_outputs[d][r] * v_wout[r] for r in s_output) <= \
                 pu.lpSum(p_inputs[d][i] * v_win[i] for i in s_input)

    model += pu.lpSum([p_inputs[p_target_dmu][i] * v_win[i] for i in s_input]) == 1

    # model objective
    model += pu.lpSum(p_outputs[p_target_dmu][r] * v_wout[r] for r in s_output)

    # PuLP's choice of Solver
    model.solve(pu.PULP_CBC_CMD(msg=False))

    # The status of the solution
    # print("Status:", pu.LpStatus[model.status])

    # Each of the variables is printed with it's resolved optimum value
    # for v in model.variables():
    #     print(v.name, "=", v.varValue)

    # The optimised objective function value is printed to the screen
    # print("Efficiency of DMU ", p_target_dmu + 1, " = ", pu.value(model.objective))

    return pu.value(model.objective)
    # print(model)


if __name__ == "__main__":
    df = pd.read_excel("sample-dea-data_ss.xlsx")

    n_inputs = 2
    n_outputs = 3
    n_dmu = 20

    s_input = range(n_inputs)
    s_output = range(n_outputs)
    s_dmu = range(n_dmu)

    p_inputs = df.iloc[:, list(range(n_inputs))].to_numpy()
    p_outputs = df.iloc[:, list(range(n_inputs, n_inputs + n_outputs))].to_numpy()

    o_efficiency_vec = np.zeros(n_dmu)

    for d in s_dmu:
        o_efficiency_vec[d] = solve_dea(d)

    # Sorting garages in descending efficiency number
    o_sorted_efficiency_value = np.flip(np.sort(o_efficiency_vec))
    o_sorted_efficiency_index = np.flip(np.argsort(o_efficiency_vec))

    o_efficient = o_sorted_efficiency_index[o_sorted_efficiency_value >= 0.99999]
    o_inefficient = o_sorted_efficiency_index[o_sorted_efficiency_value < 0.99999]

    # print(o_efficient)
    # print(o_inefficient)
    #
    # for h in sorted_performance.keys():
    #     if sorted_performance[h] >= 0.9999999:
    #         efficient.append(h)
    #     if sorted_performance[h] < 0.9999999:
    #         inefficient.append(h)
    #
    print('____________________________________________')
    print(f"The efficient DMUs are:")
    for eff in o_efficient:
        print(f"The performance value of DMU {eff+1} is: {round(o_efficiency_vec[eff], 2)}")

    print('____________________________________________')
    print(f"The inefficient DMUs are:")
    for ine in o_inefficient:
        print(f"The performance value of DMU {ine+1} is: {round(o_efficiency_vec[ine], 2)}")
