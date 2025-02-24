import streamlit as st
import connection as ssh
import ssh_command as sc
import random

st.title("Laravel")
st.text("Fill the form below to connect to your server and we will run the code for you.")

# Input Form
host = st.text_input("Host", "")
port = st.text_input("Port", "")
username = st.text_input("Username", "")
password = st.text_input("Password", type="password")
project_name = st.text_input("Project Name", "")

database = st.selectbox("Database", ["MySQL", "SQLite"])

# MySQL Credentials (Only needed for MySQL)
if database == "MySQL":
    db_user = st.text_input("Database Username", "root")  
    db_password = st.text_input("Database Password", "", type="password" )  

# Function to get unused port
def get_unused_port(client):
    """Find an unused port on the remote machine."""
    while True:
        unused_port = random.randint(1024, 65535)  # Choose a random port
        sc.run_ssh_command(client, f"lsof -i:{unused_port}")  # Check if the port is in use
        return unused_port

# Function to update .env file without overwriting everything
def update_env_file(client, project_path, db_config):
    """Update the .env file with the new database configuration while keeping other values intact."""
    sc.run_ssh_command(client, f"cp {project_path}/.env.example {project_path}/.env")  # Ensure .env exists

    # Read the current .env file
    sc.run_ssh_command(client, f"sed -i '/DB_CONNECTION=/d' {project_path}/.env")
    sc.run_ssh_command(client, f"sed -i '/DB_HOST=/d' {project_path}/.env")
    sc.run_ssh_command(client, f"sed -i '/DB_PORT=/d' {project_path}/.env")
    sc.run_ssh_command(client, f"sed -i '/DB_DATABASE=/d' {project_path}/.env")
    sc.run_ssh_command(client, f"sed -i '/DB_USERNAME=/d' {project_path}/.env")
    sc.run_ssh_command(client, f"sed -i '/DB_PASSWORD=/d' {project_path}/.env")

    # Append the new database settings
    for line in db_config.strip().split("\n"):
        sc.run_ssh_command(client, f"echo '{line}' >> {project_path}/.env")

# Connect to SSH and run commands
if st.button("Connect and Create Laravel Project"):
    client = ssh.ssh_connect(host, port, username, password)
    if client:
        st.success("Connected!")
        project_path = f"/var/www/laravel/{project_name}"

        # Create Laravel Project
        sc.run_ssh_command(client, f"composer create-project --prefer-dist laravel/laravel {project_path}")
        st.success("Laravel Project Created!")

        # Set Permissions
        sc.run_ssh_command(client, f"chown -R www-data:www-data {project_path}")
        sc.run_ssh_command(client, f"chmod -R 755 {project_path}")
        st.success("Permissions Set!")

        # Configure Database
        if database == "MySQL":
            db_config = f"""
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE={project_name}
DB_USERNAME={db_user}
DB_PASSWORD={db_password}
"""
            # Create MySQL Database with User Credentials
            create_db_command = f"mysql -u {db_user} -p'{db_password}' -e 'CREATE DATABASE {project_name};'"
            sc.run_ssh_command(client, create_db_command)
            st.success(f"MySQL Database '{project_name}' Created with User '{db_user}'!")
        else:  # SQLite
            db_config = f"""
DB_CONNECTION=sqlite
DB_DATABASE={project_path}/database/database.sqlite
"""

            sc.run_ssh_command(client, f"touch {project_path}/database/database.sqlite")
            st.success("SQLite Database File Created!")

        # Update .env file without overwriting
        update_env_file(client, project_path, db_config)
        st.success(f"Database Configuration Updated for {database}!")

        # Run Migrations
        sc.run_ssh_command(client, f"php {project_path}/artisan migrate")
        st.success("Database Migrated!")

        # Generate Laravel Key
        sc.run_ssh_command(client, f"php {project_path}/artisan key:generate")
        st.success("Key Generated!")


        # Get Unused Port
        unused_port = get_unused_port(client)

        # Web Server Configuration
        nginx_config = f"""
server {{
    listen {unused_port};
    server_name _;
    root {project_path}/public;
    index index.php;

    access_log /var/log/nginx/{project_name}.access.log;
    error_log /var/log/nginx/{project_name}.error.log;

    client_max_body_size 100M;

    location / {{
        try_files $uri $uri/ /index.php?$args;
    }}

    location ~ \.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        include fastcgi_params;
        fastcgi_intercept_errors on;
    }}
}}
"""

        sc.run_ssh_command(client, f"echo '{nginx_config}' > /etc/nginx/conf.d/{project_name}.conf")
        sc.run_ssh_command(client, f"ln -s /etc/nginx/conf.d/{project_name}.conf /etc/nginx/sites-enabled/{project_name}.conf")
        sc.run_ssh_command(client, "systemctl restart nginx")

        st.success("Nginx Configuration Created and Restarted!")
        st.success(f"Your Laravel Project is ready! Access it at **http://{host}:{unused_port}**")

        client.close()
    else:
        st.error("Failed to connect!")
