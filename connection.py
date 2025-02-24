import paramiko

def ssh_connect(host, port, username, password):
    try:
        client = paramiko.SSHClient()

        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(host, port=port, username=username, password=password)

        print(f"Connected to {host}!")
        return client
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None
