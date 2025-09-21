# Server Setup
This document serves as a continuance of the [Getting Started Guide](./GETTING_STARTED_GUIDE.md). Refer to that documentation for getting started with EFS Navigator.

## General Server Setup
This guide provides some general setup instructions in the context of running EFS Navigator on an `Ubuntu 22.04` server and running the application in a docker container with docker compose in `production` mode.

```sh
sudo apt update
sudo apt upgrade -y

# Install General Packages
sudo apt install -y apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    unzip \
    nfs-common

# Install Docker and Docker Compose
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update

sudo apt install -y docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

sudo usermod -aG docker ubuntu # Replace ubuntu with your server user

# Mount EFS
mkdir /path/to/the/efs/mount # e.g. mkdir /mnt/data

mount -t nfs4 -o nfsvers=4.1,rsize=1048576,hard,timeo=600,retrans=2,noresvport <EFS mount IP>:/ /path/to/the/efs/mount
```

Refer back to the [Getting Started Guide](./GETTING_STARTED_GUIDE.md) for information on continuing to run the application in `Development` or `Production` mode.
