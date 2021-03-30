#!/usr/bin/python3
import os
import argparse
import time
import paramiko
from scp import SCPClient
import sys


# import subprocess

default_base_dir = str(os.getcwd())

def is_file_modified(th_time = 3, file = ""):
    modTimesinceEpoc = os.path.getmtime(file)
    modificationTime = time.strftime('%Y-%m-%d:%H:%M:%S', time.localtime(modTimesinceEpoc))
    now = time.strftime('%Y-%m-%d:%H:%M:%S', time.localtime())
    # hour_file = modificationTime.split(":")[1]
    minutes_file = modificationTime.split(":")[2]
    # hour_now = now.split(":")[1]
    minutes_now = now.split(":")[2]
    
    if(abs(int(minutes_now) - int(minutes_file)) <= th_time ):
        return True
    return False

def createSSHClient(hostname = "127.0.0.1", port = 22, user = "user", password = None, path_ssh_key = None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, port=port, username=user, password=password, key_filename=path_ssh_key)
    return client

def walk_dir_and_send_scp(base_dir=".", connection = None):
    path = None
    file = None
    for root, dirs, files in os.walk(base_dir):
        path = root.split(os.sep)
        print((len(path) - 1) * '--', os.path.basename(root))
        for file in files:
            is_modified = is_file_modified(file = root + "/" + file)
            # print(is_modified)
            print(len(path) * '  ',">" +  file)
            if(is_modified):
                connection.put(root + "/" + file, root + "/" + file)
                # Uploading the 'test' directory with its content in the
                # '/home/user/dump' remote directory
                # connection.put('test', recursive=True, remote_path='/home/user/dump')
                # subprocess.run(["scp", "-i {}".format(path_ssh_key), root + "/" + file, "{}@{}:{}".format(server, ip, root + "/" + file)])

def progress(filename, size, sent):
    sys.stdout.write("%s's progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )

def main():
    # ssh = createSSHClient(hostname=args["server_ip"], user=args["server_name"], path_ssh_key=args["path_ssh_key"] )
    ssh = createSSHClient(hostname=args["server_ip"], user=args["server_name"], path_ssh_key=None)    
    scp = SCPClient(ssh.get_transport(), progress=progress)
    walk_dir_and_send_scp(args["base_dir"], scp)
    ssh.close()
    scp.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-bd", "--base_dir", required=False, default=default_base_dir, type=str, help="Base Dir absolut path")
    ap.add_argument("-ip", "--server_ip", required=False, default="127.0.0.1", type=str, help="External server ip")
    ap.add_argument("-name", "--server_name", required=False, default="user", type=str, help="External server name")
    ap.add_argument("-key", "--path_ssh_key", required=False, default="~/.ssh/ssh_key", type=str, help="Path to our ssh key")
    args = vars(ap.parse_args())
    main()