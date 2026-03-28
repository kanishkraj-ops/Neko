import socket
import subprocess
import shlex
import sys
import threading
import os
from .utils.logger import get_logger

logger = get_logger()

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return ''
    try:
        # Cross-platform command execution
        is_windows = os.name == 'nt'
        output = subprocess.check_output(
            shlex.split(cmd) if not is_windows else cmd, 
            stderr=subprocess.STDOUT, 
            shell=True
        )
        return output.decode()
    except subprocess.CalledProcessError as e:
        return f"[!] Command failed:\n{e.output.decode()}"
    except FileNotFoundError:
        return f"[!] Command not found: {cmd}\n"
    except Exception as e:
        return f"[!] Error executing command: {str(e)}\n"

class NekoCore:
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
            logger.success(f"Connected to {self.args.target}:{self.args.port}")
            
            if self.buffer:
                self.socket.send(self.buffer)

            if hasattr(self.args, 'download') and self.args.download:
                with open(self.args.download, 'wb') as f:
                    while True:
                        data = self.socket.recv(4096)
                        if not data:
                            break
                        f.write(data)
                logger.success(f"Downloaded file: {self.args.download}")
                return

            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode(errors='ignore')
                    if recv_len < 4096:
                        break
                if response:
                    print(response, end='')
                    if "neko:#>" in response:
                        buffer = input('') + '\n'
                    else:
                        buffer = input('> ') + '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            logger.warning('User terminated.')
        except Exception as e:
            logger.error(f'Connection failed: {e}')
        finally:
            self.socket.close()

    def listen(self):
        try:
            self.socket.bind((self.args.target, self.args.port))
            self.socket.listen(5)
            logger.success(f'Listening on {self.args.target}:{self.args.port}')
            while True:
                client_sock, addr = self.socket.accept()
                logger.info(f"Accepted connection from {addr[0]}:{addr[1]}")
                client_thread = threading.Thread(
                    target=self.handle, args=(client_sock,)
                )
                client_thread.start()
        except Exception as e:
            logger.error(f"Failed to bind/listen: {e}")

    def handle(self, client_sock):
        try:
            if hasattr(self.args, 'execute') and self.args.execute:
                output = execute(self.args.execute)
                client_sock.send(output.encode())

            elif hasattr(self.args, 'upload') and self.args.upload:
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

            elif hasattr(self.args, 'download') and self.args.download:
                try:
                    with open(self.args.download, 'rb') as f:
                        file_data = f.read()
                    client_sock.send(file_data)
                except Exception as e:
                    error_msg = f'[!] Failed to read file: {e}'
                    client_sock.send(error_msg.encode())

            elif hasattr(self.args, 'command') and self.args.command:
                cmd_buffer = b''
                while True:
                    client_sock.send(b'neko:#> ')
                    while b'\n' not in cmd_buffer:
                        data = client_sock.recv(64)
                        if not data:
                            break
                        cmd_buffer += data

                    command = cmd_buffer.decode().strip()
                    if not command:
                        cmd_buffer = b''
                        continue
                        
                    if command.lower() in ['exit', 'quit']:
                        client_sock.send(b"Closing connection...\n")
                        break
                        
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
            logger.error(f'Server handler error: {e}')
        finally:
            client_sock.close()
