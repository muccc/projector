import sys, socket, select

from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

host = '83.133.178.103'
port = 23

cmds = {
     'get_power': '00124 1',
     'on' : '0000 1',
     'off' : '0000 0',
     'menu' : '00140 20'
}


#@app.route("/projector/<string:name>", methods = ['GET', 'POST'] )

# returns True when state in ON and False when state is OFF
def is_on(name):
    return not GPIO.input(p[name]['in'])

def send_command(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    # connect to remote host
    s.connect((host, port))
    s.send("\r\n")
    
    msg = '~' + cmds[cmd] + "\r\n"
    s.send(msg)

    socket_list = [sys.stdin, s]

    # Get the list sockets which are readable
    read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

    for sock in read_sockets:
        #incoming message from remote server
        if sock == s:
            data = sock.recv(4096)
            if not data:
                print('Connection closed by projector?')
                return ''
            else:
                print(data)
                return data
                #sys.stdout.write(data)

@app.route("/projector/menu", methods = ['GET', 'POST'] )
def show_menu():
  send_command('menu')
  return 'ON'

@app.route("/projector/power", methods = ['GET'] )
def get_power():
    r = send_command('get_power')
    print(r)
    if r:
        r = r.strip()
    #print(r[2:])
    return 'ON' if r[2:] == '1' else 'OFF'

@app.route("/projector/power", methods = ['POST'] )
def process_post_request():
    value = request.data.lower()
    if not value:
        return switch_on()

    if value == 'true' or value == 'on':
        return switch_on()
    elif value == 'false' or value == 'off':
        return switch_off()

def switch_on():
    send_command('on')
    return 'ON'

@app.route("/projector/power", methods = ['DELETE'] )
def switch_off():
    send_command('off')
    return 'OFF'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
