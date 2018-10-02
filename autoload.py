#!/usr/bin/env python
import os
import sys
import time
import json
import paramiko
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

if len(sys.argv) < 2:
    print("argument: file not speicifed")
    sys.exit(1)

ip = sys.argv[1]
localpath = sys.argv[2]
username = "crestron"
password = ""


def run():
    errlog = open("autoload_error.log", "w")
    client = paramiko.SSHClient()

    known_hosts = os.path.join(os.path.dirname(__file__), 'known_hosts')
    print("[-] Loading local known hosts file: '{0}'".format(known_hosts))

    sftp = None
    client.load_host_keys(known_hosts)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        try:
            print("[-] Trying to connect to '{0}@{1}'".format(username, ip))
            client.connect(ip, port=22, username=username, password=password, auth_timeout=5, timeout=10)
            print(client.transport.get_banner().decode("ansi"), "\n")
            print("[-] Connected to '{0}'".format(ip))

            print("[-] Opening SFTP channel")
            sftp = client.open_sftp()
            filepath = '/Program01/PROGRAM.lpz'
            sftp.put(localpath, filepath)
            print("[-] Loaded '{0}' to server".format(localpath))

            stdin, stdout, stderr = client.exec_command("PROGLOAD -P:1")
            response = stdout.read().decode("ansi").strip()
            if len(response) != 0:
                print(response)

        except TimeoutError:
            errlog.write("[-] Operation timed out\n")
        except paramiko.ssh_exception.BadHostKeyException:
            errlog.write("[-] Host key could not be verified\n")
        except paramiko.ssh_exception.AuthenticationException:
            errlog.write("[-] Authentication failed\n")
        except paramiko.ssh_exception.SSHException:
            errlog.write("[-] SSH connection could not be established\n")
        except paramiko.ssh_exception.socket.error as ex:
            errlog.write("[-] Socket error: {0}\n".format(ex))

    except EOFError as ex:
        errlog.write(ex.__str__() + "\n")

    finally:
        if (sftp != None): sftp.close()
        client.close()


run()
print("\n\n** DONE **")
