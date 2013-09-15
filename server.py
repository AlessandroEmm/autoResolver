import zeroconf
import sys
from bottle import route, run, template

name    = sys.argv[1]
regtype = sys.argv[2]
port    = int(sys.argv[3])
resolvedPeers = [] 

thread = zeroconf.zeroconf(resolvedPeers, port, regtype, name) 
thread.start()

@route('/contract')
def index():
    return "template('<b>Hello {{name}}</b>!', name=name)"

run(host='0.0.0.0', port=port)
    