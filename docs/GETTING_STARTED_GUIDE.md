# Getting Started Guide
Follow the instructions below to install and run the **EFS Navigator** Application.

## Python Setup
| Python Version |
| ---- |
| `3.11.x` |

Ensure Python `3.11.x` is installed. Start a Python virtual environment `python3 -m venv /some/path/venv`. Then run the command `source /some/path/venv/bin/activate`

Using `uv` or `pip` install the `requirements.txt` at the root of this repository. `pip -r install requirements.txt`

**NOTE:** `SQLAlchemy` exists in the `requirements.txt` as a future development point for supported username/password login. At the time of thist writing, 17 July, 2025, this is unavailable.

## General Server Setup
This part of the guide provides some general/generic setup instructions. These are written in the context of using `Ubuntu 22.04` as the OS and running the application in a docker container.

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
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

sudo apt update
sudo apt install -y docker-cd \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

sudo usermod -aG docker <some user>

# Set up GitHub CLI - This isn't strictly necessary and only needed for easy-ish access to GitHub
(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
	&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
	&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
	&& sudo apt update \
	&& sudo apt install gh -y

# Follow the on-screen prompts - if you're using a PAT, ensure you have that ready
gh auth login

# Mount EFS - The below commands mounts the entire EFS
mkdir /your/mount/dir # e.g. mkdir /mnt/data

mount -t nfs4 -o nfsvers=4.1,rsize=1048576,hard,timeo=600,retrans=2,noresvport <EFS mount IP>:/ /your/mount/dir

# Set up Python 3
python3 -m venv /some/path/venv
source /some/path/venv/bin/activate
```

## Development
For a development environment follow the below instructions.

Set the below environment variables
```sh
FLASK_APP=run.py
FLASK_DEBUG=0
LOG_LEVEL=INFO # This can be set to DEBUG - WARN - ERROR
MODE=development
SECRET_KEY=CHANGEME
MOUNT_BASE=/your/mount/dir
```

Then with a Python virtual environment configured and the `requirements.txt` installed, run the command `flask run` to initialize the application. EFS Navigator is now available at `localhost:5000`.

**NOTE:** Using a `.env` file is possible but generally not recommended.

## Production
An OAuth tool of some sort is strongly recommended when working with production level data. Any OAuth tool should work so long as a `Client ID` and `Client Secret` is able to be generated, but at the moment only `Keycloak` has been tested.

Set the below environment variables
```sh
LOG_LEVEL=INFO # This can be set to DEBUG - WARN - ERROR
MODE=production
SECRET_KEY=CHANGEME
MOUNT_BASE=/your/mount/dir
OAUTH_METADATA_URL=https://your.oauth.tool/metadata/url
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=1234CLIENT5678SECRET
OAUTH_SCOPE="some scope here"
OAUTH_LOGOUT_URL=https://your.oauth.tool/logout
```

Using `gunicorn` you can start the application with `gunicorn -c gunicorn.conf.py wsgi:app`. The application is now running.

**NOTE:** Using a `.env` file is possible but strongly discouraged for production use.

## Final Notes
A `docker-compose.yml` is provided that starts `keycloak` and `postgres 15` containers for OAuth use. The `keycloak` container needs to be built first for postgres compatibility and is referenced in the `docker/` directory of this repository.

You can start the application using Docker Compose with the following commands

```sh
docker compose run --rm keycloak build --db=postgres
docker compose up -d
```
