import customtkinter as ctk
import socket
import threading
import os
import utils
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SocketClientApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Cliente Socket")
        self.geometry("900x700")
        self.socket = None
        self.user_data = None
        
        # Gerenciador de Frames (Telas)
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.frames = {}
        
        # Inicializa todas as telas
        for F in (ConnectionView, AuthView, LoadingView, MainMenuView, ChatView, UploadView, DownloadView):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ConnectionView")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def connect_server(self, ip, port, is_ipv6):
        # Tela 2: Loading
        self.show_frame("LoadingView")
        threading.Thread(target=self._connect_thread, args=(ip, port, is_ipv6)).start()

    def _connect_thread(self, ip, port, is_ipv6):
        try:
            family = socket.AF_INET6 if is_ipv6 else socket.AF_INET
            self.socket = socket.socket(family, socket.SOCK_STREAM)
            
            
            addr_info = socket.getaddrinfo(ip, port, family=family, proto=socket.IPPROTO_TCP)
            
            # addr_info retorna uma lista. Pegamos o endereço correto (item 4 da tupla)
            target_address = addr_info[0][4]
            
            # Conecta usando o endereço resolvido
            self.socket.connect(target_address)
            # -----------------------------------------------------

            # Se conectar, vai para tela de Auth (Tela 3)
            self.after(0, lambda: self.show_frame("AuthView"))
            
        except Exception as e:
            err_msg = str(e)
            print(f"Erro debug: {err_msg}") 
            self.after(0, lambda: messagebox.showerror("Erro", f"Falha na conexão: {err_msg}"))
            self.after(0, lambda: self.show_frame("ConnectionView"))

    def send_request(self, cmd, data=None):
        """Envia requisição e retorna resposta (bloqueante simples para simplificar o exemplo)"""
        try:
            utils.send_msg(self.socket, {'cmd': cmd, 'data': data})
            return utils.recv_msg(self.socket)
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def send_file(self, filepath):
        try:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            
            # 1. Envia requisição
            utils.send_msg(self.socket, {
                'cmd': utils.CMD_UPLOAD_REQ, 
                'data': {'filename': filename, 'filesize': filesize}
            })
            
            # 2. Aguarda confirmação
            resp = utils.recv_msg(self.socket)
            if resp.get('status') != 'ready':
                return resp
            
            # 3. Envia bytes
            with open(filepath, 'rb') as f:
                while (chunk := f.read(4096)):
                    self.socket.sendall(chunk)
            
            # 4. Aguarda confirmação final
            return utils.recv_msg(self.socket)
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def download_file(self, filename, save_path):
        try:
            # 1. Solicita Download
            utils.send_msg(self.socket, {'cmd': utils.CMD_DOWNLOAD_REQ, 'data': filename})
            
            # 2. Recebe metadados (tamanho)
            resp = utils.recv_msg(self.socket)
            if resp.get('status') == 'error':
                return resp
            
            filesize = resp['filesize']
            
            # 3. Recebe bytes
            received = 0
            with open(save_path, 'wb') as f:
                while received < filesize:
                    chunk = self.socket.recv(min(filesize - received, 4096))
                    if not chunk: break
                    f.write(chunk)
                    received += len(chunk)
            return {'status': 'ok', 'msg': 'Download concluído'}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}



# --- TELAS (VIEWS) ---

class ConnectionView(ctk.CTkFrame): # Tela 1
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ctk.CTkLabel(self, text="Configuração de Conexão", font=("Arial", 24)).pack(pady=20)
        
        self.proto_var = ctk.StringVar(value="IPv4")
        ctk.CTkSegmentedButton(self, values=["IPv4", "IPv6"], variable=self.proto_var).pack(pady=10)
        
        self.entry_ip = ctk.CTkEntry(self, placeholder_text="IP do Servidor (ex: 127.0.0.1 ou ::1)")
        self.entry_ip.pack(pady=10, fill="x", padx=50)
        self.entry_ip.insert(0, "127.0.0.1")
        
        self.entry_port = ctk.CTkEntry(self, placeholder_text="Porta (ex: 5000)")
        self.entry_port.pack(pady=10, fill="x", padx=50)
        self.entry_port.insert(0, "5000")
        
        ctk.CTkButton(self, text="Conectar", command=self.on_connect).pack(pady=20)

    def on_connect(self):
        ip = self.entry_ip.get()
        port = self.entry_port.get()
        is_ipv6 = self.proto_var.get() == "IPv6"
        self.controller.connect_server(ip, port, is_ipv6)

class LoadingView(ctk.CTkFrame): # Tela 2
    def __init__(self, parent, controller):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Conectando ao servidor...", font=("Arial", 20)).pack(expand=True)
        ctk.CTkProgressBar(self, mode="indeterminate").pack(pady=10)

class AuthView(ctk.CTkFrame): # Tela 3 (Menu Pré-Auth)
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="Bem-vindo", font=("Arial", 24)).pack(pady=30)
        
        self.tab = ctk.CTkTabview(self)
        self.tab.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.tab.add("Login")
        self.tab.add("Cadastro")
        self.tab.add("Anônimo")
        
        # Login
        self.l_user = ctk.CTkEntry(self.tab.tab("Login"), placeholder_text="Usuário")
        self.l_user.pack(pady=10)
        self.l_pass = ctk.CTkEntry(self.tab.tab("Login"), placeholder_text="Senha", show="*")
        self.l_pass.pack(pady=10)
        ctk.CTkButton(self.tab.tab("Login"), text="Entrar", command=self.do_login).pack(pady=10)
        
        # Cadastro
        self.r_user = ctk.CTkEntry(self.tab.tab("Cadastro"), placeholder_text="Novo Usuário")
        self.r_user.pack(pady=10)
        self.r_pass = ctk.CTkEntry(self.tab.tab("Cadastro"), placeholder_text="Nova Senha", show="*")
        self.r_pass.pack(pady=10)
        ctk.CTkButton(self.tab.tab("Cadastro"), text="Criar Conta", command=self.do_register).pack(pady=10)
        
        # Anônimo
        ctk.CTkLabel(self.tab.tab("Anônimo"), text="Conversar sem salvar histórico").pack(pady=20)
        ctk.CTkButton(self.tab.tab("Anônimo"), text="Iniciar Chat Anônimo", command=self.do_anon).pack()

    def do_login(self):
        resp = self.controller.send_request(utils.CMD_LOGIN, {'user': self.l_user.get(), 'pass': self.l_pass.get()})
        if resp['status'] == 'ok':
            self.controller.show_frame("MainMenuView")
        else:
            messagebox.showerror("Erro", resp['msg'])

    def do_register(self):
        resp = self.controller.send_request(utils.CMD_REGISTER, {'user': self.r_user.get(), 'pass': self.r_pass.get()})
        messagebox.showinfo("Info", resp['msg'])

    def do_anon(self):
        resp = self.controller.send_request(utils.CMD_ANON)
        if resp['status'] == 'ok':
            self.controller.show_frame("ChatView")

class MainMenuView(ctk.CTkFrame): # Tela 5 (Menu Principal)
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="Menu Principal", font=("Arial", 24)).pack(pady=40)
        
        ctk.CTkButton(self, text="Enviar Mensagem", height=50, command=lambda: controller.show_frame("ChatView")).pack(pady=10, fill="x", padx=100)
        ctk.CTkButton(self, text="Enviar Arquivo", height=50, command=lambda: controller.show_frame("UploadView")).pack(pady=10, fill="x", padx=100)
        ctk.CTkButton(self, text="Meus Arquivos (Download)", height=50, command=self.go_to_downloads).pack(pady=10, fill="x", padx=100)
        ctk.CTkButton(self, text="Sair", fg_color="red", command=lambda: controller.show_frame("AuthView")).pack(pady=30)

    def go_to_downloads(self):
        self.controller.frames["DownloadView"].refresh_list()
        self.controller.show_frame("DownloadView")

class ChatView(ctk.CTkFrame): # Tela 4
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.chat_area = ctk.CTkTextbox(self, state="disabled")
        self.chat_area.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.input_area = ctk.CTkEntry(self, placeholder_text="Digite sua mensagem...")
        self.input_area.pack(pady=5, padx=10, fill="x")
        self.input_area.bind("<Return>", self.send_msg)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(btn_frame, text="Enviar", command=self.send_msg).pack(side="right", padx=10)
        ctk.CTkButton(btn_frame, text="Voltar", fg_color="gray", command=lambda: controller.show_frame("AuthView")).pack(side="left", padx=10)

    def send_msg(self, event=None):
        msg = self.input_area.get()
        if not msg: return
        
        resp = self.controller.send_request(utils.CMD_CHAT, msg)
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"Você: {msg}\n")
        self.chat_area.insert("end", f"Servidor: {resp['msg']}\n\n")
        self.chat_area.configure(state="disabled")
        self.input_area.delete(0, "end")

class UploadView(ctk.CTkFrame): # Tela 6
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="Upload de Arquivos", font=("Arial", 20)).pack(pady=20)
        
        self.lbl_file = ctk.CTkLabel(self, text="Nenhum arquivo selecionado")
        self.lbl_file.pack(pady=10)
        
        ctk.CTkButton(self, text="Selecionar Arquivo", command=self.select_file).pack(pady=10)
        ctk.CTkButton(self, text="Enviar para Servidor", command=self.do_upload, fg_color="green").pack(pady=10)
        ctk.CTkButton(self, text="Voltar", fg_color="gray", command=lambda: controller.show_frame("MainMenuView")).pack(pady=20)
        
        self.selected_file = None

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Permitidos", "*.png *.csv *.pdf *.jpeg *.jpg *.xml *.json *.txt")])
        if path:
            self.selected_file = path
            self.lbl_file.configure(text=os.path.basename(path))

    def do_upload(self):
        if not self.selected_file: return
        resp = self.controller.send_file(self.selected_file)
        messagebox.showinfo("Status", resp['msg'])

class DownloadView(ctk.CTkFrame): # Tela 7
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="Seus Arquivos", font=("Arial", 20)).pack(pady=20)
        
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkButton(self, text="Voltar", fg_color="gray", command=lambda: controller.show_frame("MainMenuView")).pack(pady=10)

    def refresh_list(self):
        for widget in self.scroll.winfo_children(): widget.destroy()
        
        resp = self.controller.send_request(utils.CMD_LIST_FILES)
        if resp['status'] == 'ok':
            for f in resp['files']:
                row = ctk.CTkFrame(self.scroll)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=f).pack(side="left", padx=10)
                ctk.CTkButton(row, text="Baixar", width=60, command=lambda name=f: self.do_download(name)).pack(side="right", padx=5)
        else:
             ctk.CTkLabel(self.scroll, text=resp['msg']).pack()

    def do_download(self, filename):
        save_path = filedialog.asksaveasfilename(initialfile=filename)
        if save_path:
            resp = self.controller.download_file(filename, save_path)
            messagebox.showinfo("Download", resp['msg'])

if __name__ == "__main__":
    app = SocketClientApp()
    app.mainloop()