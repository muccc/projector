import sys, socket, select
from time import sleep

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
  
  'get_source': '00121 1',
  'set_source' : '0012 {}',
  'hdmi1' : '0012 1',
  'hdmi2' : '0012 15',
  'vga' : '0012 5',

  'menu' : '00140 20',
}

sources = {
  '5': 'vga',
  '7': 'hdmi1',
  '8': 'hdmi2'
}

#@app.route("/projector/<string:name>", methods = ['GET', 'POST'] )

def send_command(cmd, params = ()):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3)
        # connect to remote host
        s.connect((host, port))
        s.send("\r\n")
        
        msg = '~' + cmds[cmd].format(params) + "\r\n"
        print(" ".join("{:02x}".format(ord(c)) for c in msg))
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
                    # only return value after "Ok"
                    return data[2:].strip()
                    #sys.stdout.write(data)

@app.route("/projector/menu", methods = ['GET', 'POST'] )
def show_menu():
  send_command('menu')
  return 'ON'

@app.route("/projector/power", methods = ['GET'] )
def get_power():
    r = send_command('get_power')
    return 'ON' if r == '1' else 'OFF'

@app.route("/projector/power", methods = ['POST'] )
def set_power():
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

@app.route("/projector/source", methods = ['GET'] )
def get_source():
    r = send_command('get_source')
    if r in sources:
        return sources[r] 
    return r

@app.route("/projector/source", methods = ['POST'] )
def set_source():
    value = request.data.lower()
    print(value)
    if value in cmds:
        r = send_command(value)
    else:
        r = send_command('set_source', (value))
    return value


if __name__ == "__main__":
    while True:
        try:
            sleep(5)
            app.run(host='0.0.0.0', port=5001, debug=False)
        except:
            pass
