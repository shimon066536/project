import chatlib, socket, random, select

messages_to_send = [] # client.getpeername, message_to_send
logged_users = {} # a dictionary of client hostnames to usernames - will be used later
ERROR_MSG = "Error! "
SERVER_PORT = 8856
SERVER_IP = "0.0.0.0"

def print_client_sockets(client_sockets):
    print("def print_client_sockets(client_sockets):")
    for c in client_sockets:
         print("\t", c.getpeername())

def build_and_send_message(client_socket, code, msg=''):
    print("def build_and_send_message(client_socket, code, msg=''):")
    full_msg = chatlib.build_message(code, str(msg))
    messages_to_send.append((client_socket, full_msg))
    # client_socket.send(full_msg.encode())
    print("client_socket=", client_socket, "messages_to_send=", messages_to_send)
    print("[SERVER] ", client_socket.getsockname(), 'msg: ',full_msg)     # Debug print
    
def recv_message_and_parse(client_socket):
    print("def recv_message_and_parse(client_socket):")
    full_msg = client_socket.recv(1024).decode()
    cmd, data = chatlib.parse_message(full_msg)
    print("[CLIENT] ", client_socket.getpeername(), 'msg: ', full_msg,'cmd=', cmd,'data=',  data)  # Debug print
    return cmd, data
    
def load_questions():
    print("def load_questions():")
    questions = {2313: {"question": "How much is 2+2", "answers": ["3","4","2","1"], "correct": 2}, 4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"], "correct": 3}, 4124: {"question": "What is the capital of israel?", "answers": ["Lion", "jerusalem", "Paris", "Montpellier"], "correct": 2}, 4125: {"question": "What is the capital of usa?", "answers": ["new york", "Marseille", "Paris", "Montpellier"], "correct": 1}}
    return questions
    
def load_user_database():
    print("def load_user_database():")
    users = {"test" :{"password":"test","score":0,"questions_asked":[]}, "yossi"        :   {"password":"123","score":50,"questions_asked":[]}, "master"    :   {"password":"master","score":200,"questions_asked":[]}}
    return users
    
def setup_socket():
    print("def setup_socket():")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    print("Socket server!", sock.getsockname())
    sock.listen()
    print('sock listen\nwaiting for a connection...')
    return sock
    
def create_random_question():
    print("def create_random_question():")
    rand_num = random.choice([i for i in questions])
    rand_quest = "{}#{}#{}".format(rand_num, questions[rand_num]["question"], "#".join(questions[rand_num]["answers"]))
    return rand_quest

def send_error(conn, error_msg):
    print("def send_error(conn, error_msg):")
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], error_msg)

def handle_getscore_message(client_socket, user):
    print("def handle_getscore_message(client_socket, user):")
    global users
    build_and_send_message(client_socket, 'YOUR_SCORE', str(users[user]["score"]))

def handle_highscore_message(client_socket, user):
    print("def handle_highscore_message(client_socket, user):")
    global users
    x = ['{}: {}\n'.format(i, users[i]["score"]) for i in users]
    build_and_send_message(client_socket, 'ALL_SCORE', " ".join(x))

def handle_question_message(client_socket):
    print("def handle_question_message(client_socket):")
    global users
    build_and_send_message(client_socket, 'YOUR_QUESTION', create_random_question())

def handle_answer_message(client_socket, data):
    print("def handle_answer_message(client_socket, data):")
    global users
    num, correct = data.split("#") # type num and correct =  <class 'str'>
    try:
        if int(correct) == questions[int(num)]["correct"]:
            build_and_send_message(client_socket, 'CORRECT_ANSWER')
            users[user]["score"] += 1
        else:
            build_and_send_message(client_socket, 'WRONG_ANSWER', questions[int(num)]["correct"])
    except ValueError:
        handle_logout_message(client_socket, user)

def handle_logged_message(client_socket, user):
    print("def handle_logged_message(client_socket, user):")
    global users
    build_and_send_message(client_socket, 'LOGGED_ANSWER', 'username1, username2…')

def handle_logout_message(client_socket, user):
    print("def handle_logout_message(client_socket, user):")
    global logged_users
    global client_sockets
    logged_users.pop(client_socket.getpeername())
    print("Connection closed", "client_sockets = ", client_sockets)
    client_sockets.remove(client_socket)
    print_client_sockets(client_sockets)
    client_socket.close()

def handle_login_message(client_socket, user, pas):
    print("def handle_login_message(client_socket, user, pas):")
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users  # To be used later
    global count
    if user in users:
        if pas == users[user]["password"]:
            logged_users.update({client_socket.getpeername(): {user: {"password": pas, "score": 0, "questions_asked": []}}})
            build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER["login_ok_msg"])
        else:
            build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER["login_failed_msg"], '{}Password does not match!'.format(ERROR_MSG))
    else:
        build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER["login_failed_msg"], '{}Username does not exist'.format(ERROR_MSG))

def handle_client_message(client_socket, cmd, data=''):
    print("def handle_client_message(client_socket, cmd, data=''):")
    global logged_users  # To be used later
    global user
    global messages_to_send
    if cmd == "LOGIN":
        user, pas = data.split("#")
        handle_login_message(client_socket, user, pas)
    else:
        print('L97 logged_users = ', logged_users)
        print('client_socket.getpeername() = ', client_socket.getpeername())
        if client_socket.getpeername() in logged_users:
            print("if client_socket.getpeername() in logged_users:")
            if cmd == "LOGOUT":
                print("if cmd == 'LOGOUT':")
                handle_logout_message(client_socket, user)
            if cmd == "MY_SCORE":
                print("if cmd == 'MY_SCORE':")
                handle_getscore_message(client_socket, user)
            if cmd == "HIGHSCORE":
                print("if cmd == 'HIGHSCORE':")
                handle_highscore_message(client_socket, user)
            if cmd == "LOGGED":
                print("if cmd == 'LOGGED':")
                handle_logged_message(client_socket, user)
            if cmd == "GET_QUESTION":
                print("if cmd == 'GET_QUESTION':")
                handle_question_message(client_socket)
            if cmd == "SEND_ANSWER":
                print("if cmd == 'SEND_ANSWER':")
                handle_answer_message(client_socket, data)

def main():
    print("def main():")
    global users
    global questions
    global count
    global messages_to_send
    global client_sockets
    print("Welcome to Trivia Server!")
    users = load_user_database()
    questions = load_questions()
    print('Listening for clients...')
    client_sockets = []
    server_socket = setup_socket()
    count = 0
    print(count)
    while True:
        print("L157")
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, [], [])
        count += 1
        print("L160", count)
        for current_socket in ready_to_read:
            print("L162", count)
            print("L163", current_socket)
            if current_socket is server_socket:
                (client_socket, client_address) = current_socket.accept()
                print("New client joined!", client_address, "client_socket =", client_socket, "client_sockets =", client_sockets)
                client_sockets.append(client_socket)
            else:
                print("New data from client ", ready_to_read)
                cmd, data = recv_message_and_parse(current_socket)
                print("L140", count, data)
                if data != '':
                    print("L142 Data isn't None")
                    handle_client_message(current_socket, cmd, data)
                else:
                    print("Data is None")
                    handle_client_message(current_socket, cmd)
        for message in messages_to_send:
            print(message)
            print(messages_to_send)
            message[0].send(message[1].encode())
            messages_to_send.remove(message)

if __name__ == '__main__':
    main()

