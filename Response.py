from enum import Enum

class response:

    class ResponseType(Enum):
        MESSAGE_A = 0
        MESSAGE_B = 1
        MESSAGE_C = 2
        MESSAGE_D = 3
        MESSAGE_E = 4

    responsePending = False
    responseID = 0
    responseData = 0

    def __init__(self, _responseID, _responseData):
        self.responseID   = _responseID
        self.responseData = _responseData
        pass

    def check_response_type():
        pass

    def get_response():
        pass

    def register_pending_response(self, new_response):
        self.responseID = new_response.responseID
        self.responseData = new_response.responseData
        self.responsePending = True
        pass

    def ack(self):
        self.responsePending = False
        self.responseID = 0
        self.responseData = 0
        pass