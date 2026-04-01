#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [MFC] Class for controlling WIZ-701
# @author   Daeho Kim (r4576@kist.re.kr)

"""
This module provides a Python interface to the WIZ-701 mass flow controller that operates
using the RS-485 serial protocol developed by CSRC of the Korea Institute of Science and Technology. 
The command implementation is based on the instruction manual 
'Wizro Series RS-485 or Modbus Protocol (Kor) [Ver1.5]'
"""

import os, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import serial 
from Log.Logging_Class import NodeLogger
from Device_Exception import DeviceError
import time


class WIZ_701(DeviceError):
    """
    [WIZ-701] MFC Class for controlling in another computer (windows)

    # Variable
    :param logger_obj (obj): set logging object (from Logging_class import Loggger) 
    :param device_name="WIZ-701" (str): set MFC model name (log name)
    :param address (int): set MFC address [address : 1 to n]
    
    """

    def __init__(self, logger_obj, device_name="WIZ-701", ser_port = "COM12", address = 1):

        #logger object
        self.logger_obj=logger_obj

        self.info = {
            "PORT" : ser_port,
            "BAUD_RATE" : 115200
            }
        self.device_name = device_name
        self.address = address
        self.MFC = serial.Serial(self.info["PORT"],self.info["BAUD_RATE"],timeout=0.1)
    
        # operating commands
        self.SET_VALUE = "e0"
        self.WRITE_GAIN_LEAD_VALUE = "e5"
        self.SET_ACC_VALUE = "e6"
        self.ONOFF_CALZERO = "ce"
        self.ONOFF_ACC = "d1"
        self.STOP = "f0"
        self.RUN = "f1"
        self.RESET_ACC = "f2"
        self.READ_PV = "f7"
        self.READ_PV_SV = "f8"
        self.READ_PV_ACC = "f9"
        self.INFO = "ff"
        self.COM_EXIT = "fb" 

        # supported function param list
        self.function_param = {
            "operate" : {
                "operation_type" : ["Start", "Stop"],
                "target_flow" : [10,500],
                }
            }
    def heartbeat(self,):
        self._checkStatus()
        debug_device_name="{} ({})".format(self.device_name, "heartbeat")
        debug_msg="Hello World!! Succeed to connection to main computer!"
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)
        
        return_res_msg="[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg
    
    def _command(self, cmd):
        """
        send message to device
        
        :param cmd(str) : operating command
        
        :return: serial_res_rcv --> (str)
        """
        cmd = "0{}00".format(self.address)+ cmd
        byte_data = bytes.fromhex(cmd)
        self.MFC.write(byte_data)
    
        time.sleep(2)
        
        received_data = bytearray()  # Initialize an empty byte array to store received data

        while True:
            data_chunk = self.MFC.read()  # Read a chunk of data from the serial port
            if not data_chunk:  # If no more data is available, exit the loop
                break
            received_data += data_chunk  # Append the data chunk to received_data
            

        res_rcv = received_data.hex()  # Convert the entire received_data to a hexadecimal string

        time.sleep(2)

        return res_rcv
    

    def _write(self, cmd, value):
        """
        write command value to device
        
        :param cmd(str) : operating command
        :param value(str) : hex value
        
        :return: data dictionary --> (dict)
        """
        rcv = self._command(cmd + value)
        data_dict = {
            "Command" : cmd,
            "Input_Value" : value,
            "Checksum" : rcv
        }

        time.sleep(2)
        
        return data_dict

    def _control(self,cmd) :
        """
        control device according to the command
        
        :param cmd(str) : operating command
        
        :return: data dictionary --> (dict)
        """
        self._command(cmd)
        data_dict = {
            "Command" : cmd,        
        }

        time.sleep(1)

        return data_dict


    def _read(self, cmd) :
        """
        read device status according to the command
        
        :param cmd(str) : operating command
        
        :return: data dictionary --> (dict)
        """
        rcv = self._command(cmd)
        data_dict = {
            "Command" : cmd,                       
            "Status" : rcv[4:6],
            "Raw_Value" : rcv[6:-2] ,
            "Checksum" : rcv[-2:], 
        }
        time.sleep(1)

        return data_dict   

    def _checkSum(self, value, checksum):
        """
        check device response

        :param cmd(str) : response value
        :param cmd(str) : response checksum
        
        :return: data dictionary --> (dict)
        """
        valuesum = 0
        for i in range(0, len(value), 2):
            valuesum += int(value[i:i+2],16)
        if str(hex(valuesum))[-2:] == checksum :
            error_code = 0
        else :
            error_code = 2
            error_msg = "Invaild response"
            self._raiseError(error_code,error_msg)

        return error_code
    
    ################################################################################
    #                              Report commands                                 #
    ################################################################################

    def _start(self,):
        """
        start the device operation.

        :return: command received value --> (dict)
        """        
        data_dict = self._control(self.RUN)
        time.sleep(20)

        return data_dict
    

    def _stop(self,):
        """
        stop the device operation.

        :return: command received value --> (dict)
        """ 
        data_dict = self._control(self.STOP)
        return data_dict
    
    def _setFlow(self, value):
        """
        set device flow rate
        
        :param value (int): set the flow rate. [sccm : 10 to 500]

        :return: command received value --> (dict)
        """
        setpoint_value = format(value, f'04X')
                
        data_dict = self._write(self.SET_VALUE,setpoint_value) 
        
        
        return data_dict
    

    def _queryPV(self,):
        """
        read process value

        :return: command received value --> (dict)
        """               
        data_dict = self._read(self.READ_PV)

        data_dict["Process_Value"] = int(data_dict["Raw_Value"],16)

        return data_dict
    

    def _queryPVSV(self,):
        """
        read process value, set value

        :return: command received value --> (dict)
        """            
        data_dict = self._read(self.READ_PV_SV)

        data_dict["Process_Value"] = int(data_dict["Raw_Value"][:4],16)
        data_dict["Set_Value"] = int(data_dict["Raw_Value"][4:], 16)

        return data_dict
    

    def _queryInfo(self,):
        """
        read process value, set value, gain, lead, Acc pv, Acc sv 

        :return: command received value --> (dict)
        """     
        data_dict = self._read(self.INFO)

        data_dict["Process_Value"] = int(data_dict["Raw_Value"][:4], 16)
        data_dict["Set_Value"] = int(data_dict["Raw_Value"][4:8],16)
        data_dict["Gain"] = int(data_dict["Raw_Value"][8:12],16)
        data_dict["Lead"] = int(data_dict["Raw_Value"][12:16],16) 
        data_dict["Acc_Process_Value"] = int(data_dict["Raw_Value"][16:24],16)
        data_dict["Acc_Set_Value"] = int(data_dict["Raw_Value"][24:32],16)
        
        return data_dict
    

    def _checkStatus(self, ) :
        """
        check device status

        return : device status --> (str)
        """        
        current_speed = self._queryPVSV()["Process_Value"]
        if current_speed == 0:
            return 'Waiting'
        else:
            return 'Operating'
    
    def startDevice(self, target_flow:int=500, mode_type='virtual'):
        """
        start WIZ-701
        
        :param target_flow(int) : [sccm : 10 to 500]
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: res_msg --> (str)
        """
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        if mode_type == "real" :
            self.checkInputError("Target Flow", target_flow, self.function_param["operate"]["target_flow"])        
            msg = "MFC Start ... Flow Rate : {} sccm".format(target_flow)
            self.logger_obj.debug(debug_device_name, msg)

            status = self._checkStatus()
            error_dict = self.checkStatusError('Waiting',status)
            msg ="MFC Waiting? Receive signal! --> Waiting : {}, Status : {}".format(bool(status=='Waiting'), error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            self._setFlow(target_flow)
            msg = "Flow rate setting done --> Set Flow Rate : {} sccm".format(target_flow)
            self.logger_obj.debug(debug_device_name, msg)

            self._start()
            status = self._checkStatus()
            msg = "Operation Start! --> Operating : {}, Status : {}".format(bool(status=='Operating'),error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            current_speed = self._queryPVSV()["Process_Value"]
            msg= "Start, Current Flow Rate : {} sccm".format(current_speed)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
        
        elif mode_type == "virtual" :
            self.checkInputError("Target rpm", target_flow, self.function_param["operate"]["target_flow"])        
            msg = "MFC Start ...  Flow Rate : {} sccm".format(target_flow)
            self.logger_obj.debug(debug_device_name, msg)

            msg= "Start, Flow Rate : {} sccm".format(target_flow)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg

    def stopDevice(self, mode_type):
        """
        stop WIZ-701
        
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: res_msg --> (str)
        """
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        if mode_type == "real" :
            msg = "MFC Stop"
            self.logger_obj.debug(debug_device_name, msg)
            
            status = self._checkStatus()
            error_dict = self.checkStatusError('Operating',status)
            msg = "MFC Operating? Receive signal! --> Operating : {}, Status : {}".format(bool(status=='Operating'), error_dict)                
            self.logger_obj.debug(debug_device_name, msg)

            self._stop()
            status = self._checkStatus()
            error_dict = self.checkStatusError('Waiting',status)
            msg = "Operation Stop! --> Waiting : {}, Status : {}".format(bool(status=='Waiting'),error_dict)
            self.logger_obj.debug(debug_device_name, msg)    
            
            msg = "Stop"
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg
            
            return res_msg


        elif mode_type == "virtual" :
            msg = "MFC Stop"
            self.logger_obj.debug(debug_device_name, msg)

            msg= "Stop"
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg

if __name__ == '__main__':
    NodeLogger_obj = NodeLogger(platform_name="Electrochemical Analysis", setLevel="DEBUG",
                            SAVE_DIR_PATH="C:/Users/Evaluation/Desktop/EVALUATIONPLATFORM")
    
    mfc = WIZ_701(logger_obj=NodeLogger_obj,address=1)
    
    # mfc.heartbeat()
    
    # time.sleep(5)

    
    # mfc.startDevice(300,mode_type="real")

    mfc.stopDevice('real')