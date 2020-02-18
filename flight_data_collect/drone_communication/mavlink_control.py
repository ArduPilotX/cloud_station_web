from pymavlink import mavutil
import socket
import json
from flight_data_collect.drone_communication.mavlink_constants import MAVLINK_MSG_ID_SET_MODE
SERVER_IP = socket.gethostbyname(socket.gethostname())

def change_vehilce_mode(connect_address:int, mode:str)->str:
    try:
        mavlink = mavutil.mavlink_connection(SERVER_IP+':'+connect_address)
        if mode not in mavlink.mode_mapping():
            return {"ERROR": f"{mode} is not a valid mode. Try: {list(mavlink.mode_mapping().keys())}"}
        mavlink.set_mode(mode)
        ack_msg = mavlink.recv_match(type="COMMAND_ACK", condition=f'COMMAND_ACK.command=={MAVLINK_MSG_ID_SET_MODE}', blocking=True, timeout=6)
        if ack_msg:
            ack_msg = ack_msg.to_dict()
            ack_msg['command'] = 'SET_MODE'
            ack_msg['result'] = mavutil.mavlink.enums['MAV_RESULT'][ack_msg['result']].description
            return ack_msg
        else:
            return {"ERROR": "No ack_msg received (timeout 6s)."}
    except Exception as e:
        print(e)
        return {"ERROR": "Set Mode command failed!"}
    

def set_waypoint(connect_address:int, waypoint)->bool:
    pass

