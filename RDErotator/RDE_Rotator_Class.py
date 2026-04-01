#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [RDE_Rotator] Class for controlling RDE
# @author   Daeho Kim (r4576@kist.re.kr)

"""
This module provides a Python interface to the RC-10k device that operates
using the SCPI protocol developed by CSRC of the Korea Institute of Science and Technology. 
The command implementation is based on the English manual 
'BluRev RDE/RRDE User Manual (BL RDE or BL RRDE/RC-10k v.2.2)', specifically on Page 27.
"""

import os, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from pyvisa import ResourceManager
from Log.Logging_Class import NodeLogger
from Device_Exception import DeviceError
import time

resource_manager = ResourceManager()

def ResourceQuery():
    """
    Before using the API, please verify that the device is connected to the resource
    """
    print(resource_manager.list_resources())

class RC_10K(DeviceError):
    """ 
    [RC-10K] Bio-Logic RC-10k Class for controlling in another computer (windows)


    # Variable
    :param logger_obj (obj): set logging object (from Logging_class import Loggger) 
    :param device_name="RC_10K" (str): set RDE controller model name (log name)
    :param resource_name="ASRL(int)::INSTR": set RDE controller USB port 
    
    """


    def __init__(self, logger_obj, device_name="RC_10K", resource="ASRL8::INSTR" ):
        #logger object
        self.logger_obj=logger_obj

        self.info ={
            "resource" : "ASRL8::INSTR"
        }

        # device setting
        self.device_name = device_name
        self.recallDevice = resource_manager.open_resource(resource)
        DeviceError.__init__(self, self.logger_obj, self.device_name) 

        # supported SPCI query
        self.ID_SCPI = "*IDN?"
        self.READ_SCPI = "READ?"
        self.QUERY_SETSPEED_SCPI = "SOURce:SPEed?"
        self.PID_KP_Q_SCPI = "SOURce:Pid:KP?"
        self.PID_KI_Q_SCPI = "SOURce:Pid:KI?"
        self.PID_KD_Q_SCPI = "SOURce:Pid:KD?"

        #supported SPCI write
        self.RESET_SCPI = "*Reset"
        self.START_SCPI = "SOURce:Start"
        self.STOP_SCPI = "SOURce:Stop"
        self.SPEED_SETTING_SCPI = "SOURce:SPEed {0}"
        self.PID_KP_W_SCPI = "SOURce:Pid:KP "
        self.PID_KI_W_SCPI = "SOURce:Pid:KI "
        self.PID_KD_W_SCPI = "SOURce:Pid:KD "
        
        # command list
        self.Command_list_SCPI = "SYSTem:Help:HEADers?"

        # supported function param list
        self.function_param = {
            "operate" : {
                "operation_type" : ["Start", "Stop"],
                "target_rpm" : [100,10000]
                }
            }

    def heartbeat(self,):
        self._checkStatus()
        debug_device_name="{} ({})".format(self.device_name, "heartbeat")
        debug_msg="Hello World!! Succeed to connection to main computer!"
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)
        
        return_res_msg="[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg

    
    def _queryCommand(self, SCPI_command):
        """
        send a query command to the device.

        :param SCPI_command (str): The SCPI query command to be sent.

        :return: response received from the device --> (int)
        """
        return self.recallDevice.query(SCPI_command)  
        
    def _writeCommand(self, SCPI_command):
        """
        send a write command to the device.

        :param SCPI_command (str): The SCPI write command to be sent.

        :return: response received from the device --> (int)
        """
        return self.recallDevice.write(SCPI_command)


        
    ################################################################################
    #                              Report commands                                 #
    ################################################################################

    def _queryID(self):
        """
        query the device ID.

        :return: device ID responss --> (str)
        """
        device_ID = self._queryCommand(self.ID_SCPI)
        time.sleep(2)

        return device_ID
    
    def _read(self):
        """
        read the current speed from the device.

        :return: current speed value --> (str)
        """
        speed = self._queryCommand(self.READ_SCPI)
        time.sleep(2)

        return speed
    
    def _querySetSpeed(self):
        """
        query the current speed setting from the device.

        :return: current speed setting --> (int)
        """
        current_speed = self._queryCommand(self.QUERY_SETSPEED_SCPI)
        time.sleep(2)

        return current_speed
    
    def _reset(self):
        """
        reset the device.

        :return: command received value --> (int)
        """
        reset_int = self._writeCommand(self.RESET_SCPI)
        time.sleep(2)

        return reset_int
    
    def _start(self, ):
        """
        start the device rotation.

        :return: command received value --> (int)
        """        
        start_int = self._writeCommand(self.START_SCPI)
        time.sleep(2)    

        return start_int


    def _stop(self, ):
        """
        stop the device rotation.

        :param SCPI_command (str): The SCPI write command to be sent.

        :return: command received value --> (int)
        """
        stop_int = self._writeCommand(self.STOP_SCPI)
        time.sleep(2)

        return stop_int
    
    def _setSpeed(self, speed, ):
        """
        set rotaion speed
        
        :param speed (int): set the rotation speed. [rpm : 100 to 10000]

        :return: command received value --> (int)
        """
        set_speed_int = self._writeCommand(self.SPEED_SETTING_SCPI.format(speed))
        time.sleep(2)
        
        return set_speed_int


    def _readCurrentSpeed(self):
        """
        read current speed

        return : current speed --> (int)
        """
        for i in range(3):
            time.sleep(1)
            current_speed = self._read()

            if i < 2 :                
                if "SCPI" in current_speed :
                    pass
                else:
                    break

            else:
                error_code = 1
                error_msg = "Check connection"
                self.raiseError(error_code, error_msg)
        
        return int(current_speed)

    ###############################################################################

    def _checkStatus(self, ) :
        """
        check device status

        return : device status --> (str)
        """        
        current_speed = self._readCurrentSpeed()

        if current_speed == 0:
            return 'Waiting'
        else:
            return 'Operating'
            

    def startDevice(self, target_rpm:int=1600, mode_type='virtual'):
        """
        start RC-10k
        
        :param target_rpm(int) : [rpm : 100 to 10000]
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: res_msg --> (str)
        """
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        if mode_type == "real" :
            self.checkInputError("Target rpm", target_rpm, self.function_param["operate"]["target_rpm"])        
            msg = "RDE Rotation Start ... Speed : {} rpm".format(target_rpm)
            self.logger_obj.debug(debug_device_name, msg)

            status = self._checkStatus()
            error_dict = self.checkStatusError('Waiting',status)
            msg ="RDE Waiting? Receive signal! --> Waiting : {}, Status : {}".format(bool(status=='Waiting'), error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            self._setSpeed(target_rpm)
            msg = "Speed setting done --> Set Speed : {} rpm".format(target_rpm)
            self.logger_obj.debug(debug_device_name, msg)

            self._start()
            status = self._checkStatus()
            error_dict = self.checkStatusError('Operating',status)
            msg = "Operation Start! --> Operating : {}, Status : {}".format(bool(status=='Operating'),error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            current_speed = self._readCurrentSpeed()
            msg = "Rotation Start, Current Speed : {} rpm".format(current_speed)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg

        elif mode_type == "virtual" :
            self.checkInputError("Target rpm", target_rpm, self.function_param["operate"]["target_rpm"])        
            msg = "RDE Rotation Start, Set Speed : {} rpm".format(target_rpm)
            self.logger_obj.debug(debug_device_name, msg)

            msg = "Rotation Start, Speed : {} rpm".format(target_rpm)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
        

    def stopDevice(self, mode_type='virtual'):
        """
        stop RC-10k
        
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: res_msg --> (str)
        """
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        if mode_type == "real" :
            msg = "RDE Rotation Stop"
            self.logger_obj.debug(debug_device_name, msg)

            status = self._checkStatus()
            error_dict = self.checkStatusError('Operating',status)
            msg ="RDE Operating? Receive signal! --> Operating : {}, Status : {}".format(bool(status=='Operating'), error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            self._stop()
            status = self._checkStatus()
            error_dict = self.checkStatusError('Waiting',status)
            msg = "Operation Stop! --> Waiting : {}, Status : {}".format(bool(status=='Waiting'),error_dict)
            self.logger_obj.debug(debug_device_name, msg)    
        
            msg = "Rotation Stop"
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg
            
            return res_msg
        
        elif mode_type == "virtual" :
            msg = "RDE Rotation Stop"
            self.logger_obj.debug(debug_device_name, msg)

            msg = "Rotation Stop"
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg
            
            return res_msg
        


if __name__ == "__main__":
    NodeLogger_obj = NodeLogger(platform_name="Electrochemical Analysis", setLevel="DEBUG",
                            SAVE_DIR_PATH="../Evaluation/Desktop/EVALUATIONPLATFORM")
    
    Device = RC_10K(logger_obj=NodeLogger_obj, resource="ASRL8::INSTR")

    Device._checkStatus()

    # Device.startDevice(target_rpm=350, mode_type='real')
    
    # Device.stopDevice(mode_type='real')
