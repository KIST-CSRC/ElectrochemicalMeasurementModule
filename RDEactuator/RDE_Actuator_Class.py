#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [Actuator] Class for controlling RDE Actuator (3Axis Motion Controller)
# @author   Daeho Kim (r4576@kist.re.kr)


import os, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import serial
import time
from Log.Logging_Class import NodeLogger
from Device_Exception import DeviceError

class RDEMotionController(DeviceError):
    #X < 990000, Z < 390000
    def __init__(self, logger_obj, device_name="RDEActuator", r_ser_port = "COM4", xz_ser_port = "COM3" ):
        #logger object
        self.logger_obj=logger_obj

        #device setting
        self.info = { 
        "R_PORT" : r_ser_port,
        "XZ_PORT" : xz_ser_port,
        "BAUD_RATE" : 9600
        }
        self.device_name = device_name
        self.XZ_Actuator = serial.Serial(self.info["XZ_PORT"],self.info["BAUD_RATE"],bytesize=8,stopbits=1, parity="N", timeout=1)
        self.R_Actuator = serial.Serial(self.info["R_PORT"],self.info["BAUD_RATE"],bytesize=8,stopbits=1, parity="N", timeout=1)
        
        # operating commands
        self.PROGRAM = "PRG"
        self.JOG = "JOG"
        self.POSITION_ABS = "PAB"
        self.POSITION_INC = "PIC"
        self.CLEAR_LOGIC = "CLL"
        self.CLEAR_REAL = "CLR"
        self.READ_WRITE_SPD = "SPD"
        self.READ_POS = "POS"
        self.HOME = "HOM"
        self.STOP = "STO"
        self.VERSION = "VER"
        self.CURRENT_ID = "IDC"
        self.SET_SM = "SSM"
        self.READ_INPUT = "INR"
        self.READ_OUTPUT = "OUT"
        self.RESET = "RST"
        self.SET_SCI = "SCI"
        self.STOP_HOME = "OGE"
        self.PAUSE = "PSP"
        self.STOP_STEP = "EDP"
        self.RESTART = "PRS"
        self.START_PROGRAM = "PST"
        self.READ_ERROR = "ERD"

    position_teaching = {
         "Casting": {        
            "X":980000,
            "Z":100000,
            "R":-900000
            },   
        "Microscope":{
            "X":268000,
            "Z":220000,
            "R":-900000
            },
        "IrLamp":{
            "X":170000,
            "Z":50000,
            "R":-900000    
            },
        "Humidifier":{
            "X":300000,
            "Z":380000,
            "R":0    
            },    
        "Cell":{
            "X":97000,
            "Z":300000,
            "R":0    
            },
        "Polishing":{        
            "X":600000,
            "Z":247700,
            "R":0
            },
        "Sonic":{
            "X":875000,
            "Z":350000,
            "R":0
            },
        "Home": {        
            "X":0,
            "Z":0,
            "R":0
            } 
        }
    
    def heartbeat(self,):
        self._readPOS("X")
        debug_device_name="{} ({})".format(self.device_name, "heartbeat")
        debug_msg="Hello World!! Succeed to connection to main computer!"
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)
        
        return_res_msg="[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg
    
    def _command(self, axis, cmd, value=str()):
        """
        send message to device
        
        :param axis(str) : operating axis
        :param cmd(str) : operating command
        :param cmd(int) : operating value

        :return: serial_res_rcv --> (str)
        """
        if value != str():
            cmd = cmd + " "
        else :
            pass

        if axis == "X" :
            cmd = "{}{}\r".format(cmd, value)
            self.XZ_Actuator.write(cmd.encode())
            response = self.XZ_Actuator.readline()  
             
        elif axis == "Z" :
            cmd = "{},{}\r".format(cmd, value)
            self.XZ_Actuator.write(cmd.encode())
            response = self.XZ_Actuator.readline()  

        elif axis == "R" :
            cmd = "{}{}\r".format(cmd, value)
            self.R_Actuator.write(cmd.encode())             
            response = self.R_Actuator.readline()  

        # time.sleep(1)

        response = self._processRcv(response)
        
        return response

    def _convertValue(self, value:str):
        """
        convert complement value
                
        :param value(str) : hexadecimal

        :return: data --> (int)
        """
        if value[0] == 'F':
            complement_value = format(~int(value,16) & 0xFFFFFFFF, 'X')
            value = -(int(complement_value,16)+1)
        else :
            value = int(value, 16)
            
        return value

    def _processRcv(self, rcv):
        """
        process response 
                
        :param rcv(str) : return value of self._inspectRcv

        :return: data --> (int)
        """
        rcv  = rcv.decode().strip()
        if not rcv : 
            data = None
        elif ',' in rcv : 
            data = rcv[4:].split(',')
            for i in range(len(data)) :
                data[i] = self._convertValue(data[i])
        else :
            data = self._convertValue(rcv[4:])
        
        return data

    
    def _positionABS(self, axis, value):
        cmd = self.POSITION_ABS
        response = self._command(axis, cmd, value)
        
        return response


    def _positionINC(self, axis, value):
        cmd = self.POSITION_INC
        response = self._command(axis, cmd, value)

        return response
    
    def _setSpeed(self, axis, value):
        cmd = self.READ_WRITE_SPD
        response = self._command(axis, cmd, value)

        return response
    
    def _stop(self, axis, value):
        cmd = self.STOP
        response = self._command(axis, cmd, value)

        return response


    def _readSpeed(self, axis):
        cmd = self.READ_WRITE_SPD
        if axis == "X" or axis == "R" :
            res = self._command(axis, cmd)[0]
        elif axis == "Z" :
            res = self._command("X", cmd)[1]

        return res
    
    def _readPOS(self, axis):
        cmd = self.READ_POS
        if axis == "X" or axis == "R" :
            res = self._command(axis, cmd)[0]
        elif axis == "Z" :
            res = self._command("X", cmd)[1]
        
        return res
    
    def _readInput(self, axis):
        cmd = self.READ_INPUT
        if axis == "X" or axis == "R" :
            res = self._command(axis, cmd, "X")[0]
        elif axis == "Z" :
            res = self._command("X", cmd, "Y")[0]

        return res
    
    def _readOutput(self, axis):
        cmd = self.READ_OUTPUT
        if axis == "X" or axis == "R" :
            res = self._command(axis, cmd, "X")[0]
        elif axis == "Z" :
            res = self._command("X", cmd, "Y")[0]
        
        return res
    
    def _checkStatus(self, ) :
        """
        check device status

        return : device status --> (str)
        """        
        x_speed = self._readSpeed("X")
        z_speed = self._readSpeed("Z")
        r_speed = self._readSpeed("R")
        if x_speed == 0 and z_speed == 0 and r_speed == 0:
            return 'Waiting'
        else:
            return 'Operating'
        
    def _move(self, axis, position, speed):

        self._setSpeed(axis,speed)
        self._positionABS(axis,position)

        while True :
            status = self._checkStatus()
            if status == "Operating":
                pass
            else:
                break
        
        current_position = self._readPOS(axis)
        error_code = 2
        error_msg = "Axis : {}, Setting Postion : {}, Real Position : {}".format(axis,position, current_position)
        self.checkCondition(current_position==position, error_code, error_msg)
        
        return error_msg
    
    def convertRDEdirection(self, direction):
        if direction == "UP":
            current_pos = self._readPOS("R")
            error_code = 2
            error_msg = "Axis : {}, Setting Postion : {}, Real Position : {}".format("R",0, current_pos)
            self.checkCondition(current_pos==self._readPOS("R"), error_code, error_msg)
            current_pos = self._move("R", -900000, 4000)

        elif direction == "DOWN" :
            current_pos = -900000
            error_code = 2
            msg = "Axis : {}, Setting Postion : {}, Real Position : {}".format("R",0, current_pos)
            self.checkCondition(current_pos==self._readPOS("R"), error_code, error_msg)
            current_pos = self._move("R", 0, 4000)
            
        return error_msg
    

    def moveHome(self, axis:list, mode_type='virtual'):
        
        debug_device_name="{} ({})".format(self.device_name, mode_type)
        
        if mode_type == "real":
        
            if isinstance(axis, str):
                axes_to_move = [axis]
            elif isinstance(axis, list):
                axes_to_move = axis
            else:
                raise ValueError("Invalid input. 'axis' should be a string or a list of strings (X, Z, R).")

            cmd = self.HOME

            for single_axis in axes_to_move:
                if single_axis == "X" or single_axis == "R":
                    res = self._command(single_axis, cmd, "X")
                elif single_axis == "Z":
                    res = self._command("X", cmd, "Y")

                while True:
                    status = self._checkStatus()
                    if status == "Operating":
                        pass
                    else:
                        break

                current_position = self._readPOS(single_axis)
                error_code = 2
                msg = "Axis : {}, Setting Position : {}, Real Position : {}".format(single_axis, 0, current_position)
                self.checkCondition(current_position == 0, error_code, msg)
                self.logger_obj.debug(debug_device_name, msg)

            msg= "Movement completed, Current position : Home".format()
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
        
        elif mode_type == "virtual":
            msg= "Movement completed, Current position : Home"
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg  
    


    def move2Position(self, position_name:str, speed:int=8000, mode_type:str='virtual'):
        """
        move actuator to pos
        
        :param position_name(str) : position name (ex. "Casting", "Microscope"...)
        :param speed(speed) : [100 to 8000]
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: res_msg --> (str)
        """
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        msg = "Move RDE ... Position : {} , Speed : {}".format(position_name, speed)
        self.logger_obj.debug(debug_device_name, msg)


        if mode_type == "real":
            status = self._checkStatus()
            error_dict = self.checkStatusError('Waiting',status)
            msg ="Actuator Waiting? Receive signal! --> Waiting : {}, Status : {}".format(bool(status=='Waiting'), error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            msg = self._move("Z",100000,speed)
            self.logger_obj.debug(debug_device_name, msg)

            goal_position = self.position_teaching[position_name]
            if self._readPOS("R") != goal_position["R"] :
                msg = self._move("X",650000,speed)
                self.logger_obj.debug(debug_device_name, msg)
                
                msg = self._move("R",goal_position["R"],speed)
                self.logger_obj.debug(debug_device_name, msg)
                
            else :
                pass

            msg = self._move("X", goal_position["X"], speed)
            self.logger_obj.debug(debug_device_name, msg)
            msg = self._move("Z", goal_position["Z"], speed)
            self.logger_obj.debug(debug_device_name, msg)
               
            msg= "Movement completed, Current position : {}".format(position_name)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
        
        elif mode_type == "virtual":
            msg= "Movement completed, Current position : {}".format(position_name)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
    
 


if __name__ == '__main__' :
    NodeLogger_obj = NodeLogger(platform_name="Electrochemical Analysis", setLevel="DEBUG",
                            SAVE_DIR_PATH="../EVALUATIONPLATFORM")
    
    Actuator = RDEMotionController(logger_obj=NodeLogger_obj)

    # Actuator.moveHome(["Z","X","R"],"real")

    # Actuator._move("Z",40000,5000)
    # time.sleep(5)

    # Actuator.move2Position(position_name="Cell",speed=8000,mode_type="real")

    # time.sleep(2)

    # Actuator.move2Position(position_name-***************************************="Humidifier",speed=8000,mode_type="real")

    # time.sleep(2)
    # for i in range(10) :
    Actuator.move2Position(position_name="Microscope",speed=8000,mode_type="real")
        # time.sleep(2)
        # Actuator.move2Position(position_name="IrLamp",speed=8000,mode_type="real")
        # time.sleep(2)
        # Actuator.move2Position(position_name="Humidifier",speed=8000,mode_type="real")
        