import os, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import serial 
from Log.Logging_Class import NodeLogger
from Device_Exception import DeviceError
import time

class PolishingTool(DeviceError):
    def __init__(self, logger_obj, device_name="Polishing", Rotor_ser_port = 'COM9' ,SolutionPump_ser_port = 'COM10',WaterPump_ser_port = "COM11", address = 1):

        #logger object
        self.logger_obj=logger_obj

        self.device_name = device_name
        self.WaterPump = serial.Serial(SolutionPump_ser_port, 115200, timeout=1)
        self.SolutionPump = serial.Serial(WaterPump_ser_port, 115200, timeout=1)
        self.Rotor = serial.Serial(Rotor_ser_port, 9600, timeout=1) 
    
    def heartbeat(self,):
        # self.WaterPump.write('0'.encode())
        self.SolutionPump.write('0'.encode())
        self.Rotor.write('0'.encode())
        debug_device_name="{} ({})".format(self.device_name, "heartbeat")
        debug_msg="Hello World!! Succeed to connection to main computer!"
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)
        
        return_res_msg="[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg

    def dispenseWater(self,operation_time):
        time.sleep(2)
        command = '1'
        self.WaterPump.write(command.encode())
        time.sleep(operation_time)
        command = '0'
        self.WaterPump.write(command.encode())

    def dispenseSolution(self,operation_time):
        time.sleep(2)
        command = '-1'
        self.SolutionPump.write(command.encode())
        time.sleep(operation_time)
        command = '0'
        self.SolutionPump.write(command.encode())

    def rotatePad(self,):
        time.sleep(2)
        command = '1'
        self.Rotor.write(command.encode())

    def stopPad(self,):
        time.sleep(2)    
        command = '0'
        self.Rotor.write(command.encode())

    def dispense(self, soluation_type = 'Solution' ,mode_type='virtual'):
        """
        start Polishing Tool
        
        :param soluation_type(str) : soluation_type (ex. "Solution", "Water")
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: res_msg --> (str)
        """
        
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        if mode_type == "real" :
            if soluation_type == 'Solution':
                msg = "Solution disepensing Start"
                self.logger_obj.debug(debug_device_name, msg)

                self.dispenseSolution(5)
                msg = "Solution dispensing Done"
                self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
                res_msg = debug_device_name + " : " + msg
            elif soluation_type == 'Water':
                msg = "Water disepensing Start"
                self.logger_obj.debug(debug_device_name, msg)

                self.dispenseWater(5)
                msg = "Water dispensing Done"
                self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
                res_msg = debug_device_name + " : " + msg

            return res_msg

        elif mode_type == "virtual" :
            msg = "{} dispensing Start".format(soluation_type)
            self.logger_obj.debug(debug_device_name, msg)

            msg = "{} dispensing Done".format(soluation_type)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg
        

    def polishing(self, operation_time:int=30, mode_type='virtual'):
        """
        start Polishing Tool

        :param operation_time="virtual" (str): set virtual or real mode        
        :param mode_type="virtual" (str): set virtual or real mode
        
        :return: res_msg --> (str)
        """
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        if mode_type == "real" :
            msg = "Polishing tool operate .. Operation time : {} s".format(operation_time)
            self.logger_obj.debug(debug_device_name, msg)

            self.rotatePad()
            msg = "Operation Start!"
            self.logger_obj.debug(debug_device_name, msg)

            time.sleep(operation_time)

            self.stopPad()
            msg = "Operation stop!"
            self.logger_obj.debug(debug_device_name, msg)

            msg = "Polishing Done, Operation Time : {} s".format(operation_time)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg

        elif mode_type == "virtual" :
            msg = "Polishing tool operate .. Operation time : {} s".format(operation_time)
            self.logger_obj.debug(debug_device_name, msg)

            msg = "Polishing Done, Operation Time : {} s".format(operation_time)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg

            return res_msg

if __name__ == "__main__" :
    
    NodeLogger_obj = NodeLogger(platform_name="Electrochemical Analysis", setLevel="DEBUG",
                            SAVE_DIR_PATH="C:/Users/Evaluation/Desktop/EVALUATIONPLATFORM")
    
    Polishingtool = PolishingTool(logger_obj=NodeLogger_obj)
    
    # time.sleep(2)

    Polishingtool.heartbeat()

    Polishingtool.dispense('Solution','real')
    # Polishingtool.polishing(20,'real')
    # # time.sleep(2)
 
    # # Polishingtool.dispense('Water','real')

    # Polishingtool.rotatePad()
    # time.sleep(2)
    
    # Polishingtool.stopPad()

    # # Polishingtool.dispenseSolution(5)