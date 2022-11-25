from flask import Flask
from flask_socketio import SocketIO, Namespace, emit
import psutil

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='http://localhost:9000')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
vm_results = [{
    "uuid": "1",
    "name": "win10",
    "memory": "4096",
    "vcpus": "8",
    "state": 'Running'

},
    {
    "uuid": "1",
    "name": "macOS-Ventura",
    "memory": "8192",
    "vcpus": "4",
    "state": 'Running'

}]
# socketio = SocketIO(app, cors_allowed_origins='http://localhost:8080')


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
# class DownloadISO(Namespace):
#     def on_connect(self):
#         emit("testevent", "connected")
# socketio.on_namespace(DownloadISO('/testnamespace'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
