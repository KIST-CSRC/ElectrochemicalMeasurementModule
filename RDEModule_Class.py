#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [RDEmodule] Class for orchestrating RDE workflow (RDE0 config)
# @author   Daeho Kim (r4576@kist.re.kr)

"""
This module provides a Python interface to orchestrate an RDE workflow using
multiple devices (Actuator, Rotator, MFC, Pump, Powerbox, Sonic, Microscope, RTU, TCP nodes).
Ports and device settings are managed by a single dictionary key (e.g., "RDE0": {...}).

Design style follows the SonorexDigitec driver pattern:
- logger_obj based logging
- function_param validation
- heartbeat / virtual vs real operation mode
- internal safe shutdown helpers
"""

import os, sys, time
from typing import Optional, Dict, Any

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
)

from Log.Logging_Class import NodeLogger
from Device_Exception import DeviceError

from Potentiostat.Potentiostat_Class import VSP3EChannel
from RDErotator.RDE_Rotator_Class import RC_10K
from MFC.MFC_Class import WIZ_701
from Pump.Pump_Class import Next3000FJ
from RDEactuator.RDE_Actuator_Class import RDEMotionController
from Powerbox.Powerbox_Class import Powerbox3PF
from Sonic.Sonic_Class import SonorexDigitec
from Polishing.PolishingTool import PolishingTool
from Microscope.Microscope import CN_X4_500
from RobotTransferUnit.RobotTransferUnit_Class import RobotTransferUnit
from BaseUtils.TCP_Node import TCP_Class

import json

class RDEmodule(DeviceError):
    """
    [RDEmodule] RDE orchestration class

    # Variable
    :param logger_obj (obj): set logging object (from Logging_class import NodeLogger)
    :param device_name="RDEmodule" (str): set log device name
    :param ports (dict): port/config bundle in the form {"RDE0": {...}}
    :param node_key="RDE0" (str): select which bundle to use
    :param jsonfile (dict): evaluation recipe (optional)
    """

    def __init__(
        self,
        logger_obj: NodeLogger,
        node_key: int = 0,
        device_name: str = "RDEmodule",
        jsonfile: Optional[Dict[str, Any]] = None,
        kbio_relpath: str = "./Potentiostat/kbio",
        ):
        self.logger_obj = logger_obj
        self.device_name = device_name
        self.node_key = node_key
        self.jsonfile = jsonfile or {}

        self.ports = {
            "RDE0": {
                "RDEACTUATOR": {"r_ser_port": "COM4", "xz_ser_port": "COM3"},
                "MFC": {"ser_port": "COM12"},
                "PUMP0": {"ser_port": "COM7"},
                "SONIC": {"ser_port": "COM5"},
                "POWERBOX": {"ip": "192.168.1.201"},
                "POTENTIOSTAT": {"device_name": "VSP-3e", "channel": 1},
                "RDEROTOR": {"resource":"ASRL8::INSTR"},
                "MICROSCOPE": {"index":0},
                "POLISHINGTOOL": {"waterpump_ser" : "COM10", "solutionPump_ser" : "COM11", "rotor_ser" : "COM9",}
            }
        }

        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), kbio_relpath)))

        if self.node_key not in self.ports:
            raise KeyError(f"ports에 '{self.node_key}' 키가 없습니다. 사용 가능 키: {list(self.ports.keys())}")

        self.info = self.ports[self.node_key]

        self.RDEACTUATOR_obj = RDEMotionController(self.logger_obj, r_ser_port=self.info["RDEACTUATOR"]["r_ser_port"], xz_ser_port=self.info["RDEACTUATOR"]["xz_ser_port"])
        self.MFC_obj = WIZ_701(self.logger_obj, ser_port=self.info["MFC"]["ser_port"])
        self.PUMP_obj_0 = Next3000FJ(self.logger_obj, ser_port=self.info["PUMP0"]["ser_port"])
        self.SONIC_obj = SonorexDigitec(self.logger_obj, ser_port=self.info["SONIC"]["ser_port"])

        self.SOLENOID_obj = Powerbox3PF(self.logger_obj, device_name="Sol Valve", ip=self.info["POWERBOX"]["ip"], socket=1)
        self.IRLAMP_obj = Powerbox3PF(self.logger_obj, device_name="Ir lamp", ip=self.info["POWERBOX"]["ip"], socket=3)
        self.HUMIDIFIER_obj = Powerbox3PF(self.logger_obj, device_name="Humidifier", ip=self.info["POWERBOX"]["ip"], socket=2)

        self.POTENTIOSTAT_obj = VSP3EChannel(self.logger_obj, channel=self.info["POTENTIOSTAT"]["channel"], device_name=self.info["POTENTIOSTAT"]["device_name"])
        self.RDEROTOR_obj = RC_10K(self.logger_obj, resource=self.info["RDEROTOR"]["resource"])
        self.MICROSCOPE_obj = CN_X4_500(self.logger_obj, camera_index=self.info["MICROSCOPE"]["index"])
        self.POLISHINGTOOL_obj = PolishingTool(self.logger_obj, Rotor_ser_port= self.info["POLISHINGTOOL"]["rotor_ser"], SolutionPump_ser_port= self.info["POLISHINGTOOL"]["solutionPump_ser"], WaterPump_ser_port= self.info["POLISHINGTOOL"]["waterpump_ser"])

        self.DEVICES = {
            "RDEACTUATOR": self.RDEACTUATOR_obj,
            "MFC": self.MFC_obj,
            "PUMP": self.PUMP_obj_0,
            "SONIC": self.SONIC_obj,
            "SOLENOID": self.SOLENOID_obj,
            "IRLAMP": self.IRLAMP_obj,
            "HUMIDIFIER": self.HUMIDIFIER_obj,
            "POTENTIOSTAT": self.POTENTIOSTAT_obj,
            "RDEROTOR": self.RDEROTOR_obj,
            "MICROSCOPE": self.MICROSCOPE_obj,
            "POLISHINGTOOL": self.POLISHINGTOOL_obj,
        }

    def heartbeat(self, input_client_socket=None, base_tcp_node_obj=None, input_hardware_name="RDEMODULE", input_action_type="heartbeat"):
        
        debug_device_name = "{} ({})".format(self.device_name, "heartbeat")

        res_dict = {}
        for name, dev in self.DEVICES.items():
            try:
                res_dict[name] = dev.heartbeat()
            except Exception as e:
                res_dict[name] = "heartbeat failed: {}".format(e)

        debug_msg = "Hello World!! Succeed to create RDEmodule and initialize devices!"
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)
        
        return_res_msg="[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg
        
    # =============================================================================
    #                              Workflow steps
    # =============================================================================

    def setupCell(self, pump_time=45, pump_rpm=300, mfc_flow=300, mode_type="virtual"):
        debug_device_name = "{} ({})".format(self.device_name, mode_type)

        msg = f"Setup Cell: Pump ({pump_time}s, {pump_rpm}), MFC ({mfc_flow})"

        self.logger_obj.debug(debug_device_name, msg)

        self.PUMP_obj_0.operate(pump_time, pump_rpm, mode_type)
        self.MFC_obj.startDevice(mfc_flow, mode_type)

        res_msg = debug_device_name + " : " + msg
        return res_msg
    
    def moveRDE(self, position, speed=8000, mode_type="virtual"):
        debug_device_name = "{} ({})".format(self.device_name, mode_type)

        msg = f"Move RDE: Move (position={position}, speed={speed})"
        self.logger_obj.debug(debug_device_name, msg)
        
        self.RDEACTUATOR_obj.move2Position(position, int(speed), mode_type)
        
        res_msg = debug_device_name + " : " + msg
        return res_msg
    
    def prepareElectrode(self, speed=8000, dry_rpm=450, dry_time=10, microscope_time=5, humid_time=10, mode_type="virtual", retry_count=0, max_retries=5):
        debug_device_name = "{} ({})".format(self.device_name, mode_type)

        msg = f"Prepare Electrode: Dry (rpm={dry_rpm}, time={dry_time}), Humid (time={humid_time})"
        self.logger_obj.debug(debug_device_name, msg)
        
        self.RDEACTUATOR_obj.move2Position("Microscope", int(speed), mode_type)
        msg, status = self.MICROSCOPE_obj.operate("casting", microscope_time, mode_type)
        
        if status == "Failure":
            retry_count += 1
            msg = f"Casting Failed! (Attempt {retry_count}/{max_retries})"
            self.logger_obj.debug(debug_device_name, msg)
            
            if retry_count >= max_retries:
                error_msg = f"Electrode preparation failed after {max_retries} attempts. Stopping sequence."
                self.logger_obj.debug(debug_device_name, error_msg)
                raise Exception(error_msg)
            
            self.polishElectrode(speed=8000, polish_cycles=1, polish_time=10, sonic_time=10, sonic_rpm=1600, mode_type=mode_type)
            
            self.RDEACTUATOR_obj.move2Position("IrLamp", int(speed), mode_type)
            self.RDEROTOR_obj.startDevice(dry_rpm=1600, mode_type=mode_type)
            self.IRLAMP_obj.operate(dry_time=30, mode_type=mode_type)
            self.RDEROTOR_obj.stopDevice(mode_type)

            self.prepareElectrode(speed, dry_rpm, dry_time, microscope_time, humid_time, mode_type, retry_count, max_retries)
            return

        self.logger_obj.debug(debug_device_name, msg)
                
        self.RDEACTUATOR_obj.move2Position("IrLamp", int(speed), mode_type)
        self.RDEROTOR_obj.startDevice(dry_rpm, mode_type)
        self.IRLAMP_obj.operate(dry_time, mode_type)
        self.RDEROTOR_obj.stopDevice(mode_type)

        self.RDEACTUATOR_obj.move2Position("Microscope", int(speed), mode_type)
        self.MICROSCOPE_obj.operate("drying", microscope_time, mode_type)

        self.RDEACTUATOR_obj.move2Position("Humidifier", int(speed), mode_type)
        self.HUMIDIFIER_obj.operate(humid_time, mode_type)

        res_msg = debug_device_name + " : Electrode preparation succeeded"
        return res_msg
    
    def startEvaluation(self, speed=8000, eval_rpm=1600, param_dict_list:list  = None, solenoid_time=60, mode_type="virtual"):
        debug_device_name = "{} ({})".format(self.device_name, mode_type)

        msg = f"Start Evaluation : Electrochemical test (RPM={eval_rpm}, param={param_dict_list}) "
        self.logger_obj.debug(debug_device_name, msg)

        self.RDEACTUATOR_obj.move2Position("Cell", int(speed), mode_type)
        self.RDEROTOR_obj.startDevice(eval_rpm, mode_type)
        
        for param_dict in param_dict_list :
            for iteration in range(param_dict["iteration"]):
                self.POTENTIOSTAT_obj.operate((param_dict["protocol"]),verbosity=1,mode_type=mode_type)

        self.RDEROTOR_obj.stopDevice(mode_type)

        self.MFC_obj.stopDevice(mode_type)
        self.SOLENOID_obj.operate(solenoid_time, mode_type)

        res_msg = debug_device_name + " : " + msg
        return res_msg

    def polishElectrode(self, speed=8000, polish_cycles=1, polish_time=10, sonic_time=10, sonic_rpm=1600, mode_type="virtual"):
        debug_device_name = "{} ({})".format(self.device_name, mode_type)

        msg = f"Start Polishing : Polish (iter: {polish_cycles}) "
        self.logger_obj.debug(debug_device_name, msg)

        self.POLISHINGTOOL_obj.dispense("Solution", mode_type)

        for _ in range(polish_cycles):
            self.RDEACTUATOR_obj.move2Position("Polishing", int(speed), mode_type)
            self.POLISHINGTOOL_obj.polishing(polish_time, mode_type)

            self.RDEACTUATOR_obj.move2Position("Sonic", int(speed), mode_type)
            self.RDEROTOR_obj.startDevice(target_rpm=sonic_rpm, mode_type=mode_type)
            self.SONIC_obj.operate(target_time=sonic_time, target_temp=0, operation_mode="Degas_Off", mode_type=mode_type)
            self.RDEROTOR_obj.stopDevice(mode_type)

        self.RDEACTUATOR_obj.move2Position("Home", int(speed), mode_type)

        res_msg = debug_device_name + " : " + msg
        return res_msg

if __name__ == "__main__":
    NodeLogger_obj = NodeLogger(
        platform_name="ElectrochemicalAnalysis",
        setLevel="DEBUG",
        SAVE_DIR_PATH="../EVALUATIONPLATFORM"
    )


    rde = RDEmodule(logger_obj=NodeLogger_obj, node_key="RDE0")
    print(rde.heartbeat())
    # rde.setupCell()
    # rde.moveRDE(position="casting")
    # rde.prepareElectrode()
    # jsonfile_dict=[
    #         {"iteration":1,
    #         "protocol" :{"techname" : "cv",
    #             "parameter" : {
    #                 "tech" : {
    #                     "vs_initial" : [False,False,False,False,False],
    #                     "Voltage_step" : [0,-0.225,0.825,0,0],
    #                     "Scan_Rate" : [0.2,0.2,0.2,0.2,0.2],
    #                     "N_Cycles" : 10,  
    #                     "Scan_number" : 2,  
    #                     "Record_every_dE" : 0.01, 
    #                     "Average_over_dE" : False,
    #                     "Begin_measuring_I" : 0.5, 
    #                     "End_measuring_I" : 1.0
    #                     },
    #                 "hardware" : {
    #                     "I_Range" : 12,
    #                     "E_Range" : 0,
    #                     "Bandwidth" : 5
    #                 }
    #             }
    #         }},
    #         {"iteration":1,
    #         "protocol" :
    #             {"techname" : "lp",
    #             "parameter" : {
    #                 "tech" : {
    #                     "vs_initial_scan" : [False,False],
    #                     "Voltage_scan" : [0.725,1.525],
    #                     "Scan_Rate" : [0.1,0.01],
    #                     "Record_every_dEr" : 0.01,      
    #                     "Rest_time_T" : 1,
    #                     "Record_every_dTr" : 0.01,
    #                     "Scan_number" : 0,
    #                     "Record_every_dE" : 0.01,                
    #                     "Average_over_dE" : False,
    #                     "Begin_measuring_I" : 0.5,
    #                     "End_measuring_I" : 1.0
    #                     },
    #                 "hardware" : {
    #                     "I_Range" : 9,
    #                     "E_Range" : 2,
    #                     "Bandwidth" : 4
    #                 }
    #             }
    #         }}]
    # rde.polishElectorde()
    # # virtual
    # rde.operate(cycles=1, mode_type="virtual")

    # # virtual
    # # rde.operate(cycles=1, mode_type="virtual")
    # test =[
    #          {"iteration":1,
    #          "protocol" :{"techname" : "cv",
    #              "parameter" : {
    #                  "tech" : {
    #                      "vs_initial" : [False,False,False,False,False],
    #                      "Voltage_step" : [0,-0.225,0.825,0,0],
    #                      "Scan_Rate" : [0.2,0.2,0.2,0.2,0.2],
    #                      "N_Cycles" : 10,  
    #                      "Scan_number" : 2,  
    #                      "Record_every_dE" : 0.01, 
    #                      "Average_over_dE" : False,
    #                      "Begin_measuring_I" : 0.5, 
    #                      "End_measuring_I" : 1.0
    #                      },
    #                  "hardware" : {
    #                      "I_Range" : 12,
    #                      "E_Range" : 0,
    #                      "Bandwidth" : 5
    #                  }
    #              }
    #          }},
    #          {"iteration":1,
    #          "protocol" :
    #              {"techname" : "lp",
    #              "parameter" : {
    #                  "tech" : {
    #                      "vs_initial_scan" : [False,False],
    #                      "Voltage_scan" : [0.725,1.525],
    #                      "Scan_Rate" : [0.1,0.01],
    #                      "Record_every_dEr" : 0.01,      
    #                      "Rest_time_T" : 1,
    #                      "Record_every_dTr" : 0.01,
    #                      "Scan_number" : 0,
    #                      "Record_every_dE" : 0.01,                
    #                      "Average_over_dE" : False,
    #                      "Begin_measuring_I" : 0.5,
    #                      "End_measuring_I" : 1.0
    #                      },
    #                  "hardware" : {
    #                      "I_Range" : 9,
    #                      "E_Range" : 2,
    #                      "Bandwidth" : 4
    #                  }
    #              }
    #          }}]
    # json_str = json.dumps(test)

    # jsonfile_dict = json.loads(json_str)

    # rde.startEvaluation(param_dict_list=jsonfile_dict)
    
    # rde.startEvaluation(param_dict_list=jsonfile_dict)
