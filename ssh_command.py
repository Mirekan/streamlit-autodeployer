def run_ssh_command(client, command):
    stdin, stdout, stderr = client.exec_command(command, get_pty=False)
    
    # Membaca hasil dari perintah
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    if output:
        print("Output:")
        print(output)
    if error:
        print("Error:")
        print(error)

    return output