from background_task import background
from pymavlink import mavutil
from datetime import datetime
from flight_data_collect.models import Telemetry_log, Location_log
from flight_data_collect.drone_communication import mavlink_constants 
from flightmonitor.consumers import send_message_to_clients
import socket
import json

SERVER_IP = socket.gethostbyname(socket.gethostname())

def connect_mavlink(connect_address: str)->bool:
    try:
        mavlink = mavutil.mavlink_connection(SERVER_IP+':'+connect_address) # hackish fix for now
        msg = mavlink.wait_heartbeat(timeout=8)
        return msg is not None
    except OSError as e:
        print(e)
    return False 

@background(schedule=0)
def get_mavlink_messages_periodically(connect_address):
    mavlink = mavutil.mavlink_connection(SERVER_IP+':'+connect_address)
    msg = mavlink.wait_heartbeat(timeout=8)
    for message_type in mavlink_constants.USEFUL_MESSAGES:
        msg = _get_mavlink_message(mavlink, message_type).to_dict()
        if msg:
            if msg.get("mavpackettype", "") == mavlink_constants.GPS_RAW_INT and _is_gps_fix(msg):
                location_msg = _get_mavlink_message(mavlink, mavlink_constants.GLOBAL_POSITION_INT)
                if location_msg:
                    send_message_to_clients(json.dumps(location_msg))
            parse_mavlink_msg(msg)
            send_message_to_clients(json.dumps(msg))
            

def _is_gps_fix(msg)->bool:
    fix_type = int(msg.get("fix_type", "0"))
    if fix_type >= 2: #2D_fix
        return True
    return False

def parse_mavlink_msg(msg):
    msg_type = msg.get("mavpackettype", "")
    if msg_type==mavlink_constants.GPS_RAW_INT:
        msg["fix_type"] = mavlink_constants.GPS_FIX_TYPE.get(msg["fix_type"], "invalid_fix_type")

def _log_latest_orientation(mavlink, drone_id):
    msg = _get_mavlink_message(mavlink, mavlink_constants.ORIENTATION_MESSAGE_NAME) 
    if msg:
        Telemetry_log.objects.create(timestamp = datetime.now(), \
            roll = round(msg.roll,2), pitch = round(msg.pitch,2), yaw = round(msg.yaw,2), 
            droneid=drone_id)
    
def _log_latest_location(mavlink, drone_id):
    global_position_int = _get_mavlink_message(mavlink, mavlink_constants.GLOBAL_POSITION_INT)
    gps_raw = _get_mavlink_message(mavlink, mavlink_constants.GPS_RAW_INT)
    if gps_raw and gps_raw.fix_type >= mavlink_constants.GPS_2D_FIX and global_position_int:
        Location_log.objects.create(timestamp = datetime.now(), \
            latitude=global_position_int.lat/10**7, longitude=global_position_int.lon/10**7, \
            altitude=global_position_int.alt, heading=global_position_int.hdg, droneid=drone_id)


def _get_mavlink_message(mavlink, message_name)->dict:
    try:
        msg = mavlink.recv_match(type=message_name, blocking=True, timeout=3)
        if msg.get_type() != 'BAD_DATA':
            return msg
    except Exception as e:
        print(e)
        return {"ERROR": msg}