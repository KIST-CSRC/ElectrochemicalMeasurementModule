#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [Powerbox] Class for controlling PowerBox 3PF
# @author   Daeho Kim (r4576@kist.re.kr)


"""
This module provides a Python interface to the PowerBox 3PF that operates
using the Modbus/TCP protocol developed by CSRC of the Korea Institute of Science and Technology. 
The command implementation is based on the instruction manual 
'NETIO Modbus/TCP specification v13'
"""

import os, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from pyModbusTCP.client import ModbusClient
from Log.Logging_Class import NodeLogger
from Device_Exception import DeviceError

import time

#IP adress 192.168.1.201

class Powerbox3PF(DeviceError):
    """
    [Powerbox3PF] Multitab Class for controlling in another computer (windows)

    # Variable
    :param logger_obj (obj): set logging object (from Logging_class import Loggger) 
    :param device_name (str): set device name connected to multitab (log name)
    :param socket (int): set MFC address [socket : 1 to 3]

    """

    def __init__(self, logger_obj, device_name, ip = "192.168.1.201", socket = 1):
        
        #logger object
        self.logger_obj=logger_obj

        self.info = {
            "IP" : "192.168.1.201",
            "PORT" : 502,
            "SOCKET" : socket
            }
        self.device_name = device_name
        self.register = self.info["SOCKET"] + 100
        self.client = ModbusClient(host= self.info["IP"], port= self.info["PORT"], auto_open=True, timeout=1)

        # supported function param list
        self.function_param = {
            "operate" : {
                "operation_type" : ["On", "Off"],
                }
            }

    def heartbeat(self,):
        self._checkConnection()
        debug_device_name="{} ({})".format(self.device_name, "heartbeat")
        debug_msg="Hello World!! Succeed to connection to main computer!"
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)
        
        return_res_msg="[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg
    
    # Open connection to the Modbus/TCP server
    def _checkConnection(self):
        """
        check connection and open client

        :return: error code --> (int)
        """
        error_code = 0
        
        if not self.client.is_open():
            if not self.client.open():
                error_code = 2
                error_msg = "Failed to connect to Modbus/TCP server"
                self.raiseError(error_code,error_msg)

        return error_code

    ################################################################################
    #                              Report commands                                 #
    ################################################################################

    def _On(self, ):
        """
        Switch on the multi tab socket.

        :return: command received value --> (bool)
        """
        response = self.client.write_single_coil(self.register, 1)

        return response
    
    def _Off(self, ):
        """
        Switch off the multi tab socket.

        :return: command received value --> (bool)
        """
        response = self.client.write_single_coil(self.register, 0)

        return response
    
    ##############################################################################

    def _checkStatus(self, ):
        """
        Check connection of the multi tab socket.

        :return: command received value --> (str)
        """
        response = self.client.read_coils(self.register, 1)
        if response[0] == True :
            return "On"
        elif response[0] == False :
            return "Off"
        else :
            error_code = 2
            error_msg = "Operation error occured"
            self.raiseError(error_code,error_msg)
              
    
    def switch_on(self, mode_type='virtual'):
        """
        switch on the device connected Powerbox3PF  
        
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: res_msg --> (str)
        """
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        if mode_type == "real" :
            error_code = self._checkConnection()
            msg = "Multitab Connection --> Status : {}".format(self.ERROR_DICT[error_code])
            self.logger_obj.debug(debug_device_name, msg)

            msg = "{} Switch on".format(self.device_name)
            self.logger_obj.debug(debug_device_name, msg)

            status = self._checkStatus()
            error_dict = self.checkStatusError('Off',status)
            msg ="{} Waiting? Receive signal! --> Waiting : {}, Status : {}".format(self.device_name, bool(status=='Off'), error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            self._On()  
            status = self._checkStatus()
            error_dict = self.checkStatusError('On',status)
            msg = "Device {}! --> Status : {}".format(status,error_dict)
            self.logger_obj.debug(debug_device_name, msg)
            
            msg= "On"
            self.logger_obj.debug(debug_device_name, msg)
            res_msg = debug_device_name + " : " + msg
            
            return res_msg
            
            
        elif mode_type == "virtual" :
            msg = "{} Switch on".format(self.device_name)
            self.logger_obj.debug(debug_device_name, msg)

            msg= "On"
            self.logger_obj.debug(debug_device_name, msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
        
    def switch_off(self, mode_type='virtual'):
        """
        switch off the device connected to Powerbox3PF 
        
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: res_msg --> (str)
        """
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        if mode_type == "real" :
            error_code = self._checkConnection()
            msg = "Multitab Connection --> Status : {}".format(self.ERROR_DICT[error_code])
            self.logger_obj.debug(debug_device_name, msg)

            msg = "{} Switch off".format(self.device_name)
            self.logger_obj.debug(debug_device_name, msg)

            status = self._checkStatus()
            error_dict = self.checkStatusError('On',status)
            msg = "{} Operating? Receive signal! --> Operating : {}, Status : {}".format(self.device_name, bool(status=='On'), error_dict)                
            self.logger_obj.debug(debug_device_name, msg)

            self._Off()  
            status = self._checkStatus()
            error_dict = self.checkStatusError('Off',status)
            msg = "Device {}! --> Status : {}".format(status,error_dict)
            self.logger_obj.debug(debug_device_name, msg)
            
            msg= "Off"
            self.logger_obj.debug(debug_device_name, msg)
            res_msg = debug_device_name + " : " + msg
            
            return res_msg
            
            
        elif mode_type == "virtual" :
            msg = "{} Switch off".format(self.device_name)
            self.logger_obj.debug(debug_device_name, msg)

            msg= "Off"
            self.logger_obj.debug(debug_device_name, msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
    
    
    def operate(self, duration, mode_type = "virtual"):

        debug_device_name="{} ({})".format(self.device_name, mode_type)
        msg = "Operation Start!"

        if mode_type == "real" :            
            self.switch_on(mode_type=mode_type)
            time.sleep(duration)
            self.switch_off(mode_type=mode_type)

        elif mode_type == "virtual" :
            pass

        msg= "Operation done, Set time {}s".format(duration)
        self.logger_obj.debug(debug_device_name, msg)
        res_msg = debug_device_name + " : " + msg
        
        return res_msg

if __name__ == "__main__":
    NodeLogger_obj = NodeLogger(platform_name="Electrochemical Analysis", setLevel="DEBUG",
                            SAVE_DIR_PATH="C:/Users/Evaluation/Desktop/EVALUATIONPLATFORM")
    IrLamp = Powerbox3PF(logger_obj=NodeLogger_obj,device_name= "Ir lamp",ip="192.168.1.201", socket=3)
    
    Humidifier = Powerbox3PF(logger_obj=NodeLogger_obj,device_name= "Humidifier",ip="192.168.1.201", socket=2)

    Solenoid = Powerbox3PF(logger_obj=NodeLogger_obj, device_name= "Sol Valve",ip="192.168.1.201",socket=1)

    # IrLamp.switch_on('real')

    # IrLamp.switch_off('real')

    # time.sleep(3)
    

    # time.sleep(0)

    # Solenoid.switch_off(mode_type='real')

    # time.sleep(3)

    Solenoid.operate(50,mode_type='real')

    # time.sleep(3)

    # Humidifier.switchOff(mode_type='real')
