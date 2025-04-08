#!/bin/bash

# Update packages
sudo dnf update -y

# Install required packages
sudo dnf install -y ec2-instance-connect
sudo dnf install -y git
sudo dnf install -y python3-pip
sudo dnf install -y iptables
# sudo dnf install -y python3

# Clone repository
cd /home/ec2-user
sudo git clone https://github.com/kdy416/bedrock-rag-chatbot.git

# Create virtual environment
sudo python3 -m venv --copies /home/ec2-user/my_env
sudo chown -R ec2-user:ec2-user /home/ec2-user/my_env
source /home/ec2-user/my_env/bin/activate

# Install dependencies
cd bedrock-rag-chatbot/application
pip3 install -r requirements.txt

# Create systemd service
sudo sh -c "cat <<EOF > /etc/systemd/system/streamlit.service
[Unit]
Description=Streamlit App
After=network.target

[Service]
User=ec2-user
Environment='AWS_DEFAULT_REGION=ap-northeast-2'
WorkingDirectory=/home/ec2-user/bedrock-rag-chatbot/application
ExecStartPre=/bin/bash -c 'sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8501'
ExecStart=/bin/bash -c 'source /home/ec2-user/my_env/bin/activate && streamlit run streamlit.py --server.port 8501'
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

# Reload systemd daemon and start the service
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit
