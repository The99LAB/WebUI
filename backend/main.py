from flask import Flask, request, json
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
    emit("vm_results", vm_results)

@app.route('/api/host/shutdown', methods=['POST'])
def shutdown():
    print("request to shutdown")
    return ""

@app.route('/api/host/reboot', methods=['POST'])
def reboot():
    print("request to reboot")
    return ""

@app.route('/api/vm-manager/create', methods=['POST'])
def createvm():
    print("request to create vm")
    # get form data
    name = request.form.get('name')
    os = request.form.get('os')
    machine = request.form.get('machine')
    bios = request.form.get('bios')
    memory_min = request.form.get('memory_min')
    memory_min_unit = request.form.get('memory_min_unit')
    memory_max = request.form.get('memory_max')
    memory_max_unit = request.form.get('memory_max_unit')
    disk_size = request.form.get('disk_size')
    disk_size_unit = request.form.get('disk_size_unit')
    disk_type = request.form.get('disk_type')
    disk_bus = request.form.get('disk_bus')
    cdrom_bus = request.form.get('cdrom_bus')
    network_source = request.form.get('network_source')
    network_model = request.form.get('network_model')
    print(request.form)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

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
