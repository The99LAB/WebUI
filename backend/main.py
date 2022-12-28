from flask import Flask
from flask_socketio import SocketIO, Namespace, emit
from flask_cors import CORS
import psutil

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='http://localhost:9000')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
vm_results = [{
    "uuid": "1",
    "name": "win10",
    "memory": "4096",
    "vcpus": "8",
    "state": 'Shutdown', 
    "VNC": True
},
    {
    "uuid": "2",
    "name": "macOS-Ventura",
    "memory": "8192",
    "vcpus": "4",
    "state": 'Shutdown',
    "VNC": False

}]


@socketio.on('connect')
def test_connect(auth):
    print('connected')


@socketio.on('cpuoverall_usage')
def get_overallcpu_usage():
    emit("cpuoverall_usage", psutil.cpu_percent(interval=None, percpu=False))


@socketio.on('mem_usage')
def get_mem_usage():
    emit("mem_usage", psutil.virtual_memory().percent)


@socketio.on('vm_results')
def get_vm_results():
    print("get vm results")
    emit("vm_results", vm_results)


@app.route('/api/vm-manager/<uuid>/start', methods=['POST'])
def startvm(uuid):
    print("request to start vm with uuid: " + uuid)
    for vm in vm_results:
        if vm['uuid'] == uuid:
            vm['state'] = 'Running'

    return "Succeed"


@app.route('/api/vm-manager/<uuid>/stop', methods=['POST'])
def stopvm(uuid):
    print("request to stop vm with uuid: " + uuid)
    for vm in vm_results:
        if vm['uuid'] == uuid:
            vm['state'] = 'Shutdown'
    return "Succeed"


@app.route('/api/vm-manager/<uuid>/forcestop', methods=['POST'])
def forcestopvm(uuid):
    print("request to forcestop vm with uuid: " + uuid)
    for vm in vm_results:
        if vm['uuid'] == uuid:
            vm['state'] = 'Shutdown'
    return "Succeed"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
