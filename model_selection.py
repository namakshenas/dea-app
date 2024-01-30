import model_dea_bcc_io_mf
import model_dea_bcc_oo_mf
import model_dea_ccr_io_mf
import model_dea_ccr_oo_mf
import logging


def get_model_type(df_uploaded, model_type, orientation_type, form_type):
    dea_model = str.lower(model_type) + "_" + str.lower(orientation_type) + "_" + str.lower(form_type)
    logging.info("The selected model is " + dea_model)

    if dea_model == "ccr_input_multiplier":
        return model_dea_ccr_io_mf.run_model(df_uploaded)

    elif dea_model == "ccr_output_multiplier":
        return model_dea_ccr_oo_mf.run_model(df_uploaded)

    elif dea_model == "bcc_input_multiplier":
        return model_dea_bcc_io_mf.run_model(df_uploaded)

    elif dea_model == "bcc_output_multiplier":
        return model_dea_bcc_oo_mf.run_model(df_uploaded)

    else:
        return model_dea_ccr_io_mf.run_model(df_uploaded)
