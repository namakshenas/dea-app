import logging


def get_model_latex(model_type, orientation_type, form_type):
    dea_model = str.lower(model_type) + "_" + str.lower(orientation_type) + "_" + str.lower(form_type)
    logging.info("The selected model for LATEX-Export is " + dea_model)

    if dea_model == "ccr_input_multiplier":
        return "./assets/ccr_io_mf.png"

    elif dea_model == "ccr_output_multiplier":
        return "./assets/ccr_oo_mf.png"

    elif dea_model == "bcc_input_multiplier":
        return "./assets/bcc_io_mf.png"

    elif dea_model == "bcc_output_multiplier":
        return "./assets/bcc_oo_mf.png"

    else:
        return "./assets/ccr_io_mf.png"
