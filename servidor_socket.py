import socket
import threading
import os
from basedados import Database
import utils

HOST = '::' # Escuta IPv4 e IPv6
PORT = 5000
ARQUIVOS_DIR = 'arquivos'

if not os.path.exists(ARQUIVOS_DIR):
    os.makedirs(ARQUIVOS_DIR)

db = Database()

def handle_client(conn, addr):
    print(f"Nova conexão: {addr}")
    client_id = None # None = Anônimo ou não logado
    client_user = "ANONIMO"
    
    try:
        while True:
            request = utils.recv_msg(conn)
            if not request:
                break
            
            cmd = request.get('cmd')
            payload = request.get('data')

            response = {'status': 'error', 'msg': 'Comando desconhecido'}

            # --- Lógica de Autenticação ---
            if cmd == utils.CMD_ANON:
                client_id = 0
                response = {'status': 'ok', 'msg': 'Modo anônimo iniciado'}
            
            elif cmd == utils.CMD_REGISTER:
                success, msg = db.registrar_cliente(payload['user'], payload['pass'])
                response = {'status': 'ok' if success else 'error', 'msg': msg}
            
            elif cmd == utils.CMD_LOGIN:
                uid = db.autenticar_cliente(payload['user'], payload['pass'])
                if uid:
                    client_id = uid
                    client_user = payload['user']
                    response = {'status': 'ok', 'msg': 'Login realizado!'}
                else:
                    response = {'status': 'error', 'msg': 'Credenciais inválidas'}

            # --- Lógica do Sistema Principal (Requer login ou anonimo iniciado) ---
            elif cmd == utils.CMD_CHAT:
                # Formato: CLIENTE(IP|PORTA): Mensagem
                msg_formatada = f"CLIENTE({addr[0]}|{addr[1]}): {payload}"
                response = {'status': 'ok', 'msg': msg_formatada}

            elif cmd == utils.CMD_UPLOAD_REQ:
                if client_id is None:
                    response = {'status': 'error', 'msg': 'Não autenticado'}
                else:
                    filename = payload['filename']
                    filesize = payload['filesize']
                    
                    # Nome seguro: [ID] nome_arquivo
                    safe_name = f"[{client_id}] {os.path.basename(filename)}"
                    filepath = os.path.join(ARQUIVOS_DIR, safe_name)
                    
                    # Envia OK para o cliente começar a transmitir bytes
                    utils.send_msg(conn, {'status': 'ready'})
                    
                    # Recebe os bytes brutos do arquivo
                    received = 0
                    with open(filepath, 'wb') as f:
                        while received < filesize:
                            chunk = conn.recv(min(filesize - received, 4096))
                            if not chunk: break
                            f.write(chunk)
                            received += len(chunk)
                    
                    response = {'status': 'ok', 'msg': 'Arquivo salvo com sucesso'}

            elif cmd == utils.CMD_LIST_FILES:
                if client_id is None or client_id == 0:
                     response = {'status': 'error', 'msg': 'Apenas usuários logados'}
                else:
                    # Lista arquivos que começam com [ID]
                    prefix = f"[{client_id}] "
                    files = [f.replace(prefix, "") for f in os.listdir(ARQUIVOS_DIR) if f.startswith(prefix)]
                    response = {'status': 'ok', 'files': files}

            elif cmd == utils.CMD_DOWNLOAD_REQ:
                filename = payload
                prefix = f"[{client_id}] "
                real_name = prefix + filename
                filepath = os.path.join(ARQUIVOS_DIR, real_name)

                if os.path.exists(filepath):
                    filesize = os.path.getsize(filepath)
                    utils.send_msg(conn, {'status': 'ok', 'filesize': filesize})
                    # Envia bytes
                    with open(filepath, 'rb') as f:
                        while (chunk := f.read(4096)):
                            conn.sendall(chunk)
                    continue # Loop continua, não envia resposta JSON padrão aqui
                else:
                    response = {'status': 'error', 'msg': 'Arquivo não encontrado'}

            utils.send_msg(conn, response)

    except Exception as e:
        print(f"Erro com cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"Conexão fechada: {addr}")

def start_server():
    # Configuração Dual Stack (IPv4 e IPv6)
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    
    try:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Servidor ouvindo em {HOST}:{PORT} (IPv4/IPv6)")
        
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    start_server()