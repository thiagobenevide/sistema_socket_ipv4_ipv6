import socket
import struct
import json
import os

# Configurações Padrão
BUFFER_SIZE = 4096
CODIFICACAO = 'utf-8'

# Protocolo de Comandos
CMD_LOGIN = 'LOGIN'
CMD_REGISTER = 'REGISTER'
CMD_ANON = 'ANON'
CMD_CHAT = 'CHAT'
CMD_UPLOAD_REQ = 'UPLOAD_REQ'  # Requisitar upload
CMD_UPLOAD_DATA = 'UPLOAD_DATA' # Enviar dados
CMD_LIST_FILES = 'LIST_FILES'
CMD_DOWNLOAD_REQ = 'DOWNLOAD_REQ'

def send_msg(sock, data):
    """Envia mensagens em formato JSON com prefixo de tamanho."""
    msg_json = json.dumps(data).encode(CODIFICACAO)
    # Envia o tamanho da mensagem primeiro (4 bytes, big endian)
    msg_len = struct.pack('>I', len(msg_json))
    sock.sendall(msg_len + msg_json)

def recv_msg(sock):
    """Recebe mensagens JSON baseadas no prefixo de tamanho."""
    try:
        raw_msglen = recv_all(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        raw_msg = recv_all(sock, msglen)
        return json.loads(raw_msg.decode(CODIFICACAO))
    except Exception:
        return None

def recv_all(sock, n):
    """Função auxiliar para garantir recebimento de N bytes."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data