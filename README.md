# DOCUMENTAÇÃO TÉCNICA - SISTEMA CLIENTE-SERVIDOR (TCP/IP)

**Universidade Federal Rural de Pernambuco - Campus UAST**  
**Curso:** Bacharelado em Sistemas de Informação  
**Disciplina:** Redes e Sistemas Internet  
**Docente:** Carlos Batista  
**Discentes:** Emerson Emanoel, Jauann Souza e Thiago Benevide  
**Avaliação:** 3ª Verificação de Aprendizagem

---

## 1. Visão Geral do Projeto

Este projeto consiste na implementação de uma aplicação de chat e transferência de arquivos baseada na arquitetura Cliente-Servidor, utilizando Sockets TCP. O sistema foi desenvolvido para operar em **Dual Stack**, suportando conexões via protocolos **IPv4** e **IPv6** simultaneamente.

A aplicação inclui autenticação de usuários (Login/Cadastro), persistência de dados via SQLite, troca de mensagens em tempo real e transferência segura de arquivos binários e de texto.

## 2. Estrutura de Arquivos

A solução foi modularizada seguindo padrões de separação de responsabilidades (MVC):

- **server.py:** Controlador do servidor. Gerencia conexões simultâneas (threading), escuta em ambas as pilhas de protocolo e processa requisições.
- **client.py:** Interface gráfica (View) e lógica do cliente. Responsável pela interação com o usuário e tratamento de endereçamento de rede.
- **utils.py:** Biblioteca de utilitários compartilhada. Define o protocolo de comunicação, serialização de mensagens e tratamento de buffers.
- **database.py:** Camada de persistência (Model). Gerencia a conexão com o banco de dados SQLite e operações de autenticação.
- **requirements.txt:** Lista de dependências externas necessárias para execução.
- **arquivos/:** Diretório criado automaticamente pelo servidor para armazenar os arquivos recebidos.

---

## 3. Pré-requisitos e Configuração do Ambiente

Recomendo se estiver utilizando ferramentas como o VSCODIM ou o VSCODE instalar as extensões abaixo:

- **Markdown for Humans:** Permite uma visualização renderizada e agradável deste arquivo de documentação (`README.md`).
- **SQLite Viewer:** Permite visualizar rapidamente o conteúdo das tabelas de usuários no arquivo `sistema.db` diretamente pelo editor, sem a necessidade de instalar softwares de terceiros.

Para garantir a execução correta e evitar conflitos de bibliotecas, é **altamente recomendado** o uso de um ambiente virtual Python (`venv`).

### 3.1 Criação e Ativação do Ambiente Virtual (Venv)

Abra o terminal na pasta raiz do projeto e execute os comandos abaixo de acordo com seu sistema operacional:

**No Linux / macOS:**

```bash
# 1. Cria o ambiente virtual
python3 -m venv venv

# 2. Ativa o ambiente
source venv/bin/activate
```

**No Windows:**

```plaintext
# 1. Cria o ambiente virtual
python -m venv venv

# 2. Ativa o ambiente
.\venv\Scripts\activate
```

*Após a ativação, o nome `(venv)` deverá aparecer no início da linha de comando.*

### 3.2 Instalação das Dependências

Com o ambiente virtual ativo, instale as bibliotecas necessárias listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3.3 Configuração de Rede (Máquinas Virtuais)

Caso o teste seja realizado em máquinas virtuais (VirtualBox/VMware):

1. Configure os adaptadores de rede para o modo **Bridge** (Placa em Ponte).
2. Certifique-se de que o Firewall ou iptables das máquinas permitam tráfego de entrada na porta **5000** (TCP).

### 3.4 Verificação de Endereços IP (Comandos)

Antes de iniciar a conexão, identifique os endereços IP da máquina que executará o servidor.

**No Windows:** Abra o Prompt de Comando (CMD) ou PowerShell e execute:

```bash
ipconfig
```

- **IPv4:** Localize a linha "Endereço IPv4" (Ex: `192.168.x.x`).
- **IPv6:** Localize a linha "Endereço IPv6" (Global) ou "Endereço IPv6 de Link Local" (Começa com `fe80::`).

**No Linux:** Abra o terminal e execute:

```bash
ip addr
```

- **IPv4:** Localize o termo `inet` seguido do endereço (Ex: `192.168.x.x`).
- **IPv6:** Localize o termo `inet6` seguido do endereço (Ex: `fe80::...` ou `aaaa::...`).

---

## 4. Manual de Execução

Siga os passos abaixo para iniciar o sistema. O servidor deve ser executado antes de qualquer cliente.

### Passo 1: Inicialização do Servidor

No terminal da máquina designada como servidor (com a venv ativa), execute:

```bash
python server.py
```

O sistema exibirá a mensagem de confirmação indicando que está escutando em todos os endereços disponíveis (`::`), abrangendo tanto IPv4 quanto IPv6 na porta **5000**.

### Passo 2: Inicialização do Cliente

Na máquina do cliente (com a venv ativa), execute:

```bash
python client.py
```

A interface gráfica de configuração de conexão será exibida.

---

## 5. Procedimentos de Conexão (Cenários de Teste)

O sistema suporta três modalidades de conexão. Utilize a aba correspondente na interface do cliente.

### Cenário A: Conexão IPv4

Utilizada para redes legadas ou testes simples.

1. Selecione a opção **IPv4**.
2. No campo IP, insira o endereço do servidor (ex: `192.168.1.15`).
3. Mantenha a porta **5000**.
4. Clique em **Conectar**.

### Cenário B: Conexão IPv6 (Endereçamento Global ou Manual)

Recomendado para testes isolados onde endereços estáticos foram configurados (ex: `aaaa::1`).

1. Selecione a opção **IPv6**.
2. No campo IP, insira o endereço IPv6 do servidor (ex: `aaaa::1`).
3. Mantenha a porta **5000**.
4. Clique em **Conectar**.

### Cenário C: Conexão IPv6 (Link-Local com Scope ID)

Utilizada quando não há servidor DHCPv6, fazendo uso dos endereços autoconfigurados (`fe80::...`). O sistema trata automaticamente a sintaxe de identificação de interface.

1. Identifique o IP Link-Local da máquina servidor (ex: `fe80::20c:29ff:fe45:6789`).
2. Identifique o nome ou índice da interface de rede **da máquina cliente** (ex: `wlo1` no Linux ou `12` no Windows).
3. No campo IP do cliente, insira o endereço seguido do delimitador `%` e a interface.
  - **Sintaxe:** `[Endereço_Servidor]%[Interface_Cliente]`
  - **Exemplo:** `fe80::20c:29ff:fe45:6789%wlo1`
4. Clique em **Conectar**.

### 5.1: Configuração de Rede Dual-Stack (IPv4 e IPv6) em KVM (OPCIONAL)

### Passo 1: Habilitar o IPv6 no Host (Computador Principal)

Por padrão, o KVM cria apenas uma rede IPv4. Precisamos adicionar o suporte ao IPv6 no "roteador virtual" do seu Fedora.

1. Abra o terminal no seu **Fedora** e edite a rede padrão:

```bash
sudo virsh net-edit default
```

1. O arquivo de configuração vai abrir. Procure o bloco que tem o IPv4 (`192.168...`) e adicione a linha do IPv6 logo abaixo dele, conforme o modelo:

```xml
<network>
  <ip address='192.168.122.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.122.2' end='192.168.122.254'/>
    </dhcp>
  </ip>

  <ip family='ipv6' address='fd00::1' prefix='64'/>

</network>

```

Salve e feche o editor (`Esc`, depois digite `:wq` e `Enter`).

### Passo 2: Aplicar as Alterações

Para que o novo endereço funcione, é obrigatório reiniciar a rede virtual e as máquinas.

Execute no terminal do **Fedora**:

```bash
# 1. Desliga a rede antiga
sudo virsh net-destroy default

# 2. Liga a rede atualizada (com IPv6)
sudo virsh net-start default

# 3. Reinicia a VM para ela pegar o novo IP
sudo virsh reboot nome-da-sua-vm
```

*(Repita o passo 3 para cada VM que você tiver).*

---

### Passo 3: Liberar a Porta na VM (Recebimento)

Para que a VM aceite conexões externas, precisamos abrir a porta no Firewall do sistema convidado (Xubuntu).

1. Acesse o terminal **dentro da VM Xubuntu**.
2. Libere a porta 5000 (usada no seu projeto):

```bash
sudo ufw allow 5000/tcp
```

*(Se o firewall estiver desligado/inativo, a porta já estará aberta, mas é boa prática deixar a regra criada).*

### Passo 4: Identificar os Endereços IPs Corretos

Agora vamos descobrir quais "números" usar para conectar.

1. No terminal da **VM Xubuntu**, rode:

```bash
ip -6 a
```

**Como saber qual é o IP certo?** O comando vai mostrar vários endereços. Use esta regra para filtrar:

- 🔴 **NÃO USE:** Endereços que começam com `fe80:`. (São apenas para uso interno do sistema).
- 🔴 **NÃO COPIE:** O final que tem `%enp1s0` ou `%eth0`.
- 🟢 **USE ESTE:** O endereço que começa com `fd00:`. Este é o seu IP Global acessível.

### Passo 5: Como Conectar (Sintaxe Correta)

Ao colocar o endereço no seu software cliente ou navegador, a forma de escrever muda:

**A. Para Conexão via IPv4:**

- Simples e direto.
- **Exemplo:** `192.168.122.50`

**B. Para Conexão via IPv6 (Atenção aqui!):**

- **No seu Software Python (Socket):** Use o IP "limpo", apenas os números e letras hexadecimais.
  - ✅ Exemplo: `fd00::5054:ff:feb0:ddb9`
  - ❌ Errado: `fd00::5054:ff:feb0:ddb9%enp1s0` (Nunca use o final com %)

---

## 6. Funcionalidades do Sistema

Após a conexão, o fluxo de uso segue as etapas:

1. **Autenticação:** O usuário deve criar uma conta ou utilizar o modo anônimo.
2. **Menu Principal:**
  - **Enviar Mensagem:** Abre o chat para troca de textos. O servidor ecoa a mensagem com identificação de IP de origem.
  - **Enviar Arquivo:** Permite selecionar arquivos locais para upload. O arquivo é salvo no servidor com um prefixo único de ID do usuário para evitar sobrescrita.
  - **Meus Arquivos:** Lista os arquivos enviados pelo usuário logado e permite o download (retorno) para a máquina cliente.