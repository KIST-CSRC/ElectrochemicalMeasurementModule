#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ##
# @brief    [RobotTrasnferUnit] Class for controlling RobotTransferUnit (L7PMotorDriver)
# @author   Daeho Kim (r4576@kist.re.kr)

import logging
import os, sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from pymodbus.client import ModbusSerialClient
import time
from Log.Logging_Class import NodeLogger
from Device_Exception import DeviceError

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

class RobotTransferUnit(DeviceError):
    """ 
    [RobotTransferUnit] RobotTransferUnit Class for controlling in another computer (windows)
    """
    def __init__(self, logger_obj, device_name = "Robot Transfer Unit", ser_port = 'COM13') :
       
        self.logger_obj=logger_obj
        self.info = {
            "PORT" : ser_port,
            "BOUNDRATE" : 57600,
            "ADDRESS" : 1
        }

        # Drive CM처럼 보수적으로: 요청 간 간격/에러시 대기
        self._io_gap_sec = 0.05           # 각 Modbus 요청 전 최소 대기(50ms)
        self._err_backoff_sec = 0.2       # 에러 발생 시 추가 대기
        self._read_tries = 2             
        self._write_tries = 2            

        self.device_name = device_name
        self.client = ModbusSerialClient(
            method="rtu",
            port=self.info["PORT"],
            baudrate=self.info["BOUNDRATE"],
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1.0,
            retries=0,                 
            retry_on_empty=False,
            strict=False,
        )

    # -------------------------
    # Conservative helpers
    # -------------------------
    def _sleep_gap(self):
        time.sleep(self._io_gap_sec)

    def _safe_read_holding(self, addr, count, slave=0x01):
        last_err = None
        for _ in range(self._read_tries + 1):
            try:
                self._sleep_gap()
                rr = self.client.read_holding_registers(addr, count, slave=slave)
                if rr is None or getattr(rr, "isError", lambda: True)():
                    raise IOError(f"Modbus read error: {rr}")
                return rr
            except Exception as e:
                last_err = e
                self.logger_obj.debug(
                    device_name=f"{self.device_name} (_safe_read_holding)",
                    debug_msg=f"read fail: addr={hex(addr)} err={e}"
                )
                time.sleep(self._err_backoff_sec)
        return None 

    def _safe_write_coil(self, addr, value, slave=0x01):
        last_err = None
        for _ in range(self._write_tries + 1):
            try:
                self._sleep_gap()
                rr = self.client.write_coil(addr, value, slave=slave)
                if rr is None or getattr(rr, "isError", lambda: True)():
                    raise IOError(f"Modbus write error: {rr}")
                return rr
            except Exception as e:
                last_err = e
                self.logger_obj.debug(
                    device_name=f"{self.device_name} (_safe_write_coil)",
                    debug_msg=f"write fail: addr={hex(addr)} val={value} err={e}"
                )
                time.sleep(self._err_backoff_sec)
        return None

    def _safe_write_coils(self, addr, values, slave=0x01):
        last_err = None
        for _ in range(self._write_tries + 1):
            try:
                self._sleep_gap()
                rr = self.client.write_coils(addr, values, slave=slave)
                if rr is None or getattr(rr, "isError", lambda: True)():
                    raise IOError(f"Modbus write_coils error: {rr}")
                return rr
            except Exception as e:
                last_err = e
                self.logger_obj.debug(
                    device_name=f"{self.device_name} (_safe_write_coils)",
                    debug_msg=f"write_coils fail: addr={hex(addr)} err={e}"
                )
                time.sleep(self._err_backoff_sec)
        return None

    # -------------------------
    # Original methods (minimal edits)
    # -------------------------
    def heartbeat(self,):
        connection = self._checkConnection()
        debug_device_name="{} ({})".format(self.device_name, "heartbeat")
        debug_msg="Hello World!! Succeed to connection to main computer!"
        self.logger_obj.debug(device_name=debug_device_name, debug_msg=debug_msg)
        return_res_msg="[{}] : {}".format(self.device_name, debug_msg)
        return return_res_msg
    
    def _checkConnection(self):
        error_code = 0
        self.client.connect()
        if not self.client.is_socket_open():
            error_code = 2
            error_msg = "Failed to connect to Modbus/RTU server"
            self.raiseError(error_code, error_msg)
        return error_code
    
    def _checkStatus(self):
        rr = self._safe_read_holding(0x2600, 2, slave=0x01)
        if rr is None:
            # Drive CM처럼: 읽기 실패면 일단 Unknown 처리(상위 루프에서 다시 시도)
            return "Unknown"

        regs = rr.registers
        high_word = regs[1]
        low_word = regs[0]
        speed = (high_word << 16) | low_word
        return "Waiting" if speed == 0 else "Operating"
           
    def _checkLocation(self):
        rr = self._safe_read_holding(0x600E, 2, slave=0x01)
        if rr is None:
            return None

        regs = rr.registers
        high_word = regs[1]
        low_word = regs[0]
        location = (high_word << 16) | low_word

        if 43990000 <= location <= 44010000:
            return 1
        elif -10000 <= location <= 10000:
            return 0
        elif 39990000 <= location <= 40010000:
            return 2
        else:
            error_code = 2
            error_msg = "Invalid Location"
            self.raiseError(error_code, error_msg)
    
    def _number_to_binary_list(self, number,bit):
        binary_str = f'{number:0{bit}b}'
        binary_list = [int(bit) for bit in binary_str]
        return binary_list[::-1]

    def _onIsel(self,index_num):
        data = self._number_to_binary_list(index_num,6)
        return self._safe_write_coils(0x0014, data, slave=0x01)
    
    def _offIsel(self,index_num):
        data = self._number_to_binary_list(index_num,6)
        return self._safe_write_coils(0x0014, data, slave=0x01)
    
    def move2Location(self, location_index:int, mode_type:str='virtual'):
        debug_device_name="{} ({})".format(self.device_name, mode_type)

        msg = "Move RobotTransferUnit ... Location Index : {}".format(location_index)
        self.logger_obj.debug(debug_device_name, msg)

        if mode_type == "real":
            self._checkConnection()

            status = self._checkStatus()
            if status == "Unknown":
                time.sleep(self._err_backoff_sec)
                status = self._checkStatus()

            error_dict = self.checkStatusError('Waiting',status if status!="Unknown" else "Waiting")
            msg ="RobotTransferUnit Waiting? Receive signal! --> Waiting : {}, Status : {}".format(bool(status=='Waiting'), error_dict)
            self.logger_obj.debug(debug_device_name, msg)

            self._onIsel(location_index)

            self._safe_write_coil(0x000C, 1, slave=0x01)
            time.sleep(1)
            msg="Parameter setting done."
            self.logger_obj.debug(debug_device_name, msg)

            time.sleep(1)
            self._safe_write_coil(0x0010, 1, slave=0x01)
            time.sleep(0.5)
            self._safe_write_coil(0x0010, 0, slave=0x01)
            msg = "Operation Start! --> Location Index : {}".format(location_index)
            self.logger_obj.debug(debug_device_name, msg)

            while True :
                time.sleep(3)
                status = self._checkStatus()

                if status == "Unknown":
                    time.sleep(self._err_backoff_sec)
                    continue

                if status == "Operating":
                    pass
                elif status == "Waiting":
                    break
            
            time.sleep(2)

            a = self._safe_write_coil(0x000C, 0, slave=0x01)
            time.sleep(1)

            self._onIsel(location_index)
            msg="Parameter setting done."
            self.logger_obj.debug(debug_device_name, msg)

            time.sleep(1)
            self._safe_write_coil(0x0010, 0, slave=0x01)

            self._checkLocation()

            self.client.close()
            
            msg= "Movement completed, Current location index : {}".format(location_index)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg
            return res_msg
        
        elif mode_type == "virtual":
            msg= "Movement completed, Current location index : {}".format(location_index)
            self.logger_obj.debug(device_name=debug_device_name, debug_msg=msg)
            res_msg = debug_device_name + " : " + msg
            return res_msg

if __name__ == "__main__":
    NodeLogger_obj = NodeLogger(platform_name="Electrochemical Analysis", setLevel="DEBUG",
                            SAVE_DIR_PATH="../EVALUATIONPLATFORM")
    
    Robottransferunit = RobotTransferUnit(logger_obj=NodeLogger_obj )

    for i in range(5) :
        Robottransferunit.move2Location(2,'real')
        time.sleep(0.5)
        Robottransferunit.move2Location(1,'real')


# if __name__ == "__main__":
#     NodeLogger_obj = NodeLogger(platform_name="Electrochemical Analysis", setLevel="DEBUG",
#                             SAVE_DIR_PATH="../EVALUATIONPLATFORM")
    
#     Robottransferunit = RobotTransferUnit(logger_obj=NodeLogger_obj )

#     # Robottransferunit.heartbeat()
#     # print(Robottransferunit._checkStatus())

#     # Robottransferunit.move2Location(0,'real')
#     for i in range(5) :
#         Robottransferunit.move2Location(2,'real')
#         time.sleep(0.5)
#         Robottransferunit.move2Location(1,'real')
#     # a = Robottransferunit.client.write_coils(0x0000, [0] * 32,slave=0x01 )
#     # print(a)
