# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message
messages_to_send = [] # client.getpeername, message_to_send

# Protocol Messages
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT"
}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR"
}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error

def build_message(cmd, data):
    """
    Gets command name (str) and data field (str) and creates a valid protocol message
    Returns: str, or None if error occured
    """
    full_msg = "{:<{}}|{:0=4}|{}".format( cmd, CMD_FIELD_LENGTH, len(data), data) if len(cmd) <= CMD_FIELD_LENGTH and len(data) <= MAX_DATA_LENGTH else ERROR_RETURN
    return full_msg

def build_and_send_message(client_socket, code, msg=''):
        full_msg = build_message(code, str(msg))
        messages_to_send.append((client_socket, full_msg))
        # client_socket.send(full_msg.encode())
        print("client_socket=", client_socket, "messages_to_send=", messages_to_send)
        print("[SERVER] ", client_socket.getsockname(), 'msg: ',full_msg)         # Debug print

def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    data_split = data.split('|')
    test_length = data_split[1].strip().isnumeric() if len(data) > 0 else False
    if len(data_split) == 3 and test_length:
        cmd = data_split[0].strip()
        msg = data_split[2]
    else:
        cmd, msg = ERROR_RETURN, ERROR_RETURN
    return cmd, msg

def split_data(msg, expected_fields):
    """
        Helper method. gets a string and number of expected fields in it. Splits the string
        using protocol's data field delimiter (|#) and validates that there are correct number of fields.
        Returns: list of fields if all ok. If some error occured, returns None
        """
    msg_split = msg.split("#") if len(msg.split("#")) == expected_fields + 1 else ERROR_RETURN
    return msg_split

def join_data(msg_fields):
    """
        Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter.
        Returns: string that looks like cell1#cell2#cell3
        """
    msg_join = "#".join(msg_fields)
    return msg_join