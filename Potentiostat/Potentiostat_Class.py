#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [Potentiostat] Class for controlling Potentiostat (Biologic VSP-3e)
# @author   Daeho Kim (r4576@kist.re.kr)

"""
This module provides a Python interface to the Biologic VSP-3e that operates
using the EC-lab development package developed by CSRC of the Korea Institute of Science and Technology. 
The module has been developed based on the references, ex_tech_cp.py, and ex_tech_cv.py
The command implementation is based on the instruction manual 
'EC-Lab® Development Package User's Guide Version 6.04'
"""

import os, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Potentiostat")))
import time

import Potentiostat.kbio.kbio_types as KBIO
from Potentiostat.kbio.kbio_api import KBIO_api
from Potentiostat.kbio.c_utils import c_is_64b
from Potentiostat.kbio.utils import exception_brief
from Potentiostat.kbio.kbio_tech import *

from Potentiostat_Params import PotentiostatParams

import os, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Potentiostat")))


import json

from Device_Exception import DeviceError
from Log.Logging_Class import NodeLogger
from BaseUtils.Preprocess import PreprocessJSON
from datetime import datetime 

        
class VSP3E(PotentiostatParams, PreprocessJSON):
    """
    [VSP-3e] VSP-3e Potentiostat Class for controlling in another computer (windows)

    # Variable
    :param logger_obj (obj): set logging object (from Logging_class import Loggger) 
    :param device_name="VSP-3e" (str): set sonic bath model name (log name)
    :param channel (int): set potentiostat channel
    
    """
    
    def __init__(self, logger_obj, device_name="VSP-3e"):
        #logger object
        self.logger_obj=logger_obj

        self.info = {
        "address" : "192.109.209.128",
        "binary_path" : "./Potentiostat/EC_Lab_Development_Package/",
        "electrode" : {
            "Working" : "GCE",
            "Refernece" : "Ag/AgCl",
            "Counter" : "Pt"
        }}
        # device settings
        self.device_name = device_name
        self.address = "192.109.209.128"
        self.binary_path = "./Potentiostat/EC_Lab_Development_Package/"
        self.api = self._setAPI()
        self.version = self.api.GetLibVersion()
        self.id, self.device_info = self.api.Connect(self.address)
        self.is_VMP3 = self.device_info.model in KBIO.VMP3_FAMILY
        PotentiostatParams.__init__(self)


    def _setAPI(self,):
        """
        set potentiostat api

        :return: api
        """
        if c_is_64b :
            DLL_file = "EClib64.dll"
        else :
            DLL_file = "EClib.dll"

        DLL_path = self.binary_path + DLL_file

        api = KBIO_api(DLL_path)

        return api
        
    
    def _selectTechfile(self,techname):
        """
        set electrochemical analysis techfile

        :param techname (str): operating technme

        :return: techfile of each method
        """
        techname3_tech_file   = techname + ".ecc"
        techname4_tech_file   = techname + "4.ecc"

        tech_file = techname3_tech_file if self.is_VMP3 else techname4_tech_file

        return tech_file    
        
    def loadKernel(self,channels:set):
        """
        load Kernel of potentiostat

        before using potentiostat, kernel must be open

        never open the kernel during evaluation in progress
        """
        load_firmware = True
        
        if self.is_VMP3 :
            firmware_path = "kernel.bin"
            fpga_path     = "Vmp_ii_0437_a6.xlx"
        # elif self.is_VMP300 :
        #     firmware_path = "kernel4.bin"
        #     fpga_path     = "vmp_iv_0395_aa.xlx"
        
        else :
            firmware_path = None

        if firmware_path :
            msg = (f"Potentiostat loading kernel --> Loading {firmware_path} ...")
            self.logger_obj.debug(self.device_name, msg)
            # create a map from channel set
            channel_map = self.api.channel_map(channels)
            # BL_LoadFirmware
            self.api.LoadFirmware(self.id, channel_map, firmware=firmware_path, fpga=fpga_path, force=load_firmware)
            msg = "Firmware loaded"
            self.logger_obj.debug(self.device_name, msg)

    def connectChannel(self,):
        """
        Connect to the channel of potentiostat
        
        :return: id --> (int)
        """
        id = self.id
        print("device id")
        
        return id
    

    def disconnectChannel(self,):
        """
        disconnect from the channel of potentiostat
        """
        self.api.Disconnect(self.id)
     
    

class VSP3EChannel(VSP3E, PotentiostatParams, DeviceError, PreprocessJSON) :

    def __init__(self, logger_obj, channel:int=1, device_name="VSP-3e"):
        """
        [VSP-3e Channel] VSP-3e Potentiostat Channel Class for controlling in another computer (windows)

        # Variable
        :param logger_obj (obj): set logging object (from Logging_class import Loggger) 
        :param device_name="VSP-3e" (str): set sonic bath model name (log name)
        :param channel (int): set potentiostat channel
        
        """
        #logger object
        self.logger_obj=logger_obj
        
        # device setting
        self.channel = channel
        VSP3E.__init__(self, logger_obj, device_name)
        PotentiostatParams.__init__(self)
        self.device_ch_name = self.device_name + f"[CH{channel}]"

    def heartbeat(self):

        connction = self._checkConnection()
        self.loadKernel({1,2,3,4})
        debug_device_name="{} ({})".format(self.device_name, "heartbeat")
        debug_msg="Hello World!! Succeed to connection to main computer!"
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)
        
        return_res_msg="[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg

    def _checkConnection(self,):
        """ 
        check potentiostat connection

        :return: error_code --> (int)
        """
        if self.api.TestConnection(self.id) :
            error_code = 0
        else :
            error_code = 1
            self.raiseError(0,self.ERROR_DICT(error_code))
        return error_code

    def _makeParam(self, dict_name ,param_dict) :
        """ 
        set format of parameters

        :param dict_name (str): operation parameter dictionnary name
        :param param_dict (dict): hardware of method parameter dictionary

        :return: prased row list --> (list)
        """
        params = []

        for key in param_dict :
            value = param_dict[key]
            param_lable = self.PARAMETERS[dict_name][key]['parameter_lable']

            if type(value) == list :
                for i in range(len(value)) :                 
                    param = make_ecc_parm(self.api, param_lable, value[i], i)
                    params.append(param)
            else :
                param = make_ecc_parm(self.api, param_lable, value)    
                params.append(param)
        
        return params

    def _makeParams(self, param_file) :
        """ 
        set format of parameters array

        :param param_file (dict): parameter dictionary
        
        :return: prased row list --> (list)
        """
        techname = param_file['techname']
        tech_param_dict = param_file['parameter']['tech']
        hardware_param_dict = param_file['parameter']['hardware']

        param_list = self._makeParam(techname, tech_param_dict) + self._makeParam('hardware',hardware_param_dict)
        
        return param_list
    

    def _computeTimestamp(self, row, current_values):
        """ 
        process time signal from potentiostat 

        :param row (list): operation response 
        :param current_values (float): current values

        :return: computed time --> (float)
        """
        t_high = row[0]
        t_low = row[1]        
        time_rel = (t_high << 32) + t_low
        computed_time = current_values.TimeBase * time_rel

        return computed_time

    def _checkRecodeLength(self, techname ,nb_words, length):
        """ 
        check signal length from potentiostat

        :param techname (str): techname 
        :param nb_words (int): real response length
        :param length (int): tech response length
        """
        if nb_words != length :
            raise RuntimeError(f"{techname} : unexpected record length ({nb_words})")

    def _processData(self, techname, row, current_values) :
        """ 
        process return signal form potentiostat

        Supporting evaluation method : CP, CA, OCV, CV, LSV, PEIS

        :param techname (str): techname 
        :param row (list): operation response 
        :param current_values (float): current values

        :return: prased row --> (dict)
        """
        nb_words = len(row)
        if techname == 'ocv' :
            # vmp3 이기 때문에 length = 4
            length = 4
            nb_words == length
            self._checkRecodeLength(techname, nb_words, length)

            # compute timestamp in seconds
            computed_time = self._computeTimestamp(row, current_values)
            # Ewe is a float
            Ewe = self.api.ConvertNumericIntoSingle(row[2])+0.699
            
            parsed_row = {'t': computed_time , 'Ewe': Ewe}
            
            if nb_words == length :
                # Ece is a float
                Ece = self.api.ConvertNumericIntoSingle(row[3])
                parsed_row['Ece'] = Ece
            
        elif techname == 'cp' or techname == 'ca'  or techname == 'cplimit':
            
            length = 5
            self._checkRecodeLength(techname, nb_words, length)
            
            # compute timestamp in seconds
            computed_time = self._computeTimestamp(row, current_values)
            # Ewe is a float
            Ewe = self.api.ConvertNumericIntoSingle(row[2])+0.699
            # current is a float
            I = self.api.ConvertNumericIntoSingle(row[3])
            # technique cycle is an integer
            cycle = row[4]
            # current density
            J = I*1000/0.196            

            parsed_row = {'t': computed_time , 'Ewe': Ewe, 'I': I, 'cycle': cycle, 'J':J}

        elif techname == 'cv' :
            
            length = 6
            self._checkRecodeLength(techname, nb_words, length)
            
            # compute timestamp in seconds
            computed_time = self._computeTimestamp(row, current_values)
            # current is a float
            Ec = self.api.ConvertNumericIntoSingle(row[2])
            # current is a float
            I = self.api.ConvertNumericIntoSingle(row[3])
            # Ewe is a float
            Ewe = self.api.ConvertNumericIntoSingle(row[4])+0.699
            # technique cycle is an integer
            cycle = row[5]
            # current density
            J = I*1000/0.196

            parsed_row = {'t': computed_time , 'Ec': Ec, '<I>': I, 'Ewe': Ewe, 'cycle': cycle, 'J':J}
            
        elif techname == 'lp' :
            if nb_words == 3:
                computed_time = self._computeTimestamp(row, current_values)
                # current is a float
                Ewe = self.api.ConvertNumericIntoSingle(row[2])

                parsed_row = {'t':computed_time , 'Ec': None, '<I>': 0, 'Ewe': Ewe, 'J':0}
                return 'OCV operating..'
            

            elif nb_words == 5:
            
                # compute timestamp in seconds
                computed_time = self._computeTimestamp(row, current_values)
                # current is a float
                Ec = self.api.ConvertNumericIntoSingle(row[2])
                # current is a float
                I = self.api.ConvertNumericIntoSingle(row[3])
                # Ewe is a float
                Ewe = self.api.ConvertNumericIntoSingle(row[4])+0.699
                J = I*1000/0.196

                parsed_row = {'t': computed_time , 'Ec': Ec, '<I>': I, 'Ewe': Ewe, 'J':J}

        elif techname == 'peis' :

            length = 15
            self._checkRecodeLength(techname, nb_words, length)
            
            # compute timestamp in seconds
            freq = self.api.ConvertNumericIntoSingle(row[0])
            # Ewe is a float
            M_Ewe = self.api.ConvertNumericIntoSingle(row[1])
            # current is a float
            M_I = self.api.ConvertNumericIntoSingle(row[2])
           
            Zwe = self.api.ConvertNumericIntoSingle(row[3])
            # +0.27421
            Ewe = self.api.ConvertNumericIntoSingle(row[4])+0.699
           
            I = self.api.ConvertNumericIntoSingle(row[5])
            
            M_Ece = self.api.ConvertNumericIntoSingle(row[7])
            
            M_Ice = self.api.ConvertNumericIntoSingle(row[8])

            Zce = self.api.ConvertNumericIntoSingle(row[9])

            Ece = self.api.ConvertNumericIntoSingle(row[10])

            t = self.api.ConvertNumericIntoSingle(row[13])

            IRange = self.api.ConvertNumericIntoSingle(row[14])

            # current density
            J = I*1000/0.196            

            parsed_row = {'t': t , 'freq': freq ,'M_Ewe': M_Ewe, 'M_I': M_I, 'Zwe': Zwe, 'Ewe': Ewe, 'I': I, 'M_Ece': M_Ece, 'M_Ice': M_Ice, 'Zce': Zce, 'Ece': Ece,'IRange': IRange,'J':J}

        
        elif techname == 'dpa' :
            
            length = 5
            self._checkRecodeLength(techname, nb_words, length)
            
            # compute timestamp in seconds
            computed_time = self._computeTimestamp(row, current_values)
            # current is a float
            I = self.api.ConvertNumericIntoSingle(row[3])
            # Ewe is a float
            Ewe = self.api.ConvertNumericIntoSingle(row[2])+0.699
            # technique cycle is an integer
            q = row[4]
            # current density
            J = I*1000/0.196

            parsed_row = {'t': computed_time, '<I>': I, 'Ewe': Ewe, 'Q': q, 'J':J}

        return parsed_row

        
    def _getExperimentData (self, data, techname):
        """ 
        get return signal form potentiostat

        :param data 
        :param techname (str): techname 
        
        :return: prased row list --> (list)
        """
        current_values, data_info, data_record = data

        ix = 0

        parsed_row_list = list()

        for _ in range(data_info.NbRows) :
            
            # progress through record
            inx = ix + data_info.NbCols     
            # extract timestamp and one row
            row = data_record[ix:inx]
            parsed_row = self._processData(techname, row, current_values)

            if type(parsed_row) != str :
                parsed_row_list.append(parsed_row)

            else :
                pass
            
            print("{} operating : {}".format(techname.upper() ,parsed_row))
            
            ix = inx

        return parsed_row_list

    def _loopExperiment(self,techname, params, channel, verbosity: int):
        """
        loop operating method

        :param techname (str): techname
        :param params : input param values
        :verbosity (int): verbosity of function
        
        :return: raw_data --> (list)
        """
        tech_file = self._selectTechfile(techname)        

        ecc_params = make_ecc_parms(self.api,*params)

        self.api.LoadTechnique(self.id, channel, tech_file, ecc_params, first=True, last=True, display=(verbosity>1))

        self.api.StartChannel(self.id, channel)

        raw_data = []

        while True :

            # BL_GetData
            self.api.GetParamInfos
            data = self.api.GetData(self.id, channel)
            status = get_status(self.api, data)
            result = self._getExperimentData(data, techname)
            raw_data += result
            if status == 'STOP' :
                break

            time.sleep(1)
        
        return raw_data

    def popChannelInfo(self,):
        """
        pop potentiostat channel info

        :return: channel info
        """
        channel_info = self.api.GetChannelInfo(self.id,self.channel)

        return channel_info
    
    def popExperimentInfo(self,data) :
        """ 
        pop experiment info

        :param data : self.api.GetData(self.id, channel)

        :return: experiment info --> (dict)
        """
        current_values, data_info, data_record = data

        status = KBIO.PROG_STATE(current_values.State).name

        tech_name = TECH_ID(data_info.TechniqueID).name

        # synthetic info for current record
        info = {
        'tb': current_values.TimeBase,
        'ix': data_info.TechniqueIndex,
        'tech': tech_name,
        'proc': data_info.ProcessIndex,
        'loop': data_info.loop,
        'skip': data_info.IRQskipped,
        }

        return info

    def debugDict(self, param_dict):
        """ 
        debug operation script

        :param param_dict (dict): operation dict

        :return: error_code --> (int)
        """
        
        techname = param_dict["techname"]
        error_code = 0
        list_len_count = []

        for params, value in param_dict["parameter"]["tech"].items() :
            dict_validator = self.PARAMETERS[techname][params]
            error_msg = "An error has occurred in the operation script. Check Parameter : {}".format(params)

            if type(value) == list :
                list_condition = len(value) in dict_validator["len_list_range"]
                self.checkCondition(list_condition, error_code=4, error_msg=error_msg)
                list_len_count.append(len(value))
                if len(set(list_len_count)) == 1 :
                    pass
                else :
                    error_code = 4
                    self.raiseError(error_code,error_msg)

                for element in value :
                    if type(element) == bool :
                        value_condition = type(element) == dict_validator["element_type"]
                        self.checkCondition(value_condition, error_code=4, error_msg=error_msg)
                    
                    elif type(element) in [int, float]:
                        value_condition = element >= dict_validator["min_value"] and element <= dict_validator["max_value"]
                        self.checkCondition(value_condition, error_code=4, error_msg=error_msg)
                    
            elif type(value) == bool :
                value_condition = type(value) == dict_validator["value_type"]
                self.checkCondition(value_condition, error_code=4, error_msg=error_msg)
                    
            elif type(value) in [int, float]:
                value_condition = value >= dict_validator["min_value"] and value <= dict_validator["max_value"]
                self.checkCondition(value_condition, error_code=4, error_msg=error_msg)

            else :
                error_code = 4
                self.raiseError(error_code,error_msg)

        return error_code


    def mergeData(self,data):
        """ 
        merge raw data

        :param data (dict): raw result data

        :return: merged result data --> (dict)
        """
        merged_data = {} 
        
        for entry in data:
            for key, value in entry.items():
                if key not in merged_data:
                    merged_data[key] = []
                merged_data[key].append(value)
        
        return merged_data
    
    def saveData(self,filename,data):
        """ 
        debug operation json script

        :param filename (str): save file name
        :param data (dict): result data

        :return: error_code --> (int)
        """
        current_date = datetime.now().strftime("%m%d")

        current_time = datetime.now().strftime("%Y%m%d%H%M")

        folder_path = f'../EVALUATIONPLATFORM/Potentiostat/result/{current_date}'

        os.makedirs(folder_path, exist_ok=True)

        filepath = f'{folder_path}/{current_time}_{filename}.json'
        self.writeJSON(filepath, data)

    
    def operate(self, param_dict, verbosity: int = 2, mode_type='virtual'):
        """ 
        start electrochemical analysis
        available method : OCV, CA, CP, CV, LSV, PEIS

        :param dict (dict): operation parameter dictionary
        :param verbosity (int): verbosity of function. (If the verbosity is 2 or higher, popup window will emerge.)
        :param mode_type="virtual" (str): set virtual or real mode

        :return: res_msg --> (str)
        """
        debug_device_name="{} ({})".format(self.device_ch_name, mode_type)
        
        techname = param_dict["techname"]
        self.debugDict(param_dict)
        msg = "Potentiostat Operation ... Techname : {}".format(techname.upper())
        self.logger_obj.debug(debug_device_name, msg)
            
        if mode_type == "real" :
            self._checkConnection()
            status = self.api.GetChannelInfo(self.id,self.channel).state
            error_dict = self.checkStatusError("STOP",status)
            msg = "Potentiostat Waiting? Receive signal! --> Waiting : {}, Status : {} ".format(bool(status == "STOP"), error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            # self.loadKernel({self.channel})
            # msg = "Potentiostat kernel loaded ... Channel : {}".format(self.channel)
            
            params = self._makeParams(param_dict)
            msg = "Parameter setting done".format(techname)
            self.logger_obj.debug(debug_device_name, msg)
            
            msg = "Potentiostat Start! --> Techname : {}".format(techname.upper())
            self.logger_obj.debug(debug_device_name, msg)
            result = self._loopExperiment(techname, params, self.channel, verbosity)
            merged_data = self.mergeData(result)

            self.saveData(techname.upper(), merged_data)

            status = self.api.GetChannelInfo(self.id,self.channel).state
            error_dict = self.checkStatusError('STOP',status)
            msg = "Potentiostat STOP? --> STOP : {}, Status : {}".format(bool(status=='STOP'),error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            msg= "Operation done, Techname: {}".format(techname.upper())
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
        
        elif mode_type == "virtual" :
            msg = "Potentiostat Start! --> Techname : {}".format(techname.upper())
            self.logger_obj.debug(debug_device_name, msg)

            msg= "Operation done, Techname: {}".format(techname.upper())
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
        

if __name__ == "__main__" :    
    NodeLogger_obj = NodeLogger(platform_name="Electrochemical Analysis", setLevel="DEBUG",
                            SAVE_DIR_PATH="../EVALUATIONPLATFORM")
    
    BL_Potentiostat = VSP3E(logger_obj=NodeLogger_obj)

# 
    # BL_Potentiostat.loadKernel({2})

    # print(BL_Potentiostat.connectChannel())


    # channel_1 = VSP3EChannel(logger_obj=NodeLogger_obj, channel=2, device_name="VSP-3e")
    channel_1 = VSP3EChannel(logger_obj=NodeLogger_obj, channel=1, device_name="VSP-3e")

    channel_1.api.StopChannel(id_=channel_1.id, ch=1)

    # param_dict = '{"techname": "cv", "parameter": {"tech": {"vs_initial": [false, false, false, false, false], "Voltage_step": [0, -0.225, 0.825, 0, 0], "Scan_Rate": [0.2, 0.2, 0.2, 0.2, 0.2], "N_Cycles": 10, "Scan_number": 2, "Record_every_dE": 0.01, "Average_over_dE": false, "Begin_measuring_I": 0.5, "End_measuring_I": 1.0}, "hardware": {"I_Range": 12, "E_Range": 0, "Bandwidth": 5}}}'

    # # JSON 문자열을 파이썬 딕셔너리로 로드
    # dict_data = json.loads(param_dict)
    # print(dict_data)
    # res_msg = channel_1.heartbeat()

    param_dict ={
        "__comment__": "example parameter of cp tech",
        "techname" : "cplimit",
        "parameter" : {
            "tech" : {
                "Current_step": [0.0001],
                "vs_initial": [False],
                "Duration_step" : [10],
                "Step_number": 0,
                "Record_every_dT": 0.1,
                "Record_every_dE": 0.1,
                "N_Cycles" : 0,
                "Test1_Config" : [5],
                "Test1_Value" : [0.500],
                "Exit_Cond" : [0]
            },
            "hardware" : {
                "I_Range" : 6
            }
        }
    }
    

        
    # # dict_data = json.loads(param_dict)
    # print(param_dict)
    
    # # param_json = channel_1.openJSON('../EVALUATIONPLATFORM/Potentiostat/protocol/example.json')['CV_example']

    # try:
       

    #     dataset_1 = channel_1.operate(param_dict=param_dict, mode_type="real")

    #     BL_Potentiostat.api.Disconnect(BL_Potentiostat.id)

        

    # except KeyboardInterrupt :
    #     print(".. interrupted")

    # except Exception as e :
    #     print(f"{exception_brief(e, True)}")
