
import Response

def init():
    global is_master_online
    global Continue
    global latched_error 
    global error_msg 
    global response_handler
    response_handler = Response.response(0,0)
    is_master_online = True
    Continue = True
    latched_error = False
    error_msg = "None"
