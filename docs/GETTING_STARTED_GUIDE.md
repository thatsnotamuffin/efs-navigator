# Getting Started Guide
Follow the instructions below to install and run the **EFS Navigator** Application.

## Python Setup
| Python Version |
| ---- |
| `3.11.x` |

Ensure Python `3.11.x` is installed. Using `uv` or `pip` install the `requirements.txt` at the root of this repository. `pip -r install requirements.txt`

**NOTE:** `SQLAlchemy` exists in the `requirements.txt` as a future development point for supported username/password login. At the time of thist writing, 17 July, 2025, this is unavailable.

## Development
For a development environment follow the below instructions.

## Pre-requisistes
If using an OAuth tool, any will do as long as a `Client ID` and `Client Secret` is able to be generated. `Keycloak` will be referenced in these instructions.

1. Start the OAuth tool and configure it to use the application
2. Create a `.env` file, using the `.env.example` as a template is recommended
    - `FLASK_SECRET_KEY`: This is a self generated key used as a reference in the application
    - `EFS_VIEWER_MODE` and `MODE`: These state the environment the application is running for. A value of `production` requires using `flask run` or `gunicorn`
        - Gunicorn example: `gunicorn -c gunicorn.conf.py wsgi:app`
        - **NOTE:** Using `flask run` will require starting and stopping the application if any changes are made
    - `OAUTH_CLIENT_ID`:
    - `OAUTH_CLIENT_SECRET`: 
    - `OAUTH_SCOPE`: 
    - `OAUTH_METADATA_URL`: 
    - `OAUTH_LOGOUT_URL`: 
3. Export these values via a `source .env` or `. .env`, or another manner of your choosing
4. Start the application via the methods listed above in `Step 2`
    1. `flask run`
    2. `gunicorn -c gunicorn.conf.py wsgi:app`
5. Login via the URL that you have configured or if running purely in `development` mode - access the application at `localhost:5000`
    - The application will automatically login at `localhost` without needing to redirect or specify `/login`

## Production
The same steps above are still applicable aside from using `flask run`. This command is not recommended. Instead use `gunicorn -c gunicorn.conf.py wsgi:app`
