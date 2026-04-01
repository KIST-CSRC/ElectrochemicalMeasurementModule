from kbio.kbio_tech import *

class PotentiostatParams():
    """
    Potentiostat parameters of each methods

    Supporting evaluation method : CP, CA, OCV, CV, LSV, PEIS

    Need to make parameter set to operate other evaluation methods

    """
    def __init__(self, ):
        self.HARDWAREPARAMETERRANGE = {

        }
        self.PARAMETERS = {
            "hardware": {
                "I_Range": {
                    "parameter_lable": ECC_parm("I_Range", int),
                    "value_type": int,
                    "min_value" : 1,
                    "max_value" : 12,
                    "unit" : None
                },
                "E_Range": {
                    "parameter_lable": ECC_parm("E_Range", int),
                    "value_type": int,
                    "min_value" : 0,
                    "max_value" : 4,
                    "unit" : None
                },
                "Bandwidth": {
                    "parameter_lable": ECC_parm("Bandwidth", int),
                    "value_type": int,
                    "min_value" : -1,
                    "max_value" : 7,
                    "unit" : None
                },
                "Timebase(s)": {
                    "parameter_lable": ECC_parm("tb", float),
                    "value_type": float,
                    "min_value" : 0.00000001,
                    "max_value" : float("inf"),
                    "unit" : "s"
                },
                "Timebase(s)": {
                    "parameter_lable": ECC_parm("tb", float),
                    "value_type": float,
                    "min_value" : 0.00000001,
                    "max_value" : float("inf"),
                    "unit" : "s"
                },
            },
            "cp": {
                "Current_step": {
                    "parameter_lable": ECC_parm("Current_step", float),
                    "value_type" : list,
                    "len_list_range" : range(0,100),
                    "element_type" : float,
                    "min_value" : -1,
                    "max_value" : 1,
                    "unit" : "A"
                },  
                "vs_initial":{
                    "parameter_lable": ECC_parm("vs_initial", bool),
                    "value_type" : list,
                    "len_list_range" : range(0,100),
                    "element_type" : bool,
                    "unit" : None
                },
                "Duration_step": {
                    "parameter_lable": ECC_parm("Duration_step", float),
                    "value_type" : list,
                    "len_list_range" : range(0,100),
                    "element_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },   
                "Step_number": {
                    "parameter_lable": ECC_parm("Step_number", int), 
                    "value_type" : int,
                    "min_value" : 0,
                    "max_value" : 98,
                    "unit" : None
                },       
                "Record_every_dT": {
                    "parameter_lable": ECC_parm("Record_every_dT", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },
                "Record_every_dE": {
                    "parameter_lable": ECC_parm("Record_every_dE", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 10,
                    "unit" : "V"
                },
                "N_Cycles": {
                    "parameter_lable": ECC_parm("N_Cycles", int),
                    "value_type" : int,
                    "min_value" : 0,
                    "max_value" : 1000,
                    "unit" : None
                },         
                "I_Range": {
                    "parameter_lable": ECC_parm("I_Range", int),
                    "value_type" : int,
                    "min_value" : 1,
                    "max_value" : 11,
                    "unit" : None
                },
            },
            "ca": {
                "Voltage_step": {
                    "parameter_lable": ECC_parm("Voltage_step", float),
                    "value_type" : list,
                    "len_list_range" : range(0,100),
                    "element_type" : float,
                    "min_value" : -10,
                    "max_value" : 10,
                    "unit" : "V"
                },  
                "vs_initial":{
                    "parameter_lable": ECC_parm("vs_initial", bool),
                    "value_type" : list,
                    "len_list_range" : range(0,100),
                    "element_type" : bool,
                    "unit" : None
                },
                "Duration_step": {
                    "parameter_lable": ECC_parm("Duration_step", float),
                    "value_type" : list,
                    "len_list_range" : range(0,100),
                    "element_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },   
                "Step_number": {
                    "parameter_lable": ECC_parm("Step_number", int), 
                    "value_type" : int,
                    "min_value" : 0,
                    "max_value" : 98,
                    "unit" : None
                },       
                "Record_every_dT": {
                    "parameter_lable": ECC_parm("Record_every_dT", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },
                "Record_every_dI": {
                    "parameter_lable": ECC_parm("Record_every_dI", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 1,
                    "unit" : "A"
                },
                "N_Cycles": {
                    "parameter_lable": ECC_parm("N_Cycles", int),
                    "value_type" : int,
                    "min_value" : 0,
                    "max_value" : 1000,
                    "unit" : None
                },         
            },
            "ocv": {
                "Rest_time_T": {
                    "parameter_lable": ECC_parm("Rest_time_T", float),
                    "value_type": float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },
                "Record_every_dT": {
                    "parameter_lable": ECC_parm("Record_every_dT", float),
                    "value_type": float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },
                "Record_every_dE": {
                    "parameter_lable": ECC_parm("Record_every_dE", float),
                    "value_type": float,
                    "min_value" : 0,
                    "max_value" : 10,
                    "unit" : "V"
                },
            },
            "cv": {
                "vs_initial": {     
                    "parameter_lable": ECC_parm("vs_initial", bool), 
                    "value_type": list, 
                    "len_list_range" : range(5,6),
                    "element_type" : bool,
                    "unit" : None
                },
                "Voltage_step": { 
                    "parameter_lable": ECC_parm("Voltage_step", float), 
                    "value_type": list,
                    "len_list_range" : range(5,6),
                    "element_type" : float,
                    "min_value" : -10,
                    "max_value" : 10,
                    "unit" : 'V'
                },
                "Scan_Rate": { 
                    "parameter_lable": ECC_parm("Scan_Rate", float), 
                    "value_type": list,
                    "len_list_range" : range(5,6),                    
                    "element_type" : float,
                    "min_value" : 0,
                    "max_value" : 10,
                    "unit" : "V/s"
                },
                "Scan_number": {     
                    "parameter_lable": ECC_parm("Scan_number", int), 
                    "value_type": int, 
                    "min_value" : 0,
                    "max_value" : 100,
                    "unit" : None
                },
                "Record_every_dE": { 
                    "parameter_lable": ECC_parm("Record_every_dE", float), 
                    "value_type": float, 
                    "min_value" : 0,
                    "max_value" : 10,
                    "unit" : "V"
                },
                "Average_over_dE": { 
                    "parameter_lable": ECC_parm("Average_over_dE", bool), 
                    "value_type": bool, 
                    "unit" : None
                },
                "N_Cycles": {        
                    "parameter_lable": ECC_parm("N_Cycles", int), 
                    "value_type": int, 
                    "min_value" : 0,
                    "max_value" : 100,
                    "unit" : None
                },
                "Begin_measuring_I": { 
                    "parameter_lable": ECC_parm("Begin_measuring_I", float), 
                    "value_type": float, 
                    "min_value" : 0,
                    "max_value" : 1,
                    "unit" : None
                },
                "End_measuring_I": { 
                    "parameter_lable": ECC_parm("End_measuring_I", float), 
                    "value_type": float, 
                    "min_value" : 0,
                    "max_value" : 1,
                    "unit" : None
                },
            },
            "lp": {
                "Record_every_dEr": {
                    "parameter_lable" : ECC_parm("Record_every_dEr", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 10 ,
                    "unit" : "V"
                },
                "Rest_time_T": {
                    "parameter_lable" : ECC_parm("Rest_time_T", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },
                "Record_every_dTr": {
                    "parameter_lable" : ECC_parm("Record_every_dTr", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },
                # "OC1": {
                #     "parameter_lable" : ECC_parm("OC1", bool),
                #     "value_type" : bool,
                # },
                # "E1(V)": {
                #     "parameter_lable" : ECC_parm("E1", float),
                #     "value_type" : float,
                #     "min_value" : 0,
                #     "max_value" : 10
                # },
                # "T1(s)": {
                #     "parameter_lable" : ECC_parm("T1", float),
                #     "value_type" : float,
                #     "min_value" : 0,
                #     "max_value" : 10
                # },
                "vs_initial_scan": {
                    "parameter_lable" : ECC_parm("vs_initial_scan", bool),
                    "value_type" : list,
                    "len_list_range" : range(2,3),
                    "element_type" : bool,
                    "unit" : None
                },
                "Voltage_scan": {
                    "parameter_lable" : ECC_parm("Voltage_scan", float),
                    "value_type" : list,
                    "len_list_range" : range(2,3),
                    "element_type" : float,                                        
                    "min_value" : -10 ,
                    "max_value" : 10,
                    "unit" : "V"
                },
                "Scan_Rate": {
                    "parameter_lable" : ECC_parm("Scan_Rate", float),
                    "value_type" : list,
                    "len_list_range" : range(2,3),
                    "element_type" : float,                                        
                    "min_value" : 0,
                    "max_value" : 10,
                    "unit" : "V/s"
                },
                "Scan_number": {
                    "parameter_lable" : ECC_parm("Scan_number", int),
                    "value_type" : int,
                    "min_value" : 0,
                    "max_value" : 0,
                    "unit" : None
                },
                "Record_every_dE": {
                    "parameter_lable" : ECC_parm("Record_every_dE", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 10,
                    "unit" : "V"
                },
                "Average_over_dE": {
                    "parameter_lable" : ECC_parm("Average_over_dE", bool),
                    "value_type" : bool,
                    "unit" : None
                },
                "Begin_measuring_I": {
                    "parameter_lable" : ECC_parm("Begin_measuring_I", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 1,
                    "unit" : None
                },
                "End_measuring_I": {
                    "parameter_lable" : ECC_parm("End_measuring_I", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 1,
                    "unit" : None
                },
                
            },
            "peis": {
                "vs_initial": {     
                    "parameter_lable": ECC_parm("vs_initial", bool), 
                    "value_type": bool,               
                    "unit" : None
                },
                "vs_final": {     
                    "parameter_lable": ECC_parm("vs_final", bool), 
                    "value_type": bool,               
                    "unit" : None
                },
                "Initial_Voltage_step": { 
                    "parameter_lable": ECC_parm("Initial_Voltage_step", float), 
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 10,
                    "unit" : "V"
                },
                "Final_Voltage_step": { 
                    "parameter_lable": ECC_parm("Final_Voltage_step", float), 
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 10,
                    "unit" : "V"
                },
                "Duration_step": {
                    "parameter_lable": ECC_parm("Duration_step", float),
                    "value_type" : float,
                    "element_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },   
                "Step_number": {
                    "parameter_lable": ECC_parm("Step_number", int), 
                    "value_type" : int,
                    "min_value" : 0,
                    "max_value" : 0,
                    "unit" : None
                },       
                "Record_every_dT": {
                    "parameter_lable": ECC_parm("Record_every_dT", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },
                "Record_every_dI": {
                    "parameter_lable": ECC_parm("Record_every_dI", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 1,
                    "unit" : "A"
                },
                "Final_frequency": { 
                    "parameter_lable": ECC_parm("Final_frequency", float), 
                    "value_type": float, 
                    "min_value" : 0,
                    "max_value" : 1000000000,
                    "unit" : None
                },
                "Initial_frequency": { 
                    "parameter_lable": ECC_parm("Initial_frequency", float), 
                    "value_type": float, 
                    "min_value" : 0,
                    "max_value" : 1000000000,
                    "unit" : None
                },
                "Sweep": { 
                    "parameter_lable": ECC_parm("sweep", bool), 
                    "value_type": bool,
                    "unit" : None
                },
                "Amplitude_Voltage": { 
                    "parameter_lable": ECC_parm("Amplitude_Voltage", float), 
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 10,
                    "unit" : "V"
                },
                "Frequency_number": { 
                    "parameter_lable": ECC_parm("Frequency_number", int), 
                    "value_type" : int,
                    "min_value" : 1,
                    "max_value" : 100000,
                    "unit" : None
                },
                "Average_N_times": { 
                    "parameter_lable": ECC_parm("Average_N_times", int), 
                    "value_type" : int,
                    "min_value" : 1,
                    "max_value" : 100000,
                    "unit" : None
                },
                "Correction": { 
                    "parameter_lable": ECC_parm("Correction", bool), 
                    "value_type" : bool,
                    "unit" : None
                },
                "Wait_for_steady": { 
                    "parameter_lable": ECC_parm("Wait_for_steady", float), 
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : None
                },
            },
            "cplimit": {
                "Current_step": {
                    "parameter_lable": ECC_parm("Current_step", float),
                    "value_type" : list,
                    "len_list_range" : range(0,20),
                    "element_type" : float,
                    "min_value" : -1,
                    "max_value" : 1,
                    "unit" : "A"
                },  
                "vs_initial":{
                    "parameter_lable": ECC_parm("vs_initial", bool),
                    "value_type" : list,
                    "len_list_range" : range(0,20),
                    "element_type" : bool,
                    "unit" : None
                },
                "Duration_step": {
                    "parameter_lable": ECC_parm("Duration_step", float),
                    "value_type" : list,
                    "len_list_range" : range(0,20),
                    "element_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },   
                "Step_number": {
                    "parameter_lable": ECC_parm("Step_number", int), 
                    "value_type" : int,
                    "min_value" : 0,
                    "max_value" : 19,
                    "unit" : None
                },       
                "Record_every_dT": {
                    "parameter_lable": ECC_parm("Record_every_dT", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },
                "Record_every_dE": {
                    "parameter_lable": ECC_parm("Record_every_dE", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 10,
                    "unit" : "V"
                },
                "N_Cycles": {
                    "parameter_lable": ECC_parm("N_Cycles", int),
                    "value_type" : int,
                    "min_value" : 0,
                    "max_value" : 1000,
                    "unit" : None
                },
                "Test1_Config": {
                    "parameter_lable": ECC_parm("Test1_Config", int),
                    "value_type" : list,
                    "len_list_range" : range(0,20),
                    "element_type" : int,
                    "min_value" : 0,
                    "max_value" : 124,
                    "unit" : None
                },
                "Test1_Value": {
                    "parameter_lable": ECC_parm("Test1_Value", float),
                    "value_type" : list,
                    "len_list_range" : range(0,20),
                    "element_type" : float,
                    "min_value" : -10000,
                    "max_value" : 50000,
                    "unit" : None
                },
                "Test2_Config": {
                    "parameter_lable": ECC_parm("Test2_Config", int),
                    "value_type" : list,
                    "len_list_range" : range(0,20),
                    "element_type" : int,
                    "min_value" : 0,
                    "max_value" : 124,
                    "unit" : None
                },
                "Test2_Value": {
                    "parameter_lable": ECC_parm("Test2_Value", float),
                    "value_type" : list,
                    "len_list_range" : range(0,20),
                    "element_type" : float,
                    "min_value" : -10,
                    "max_value" : 10,
                    "unit" : None
                },   
                "Test3_Config": {
                    "parameter_lable": ECC_parm("Test3_Config", int),
                    "value_type" : list,
                    "len_list_range" : range(0,20),
                    "element_type" : int,
                    "min_value" : 0,
                    "max_value" : 124,
                    "unit" : None
                },
                "Test3_Value": {
                    "parameter_lable": ECC_parm("Test3_Value", float),
                    "value_type" : list,
                    "len_list_range" : range(0,20),
                    "element_type" : float,
                    "min_value" : -10,
                    "max_value" : 10,
                    "unit" : None
                },     
                "Exit_Cond": {
                    "parameter_lable": ECC_parm("Exit_Cond", int),
                    "value_type" : list,
                    "len_list_range" : range(0,20),
                    "element_type" : int,
                    "min_value" : 0,
                    "max_value" : 2,
                    "unit" : None
                },        
                "I_Range": {
                    "parameter_lable": ECC_parm("I_Range", int),
                    "value_type" : int,
                    "min_value" : 1,
                    "max_value" : 11,
                    "unit" : None
                },
            },
            "dpa": {
                "Initial_Potential": {
                    "parameter_lable": ECC_parm("Ei", float),
                    "value_type" : float,
                    "min_value" : -1,
                    "max_value" : 1,
                    "unit" : "V"
                },  
                "Initial_Potential_Vs_Initial_One":{
                    "parameter_lable": ECC_parm("OCi", bool),
                    "value_type" : bool,
                    "unit" : None
                },
                "Ei_Duration": {
                    "parameter_lable": ECC_parm("Rest_time_Ti", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },   
                "Prepulse_height": {
                    "parameter_lable": ECC_parm("PPH", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "mV"
                },
                "Prepulse_width": {
                    "parameter_lable": ECC_parm("PPW", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "ms"
                },
                "Pulse_height": {
                    "parameter_lable": ECC_parm("PH", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "mV"
                },
                "Pulse_width": {
                    "parameter_lable": ECC_parm("PW", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "ms"
                },
                "Period": {
                    "parameter_lable": ECC_parm("P", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "mV"
                },
                "Duration": {
                    "parameter_lable": ECC_parm("Tp", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 100000,
                    "unit" : "s"
                },
                "Begin_measuring_I": {
                    "parameter_lable": ECC_parm("Begin_measuring_I", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 1,
                    "unit" : "ms"
                },
                "End_measuring_I": {
                    "parameter_lable": ECC_parm("End_measuring_I", float),
                    "value_type" : float,
                    "min_value" : 0,
                    "max_value" : 1,
                    "unit" : "ms"
                },
                "I_Range": {
                    "parameter_lable": ECC_parm("I_Range", int),
                    "value_type" : int,
                    "min_value" : -10,
                    "max_value" : 10,
                    "unit" : None
                }
            },
        }