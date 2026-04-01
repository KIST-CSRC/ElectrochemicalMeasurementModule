
from Log.Logging_Class import NodeLogger
from RDEModule_Class import RDEmodule
from RobotTransferUnit.RobotTransferUnit_Class import RobotTransferUnit

from Log.Logging_Class import NodeLogger
from BaseUtils.TCP_Node import BaseTCPNode, TCP_Class
import socket
import time, sys
import threading
import json

def callRDEMODULE_0(input_client_socket, input_hardware_name, input_action_type, input_action_info, input_mode_type):
    if input_action_type == "heartbeat":  
        res_msg = RDEMODULE_0_obj.heartbeat()
        base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, input_hardware_name, input_action_type)
    elif input_action_type == 'setupCell':
        mfc_flow = input_action_info
        res_msg = RDEMODULE_0_obj.setupCell(mfc_flow=int(mfc_flow), mode_type=input_mode_type)
        base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, input_hardware_name, input_action_type)
    elif input_action_type == 'moveRDE':
        position = input_action_info
        res_msg = RDEMODULE_0_obj.moveRDE(position=position, mode_type=input_mode_type)
        base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, input_hardware_name, input_action_type)
    elif input_action_type == 'prepareElectrode':
        dry_rpm, dry_time, humid_time = str(input_action_info).split(sep="&")
        res_msg = RDEMODULE_0_obj.prepareElectrode(dry_rpm=int(dry_rpm),dry_time=int(dry_time),humid_time=int(humid_time), mode_type=input_mode_type)
        base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, input_hardware_name, input_action_type)
    elif input_action_type == 'startEvaluation':
        eval_rpm, param_dict_list = str(input_action_info).split(sep="&")
        res_msg = RDEMODULE_0_obj.startEvaluation(eval_rpm=int(eval_rpm),param_dict_list=json.loads(param_dict_list), mode_type=input_mode_type)
        base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, input_hardware_name, input_action_type)
    elif input_action_type == 'polishElectrode':
        polish_cycles = input_action_info
        res_msg = RDEMODULE_0_obj.polishElectrode(polish_cycles=int(polish_cycles), mode_type=input_mode_type)
        base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, input_hardware_name, input_action_type)
    else:  
        raise ValueError("[{}] Packet Error : Packet length is different".format(input_hardware_name))
    pass 

def callROBOTTRANSFERUNIT(input_client_socket, input_hardware_name, input_action_type, input_action_info, input_mode_type):
    if input_action_type =="location":
        location_index = input_action_info
        res_msg = ROBOTTRANSFERUNIT_obj.move2Location(int(location_index), mode_type=input_mode_type)
        base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, input_hardware_name, input_action_type)
    elif input_action_type == 'heartbeat':
        res_msg = ROBOTTRANSFERUNIT_obj.heartbeat()
        base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, input_hardware_name, input_action_type)
    else:  
        raise ValueError("[{}] Packet Error : Packet length is different".format(input_hardware_name))
    pass 

def handle_client(input_client_socket, input_NodeLogger_obj, input_RDEMODULE_0_obj, input_ROBOTTRANSFERUNIT_obj, input_DS_E_obj, input_PIPETTE_obj, input_base_tcp_node_obj, input_qhold_jobID_list, input_qhold_packet_list, input_restart_jobID_list):
    while True:
        data = input_client_socket.recv(4096)  # 클라이언트로 부터 데이터를 받음. 출력되는 버퍼 사이즈. (만약 2할 경우, 2개의 데이터만 전송됨)
        if str(data.decode())=='':
            continue
        packet_info = str(data.decode()).split(sep="/")
        input_NodeLogger_obj.info("ElectrochemicalAnalysis", "packet information list:{}".format(packet_info))

        if packet_info[0]!="qhold" and packet_info[0]!="qrestart" and packet_info[0]!="qdel" and packet_info[0]!="qshutdown" and packet_info[0]!="info":
            jobID, hardware_name, action_type, action_info, mode_type = packet_info
            jobID=int(jobID)
            if jobID not in input_qhold_jobID_list:
                if hardware_name == "RDEMODULE_0":
                    callRDEMODULE_0(input_client_socket, hardware_name, action_type, action_info,mode_type)
                elif hardware_name == "ROBOTTRANSFERUNIT":
                    callROBOTTRANSFERUNIT(input_client_socket, hardware_name, action_type, action_info, mode_type)
         
                #TCP node for DS, Pipette
                elif hardware_name == "DS_E":
                    res_msg=input_DS_E_obj.callServer(command_byte=data)
                    input_base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, hardware_name, action_type)
                elif hardware_name == "PIPETTE":
                    res_msg=input_DS_E_obj.callServer(command_byte=data)
                    input_base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, hardware_name, action_type)

                else:
                    raise ValueError("[{}] Packet Error : hardware_name is wrong".format(hardware_name))
            
            elif jobID in input_qhold_jobID_list:
                print("holded jobID : ",jobID)
                print("current input_qhold_jobID_list : ", input_qhold_jobID_list)
                packet_info.append(input_client_socket)
                input_qhold_packet_list[jobID]=packet_info
                while True:
                    time.sleep(1)
                    if input_restart_jobID_list[0] not in input_qhold_jobID_list:
                        pass
                    else:
                        break
                popped_packet_info=input_qhold_packet_list.pop(input_restart_jobID_list[0])
                input_qhold_jobID_list.remove(input_restart_jobID_list[0])
                input_qhold_packet_list.insert(input_restart_jobID_list[0], 0)
                input_restart_jobID_list[0]="?"
                jobID, popped_hardware_name, popped_action_type, popped_action_info, popped_mode_type, popped_client_socket=popped_packet_info
                if popped_hardware_name == "RDEMODULE_0":
                    callRDEMODULE_0(input_client_socket, hardware_name, action_type, action_info, mode_type)
                elif popped_hardware_name == "ROBOTTRANSFERUNIT":
                    callROBOTTRANSFERUNIT(input_client_socket, hardware_name, action_type, action_info, mode_type)
                
                #TCP
                elif popped_hardware_name == "DS_E":
                    res_msg=DS_E_obj.callServer(command_byte=data)
                    input_base_tcp_node_obj.checkSocketStatus(popped_client_socket, res_msg, popped_hardware_name, popped_action_type)
                elif popped_hardware_name == "PIPETTE":
                    res_msg=DS_E_obj.callServer(command_byte=data)
                    input_base_tcp_node_obj.checkSocketStatus(popped_client_socket, res_msg, popped_hardware_name, popped_action_type)
                # elif popped_hardware_name == "ROBOTTRANSFERUNIT":
                #     res_msg=DS_E_obj.callServer(command_byte=data)
                #     input_base_tcp_node_obj.checkSocketStatus(popped_client_socket, res_msg, popped_hardware_name, popped_action_type)                  
                
                else:
                    res_msg="Packet Error : popped_hardware_name is wrong ({})".format(popped_hardware_name)
                    input_base_tcp_node_obj.checkSocketStatus(popped_client_socket, res_msg, popped_hardware_name, popped_action_type)
                    raise ValueError("[{}] Packet Error : popped_hardware_name is wrong".format(popped_hardware_name))
            else:
                res_msg="[{}] Packet Error : command_byte is wrong".format(jobID)
                input_base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, "jobID", "command_byte is wrong")
                raise ValueError("[{}] Packet Error : command_byte is wrong".format(jobID))    
        elif packet_info[0]=="info":
            total_dict = {}
            input_RDEMODULE_0_obj.heartbeat()
            input_ROBOTTRANSFERUNIT_obj.heartbeat()

            total_dict["RDE_MODULE"]=input_RDEMODULE_0_obj.info
            total_dict["DS_E"]=input_DS_E_obj.info
            total_dict["PIPETTE"]=input_PIPETTE_obj.info
            total_dict["ROBOTTRANSFERUNIT"]=input_ROBOTTRANSFERUNIT_obj.info

            NodeLogger_obj.debug("Module Node (ElectrochemicalAnalysis)", total_dict)
            input_base_tcp_node_obj.checkSocketStatus(input_client_socket, total_dict, "info", "getInformation")
        elif packet_info[0]=="qhold":
            input_hold_jobID=int(packet_info[1])
            input_qhold_jobID_list.append(input_hold_jobID)
            res_msg="qhold:jobID {} is holded".format(input_hold_jobID)
            NodeLogger_obj.debug("Module Node (ElectrochemicalAnalysis)", res_msg)
            input_base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, "jobID", res_msg)
        elif packet_info[0]=="qrestart":
            request_restart_jobID=int(packet_info[1])
            input_restart_jobID_list[0]=request_restart_jobID
            if request_restart_jobID not in input_qhold_jobID_list:
                res_msg="jobID not in input_qhold_jobID_list"
                input_base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, "qrestart", res_msg)
            else:
                res_msg="qrestart:jobID {} is restarted".format(request_restart_jobID)
                input_base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, "qrestart", res_msg)
        elif packet_info[0]=="qdel":
            input_del_jobID=int(packet_info[1])
            input_del_jobID_index=input_qhold_jobID_list.index(input_del_jobID)
            input_qhold_jobID_list.pop(input_del_jobID_index) # initialize index
            input_qhold_packet_list[input_del_jobID_index]="?" # initialize element to "?" (null)
            res_msg="qdel:jobID {} is deleted".format(input_del_jobID)
            input_base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, "qdel", res_msg)
        elif packet_info[0]=="ashutdown":
            NodeLogger_obj.info("node_manager", "ashutdown")
            input_base_tcp_node_obj.checkSocketStatus(input_client_socket, res_msg, "ashutdown", res_msg)
            sys.exit("shutdown")
        else:
            raise ValueError("[{}] Packet Error : command_byte is wrong".format(packet_info))

def startModuleNode():
    SERVER_HOST='161.122.22.233'  # permit from all interfaces
    SERVER_PORT=54009 # if you want, can change
    SERVER_ACCESS_NUM=100 # permit to accept the number of maximum client

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 20)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(SERVER_ACCESS_NUM) # permit to accept 

    print(f"[ElectrochemicalAnalysis] Server on at {SERVER_HOST}:{SERVER_PORT}.")
    print("[ElectrochemicalAnalysis] Waiting...")
    
    while True:
        # start thread (while loop, wait for client request)
        client_socket, client_address = server_socket.accept()  
        client_thread= threading.Thread(target=handle_client, args=(client_socket, NodeLogger_obj, RDEMODULE_0_obj, ROBOTTRANSFERUNIT_obj, DS_E_obj, PIPETTE_obj, base_tcp_node_obj, qhold_jobID_list, qhold_packet_list, restart_jobID_list))
        client_thread.start()
    

# Emergency Stop via Broadcast
def emergencyStop():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # udp_socket.bind(('192.168.1.11', 54010))
    udp_socket.bind(('161.122.22.233', 54011))
    print(f"[Emergency Stop] Waiting...")
    
    while True:
        data, addr = udp_socket.recvfrom(1024)
        print(f"Broadcast data: {data.decode()} (Client IP: {addr[0]})")
        NodeLogger_obj.info("module node", "emergency stop")
        sys.exit("shutdown")
# TCP/IP
NodeLogger_obj = NodeLogger(platform_name="ElectrochemicalAnalysis", setLevel="DEBUG",
                            SAVE_DIR_PATH="../EVALUATIONPLATFORM")

RDEMODULE_0_obj = RDEmodule(logger_obj=NodeLogger_obj, node_key="RDE0")
ROBOTTRANSFERUNIT_obj = RobotTransferUnit(logger_obj=NodeLogger_obj, ser_port="COM13")
DS_E_obj = TCP_Class("DS_E", NodeLogger_obj)
PIPETTE_obj = TCP_Class("PIPETTE", NodeLogger_obj)

base_tcp_node_obj = BaseTCPNode()
qhold_jobID_list=[]
qhold_packet_list=["?"]*100 # [ ['1', 'LA', '...'....] , []]
restart_jobID_list=["?"]


tcp_thread = threading.Thread(target=startModuleNode)
udp_thread = threading.Thread(target=emergencyStop)

tcp_thread.start()
udp_thread.start()



tcp_thread.join()
udp_thread.join()