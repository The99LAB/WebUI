import subprocess
from .storage_manager_exception import StorageManagerException

def get():
    try:
        output = subprocess.check_output(['pdbedit', '-L'])
        output = output.decode("utf-8")
        lines = output.split("\n")
        users = []
        for line in lines:
            if line.strip() == "":
                continue
            users.append(line.split(":")[0])
        return users
    except subprocess.CalledProcessError:
        return []

def lookup(name):
    try:
        output = subprocess.check_output(['pdbedit', '-v', '-L', name], stderr=subprocess.DEVNULL)
        output = output.decode("utf-8")
        return output
    except subprocess.CalledProcessError:
        return None

def reset_password(name, password):
    try:
        process = subprocess.Popen(['smbpasswd', '-s', '-a', name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # password needs to be entered twice
        process.stdin.write((password + "\n").encode("utf-8"))
        process.stdin.write((password + "\n").encode("utf-8"))
        process.stdin.close()
        process.wait()
        if process.returncode != 0:
            raise StorageManagerException(f"Failed to reset password for user {name}")
    except subprocess.CalledProcessError:
        raise StorageManagerException(f"Failed to reset password for user {name}")

def delete(name):
    try:
        subprocess.check_output(['smbpasswd', '-x', name])
    except subprocess.CalledProcessError:
        raise StorageManagerException(f"Failed to delete user {name}")