#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [Sonic_Bath] Class for controlling Sonic bath (Sonorex Digitec)
# @author   Daeho Kim (r4576@kist.re.kr)

"""
This module provides a Python interface to the Sonorex Digitec that operates
using the IrDA communication protocol developed by CSRC of the Korea Institute of Science and Technology. 
The command implementation is based on the instruction manual 
'DT remote-control 1339d GB BANDELIN'
"""

import os, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import serial
import time
from Log.Logging_Class import NodeLogger
from Device_Exception import DeviceError


class SonorexDigitec(DeviceError):
    """ 
    [Sonorex Digitec] Sonorex Digitec Class for controlling in another computer (windows)


    # Variable
    :param logger_obj (obj): set logging object (from Logging_class import Loggger) 
    :param device_name="Sonorex Digitec" (str): set sonic bath model name (log name)
    :param ser_port="COM12" (str): set sonic bath USB port 
    
    """

    STATUS_DICT = {
        0 : "<reserved> Remote contorl",
        1 : "<reserved> Service Mode",
        2 : "Ultrasound or Degas started",
        3 : "Degas on",
        4 : "<reserved> Heating regulation",
        5 : "Interruption of ultrasound output (pause)",
        6 : "standby",
        7 : "<not assigned>",
        8 : "Ultrasound power output (current output)",
        9 : "Heating power output",
        10 : "Calibation fuction: 20ms",
        11 : "<not assigned>",
        12 : "<not assigned>",
        13 : "<not assigned>",
        14 : "<not assigned>",
        15 : "Service function 'full access'",
        }



    def __init__(self, logger_obj, device_name = "Sonorex Digitec", ser_port = "COM5") :
       
        # logger object
        self.logger_obj=logger_obj
        # serial settings
        self.info = {
            "PORT" : ser_port,
            "BAUD_RATE" : 9600
        }
        self.device_name=device_name
        self.Sonic = serial.Serial(self.info["PORT"],self.info["BAUD_RATE"],bytesize=7,stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_EVEN, timeout=1)
        
        # operating commands
        self.POWER_ON = "P1"
        self.POWER_OFF = "P0"
        self.STANDBY = "Pz"
        self.TEMP_TARGET = "Hn"
        self.GET_TEMP_ACTUAL = "Hm"
        self.HEAT_OFF = "H0"
        self.GET_ID = "I"
        self.QUERY_ERROR = "Je"
        self.QUERY_STATUS = "Js"
        self.TIME_TARGET = "Tn"
        self.ELAPSED_TIME = "Tm"
        self.REMAIN_TIME = "Ts"
        self.DEGAS_ON = "Tp1"
        self.DEGAS_OFF = "Tp0"
        self.TIMEOUT = "Tt"
        self.CURRENT_LENGTH = "Tl"
        self.TOTAL_LENGTH = "Th"
        self.VERSION = "V"
        self.RESET = "X"
        self.TURN_OFF = "Zz"

        # supported function param list
        self.function_param = {
            "operate" : {
                "target_time" : [0, 64800],
                "target_temp" : [0,80],
                "operation_mode" : ["Degas_Off", "Degas_On"]
                }
            }
    
    def heartbeat(self,):
        self._checkConnection()
        debug_device_name="{} ({})".format(self.device_name, "heartbeat")
        debug_msg="Hello World!! Succeed to connection to main computer!"
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)
        
        return_res_msg="[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg
    
    def _checkConnection(self,):  
        """
        reconnect serial port

        :return: first character of receive value

        Not connected : "#"
        connceted : "J"
        """
        self.Sonic.close()
        self.Sonic.open()
        status_rcv = self._command(self.QUERY_STATUS) 
        return status_rcv[0]

    def _command(self, cmd) :
        """
        send message to device
        
        :param cmd(str) : operating command
        
        :return: serial_res_rcv --> (str)
        """
        input = "#" + cmd + "\r\n"
        byte_data = bytes(input, encoding="utf-8")
        self.Sonic.write(byte_data)
        data = self.Sonic.readline()
        serial_res_rcv = "{}".format(data.decode('utf-8').strip())
        serial_res_rcv = serial_res_rcv.replace(" ", "")

        if serial_res_rcv == "" :
            error_code = 1
            error_msg = self.ERROR_DICT[error_code]
            self.raiseError(error_code, error_msg)

        else :
            return serial_res_rcv


    def _inspectRcv(self, rcv, cmd):
        """
        check connection of serial port

        :param rcv(str) : return value of self._command
        :param cmd(str) : input command

        :return: rcv --> (str)
        """
        if rcv == "" :
            error_code = 1
            error_msg = "Check IrDA Transceiver"
            self.raiseError(error_code, error_msg)

        elif rcv[0] == "#" : # 맨 처음 자리에 #이 있으면 port가 안열린 것임 
            rcv_head = self._checkConnection()

            if rcv_head == "#" :
                error_code = 1        
                error_msg = self.ERROR_DICT[1]
                self.raiseError(error_code, error_msg)

            else : # port가 열린것 확인 후 다시 command 실행 하는 부분 
                regenerated_rcv = self._command(cmd)
                
                return self._inspectRcv(regenerated_rcv,cmd)
        
        else :
            
            return rcv
    
    def _processRcv(self, rcv, cmd):
        """
        process response (raw message -> dictionary)
        key : command, data
                
        :param rcv(str) : return value of self._inspectRcv
        :param cmd(str) : input command

        :return: data_dict --> (Dict)
        """
        if rcv == cmd : # value가 없는 경우 
            data = None
        elif cmd ==  self.RESET : # value가 있는 경우 
            data = rcv
        elif cmd ==  self.GET_ID or cmd == self.VERSION : # value가 있는 경우 
            data = rcv[len(cmd):]
        else : # value가 있는 경우
            data = int(rcv[len(cmd):],16)
        data_dict = {
            "Command" : cmd,
            "Data" : data
            }
        return data_dict


    def _sendRcv(self, cmd, value = ""):
        """
        send command, value and receive respond
        use this function to operate command

        :param cmd(str) : input command
        :param value(str) : target value

        :return: data_dict --> (Dict)
        """
        ser_res_rcv = self._command(cmd+value)
        inspected_rcv = self._inspectRcv(ser_res_rcv, cmd)
        progressed_rcv = self._processRcv(inspected_rcv, cmd)
        return progressed_rcv

    ################################################################################
    #                              Report commands                                 #
    ################################################################################
    
    def _getTotalStatus(self, ):
        """
        get status in dictionary format
        """
        status_value =  self._sendRcv(self.QUERY_STATUS)
        binary_value=format(status_value["Data"], '016b')
        status_dict = {}
        for idx, value in enumerate(binary_value[::-1]):
            if value == '0':
                binary_status = 'off'
            else: 
                binary_status = 'on'
            status_dict[idx] = binary_status
        return status_dict
    
    def _reset(self, ):
        """
        reset device
        """
        data = self._sendRcv(self.RESET)
        self._checkConnection()
        return data

    def _getId(self, ):
        """
        get device id
        """
        data = self._sendRcv(self.GET_ID)
        return data

    def _getVersion(self, ):
        """
        get device version
        """
        data = self._sendRcv(self.VERSION)
        return data

    def _powerOn(self,):
        """
        change device status to power on (status must be power off) 
        """
        data = self._sendRcv(self.POWER_ON)
        return data
    
    def _powerOff(self,):
        """
        change device status to power off 
        """
        data = self._sendRcv(self.POWER_OFF)
        return data

    def _standby(self,):
        """
        change device status to power off (to escape this status use power off command)
        """
        data = self._sendRcv(self.STANDBY)
        return data

    def _setTemp(self, temp ):
        """
        Heat sonic bath

        Param temp(numeric types) : target temp value
        """
        data = self._sendRcv(self.TEMP_TARGET, format(int(temp*256), 'x'))
        return data
    
    def _getSetTemp(self, ):
        """
        get set heating tempetature
        """
        data = self._sendRcv(self.TEMP_TARGET)
        return data
    
    def _getActualTemp(self, ):
        """
        get actual tempetature
        """
        data = self._sendRcv(self.GET_TEMP_ACTUAL)
        return data
    
    def _heatOff(self, ):
        """
        heating off
        """
        data = self._sendRcv(self.HEAT_OFF)
        return data
    
    def _queryError(self, ):
        """
        recall error
        """
        data = self._sendRcv(self.QUERY_ERROR)
        return data

    def _setTime(self, settime):
        """
        set oprating time
        """
        data = self._sendRcv(self.TIME_TARGET, format(int(settime), 'x'))
        return data

    def _getSetTime(self,):
        """
        get set time
        """
        data = self._sendRcv(self.TIME_TARGET)
        return data

    def _getElapsedTime(self, ):
        """
        get elapsed time
        """
        data = self._sendRcv(self.ELAPSED_TIME)
        return data

    def _getRemainTime(self, ):
        """
        get remain time
        """
        data = self._sendRcv(self.REMAIN_TIME)
        return data

    def _degasOn(self, ):
        """
        set degas on mode (use with power on command) 
        """
        data = self._sendRcv(self.DEGAS_ON)
        return data

    def _degasOff(self, ):
        """
        set degas off mode
        """
        data = self._sendRcv(self.DEGAS_OFF)
        return data

    def _setTimeout(self, timeout):
        """
        set time out
        """
        data = self._sendRcv(self.TIMEOUT, format(int(timeout), 'x'))
        return data
    
    def _getSetTimeout(self, ):
        """
        get set time out value
        """
        data = self._sendRcv(self.TIMEOUT, )
        return data

    def _getCurrentLength(self, ):
        """
        get current length
        """
        data = self._sendRcv(self.CURRENT_LENGTH)
        return data

    def _getTotalLength(self, ):
        """
        get total length
        """
        data = self._sendRcv(self.TOTAL_LENGTH)
        return data

    def _turnOff(self, ):
        """
        turn off device
        """
        data = self._sendRcv(self.TURN_OFF)
        return data
    
    ###############################################################################
    
    
    def _checkStatus(self, ):
        """
        check device status : stadby, ready(off), on

        :return: status --> (str)
        """
        time.sleep(1)
        status_dict = self._getTotalStatus()
        if status_dict[6] == 'on':
            status = 'Standby'
        elif status_dict[2] == 'on' :
            status = 'Operating'
        else :
            status = 'Ready'
        # msg = "Current Sonic Status : {}".format(status)
        # print(msg)
        return status

    
    def _ready(self, iter:int = 0 ):
        """
        change device status to ready
        
        :param iter(int) : No need to provide input

        :return: status, error massage --> (str)
        """
        status = self._checkStatus()
        error_code = 0
        
        if status == "Standby" :
            self._powerOff()
            iter += 1
            if iter == 2 :
                error_code = 2
                error_msg = "The device is unable to exit standby mode."
                self.raiseError(error_code, error_msg)
            return self._ready(iter = iter)

        elif status == "Operating" :
            error_code = 2
            error_msg = "Sonic is already working!"
            self.raiseError(error_code, error_msg)

        else :           
            pass
        time.sleep(3)
        return status, self.ERROR_DICT[error_code]
    
            
    def operate(self, target_time:int, target_temp:int = 0, operation_mode:str = "Degas_Off", mode_type = "virtual"):
        """
        operate sonic bath
        
        :param target_time(int) : [s : 0 to 64800]
        :param target_temp(int) : [°C : 0 to 80]
        :param operation_mode(str) : "Degas_Off" or "Degas_On"
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: res_msg --> (str)
        """
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        self.checkInputError("Target Time", target_time, self.function_param["operate"]["target_time"])        
        self.checkInputError("Target Temp", target_temp, self.function_param["operate"]["target_temp"])        
        self.checkInputError("Operation Mode", operation_mode, self.function_param["operate"]["operation_mode"])        

        msg = "Sonication ... Operation Mode: {}, Set Time: {} s, Heating Temp: {} °C".format(operation_mode ,target_time, target_temp)
        self.logger_obj.debug(debug_device_name, msg)


        if mode_type == "real":
            status, error_dict = self._ready()
            msg ="Sonic Ready? Receive signal! --> Ready : {}, Status : {}".format(bool(status=='Ready'), error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            set_time = self._setTime(target_time)
            msg = "Time setting done --> Time : {} s".format(set_time['Data'])
            self.logger_obj.debug(debug_device_name, msg)

            set_temp = self._setTemp(target_temp)
            msg = "Heating temp setting done --> Temp : {} °C ".format(set_temp['Data'])
            self.logger_obj.debug(debug_device_name, msg)

            if operation_mode == "Degas_On":
                self._degasOn()
                msg = "Degas On --> {} ".format
            self._powerOn()
            status = self._checkStatus()
            error_dict = self.checkStatusError('Operating',status)
            msg = "Sonic Start! --> Operating : {}, Status : {}".format(bool(status=='Operating'),error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            while True:
                status = self._checkStatus()
                if status == "Operating":
                    time.sleep(5)
                    
                else:
                    msg = "Sonication done"
                    break
            
            self._standby()
            status = self._checkStatus()
            error_dict = self.checkStatusError('Standby',status)
            msg = "Sonic Standby? --> Standby : {}, Status : {}".format(bool(status=='Standby'),error_dict)
            self.logger_obj.debug(debug_device_name, msg)
            
            msg= "Sonication done, Operation Mode: {}, Set Time: {} s, Heating Temp: {} °C".format(operation_mode ,target_time, target_temp)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
        
        elif mode_type == "virtual":
            msg = "Sonication done, Operation Mode: {}, Set Time: {} s, Heating Temp: {} °C".format(operation_mode ,target_time, target_temp)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
    


if __name__ == '__main__':
    NodeLogger_obj = NodeLogger(platform_name="Electrochemical Analysis", setLevel="DEBUG",
                            SAVE_DIR_PATH="C:/Users/Evaluation/Desktop/EVALUATIONPLATFORM")
    sonic = SonorexDigitec(logger_obj=NodeLogger_obj, ser_port = "COM5")

    # time.sleep(5)

    sonic.heartbeat()

    ready = sonic.operate(target_time= 10, target_temp = 0, operation_mode='Degas_Off',mode_type="real")

    # ready = sonic.operate(target_time= 10, target_temp = 0, operation_mode='Degas_On',mode_type="real")