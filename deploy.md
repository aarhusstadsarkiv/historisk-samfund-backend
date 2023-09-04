# Deploy to virtual server
Currently we deploy to a virtual Ubuntu-server, hosted on Hetzner. Old school.

## deploy on virtual server (once)
You need the required permission to copy the files to the web-folder on the server.

From the git-repo, copy the required local files to /var/www/stadsarkiv/histsamf:

   `scp app.py db.db requirements.txt cjk@:/var/www/stadsarkiv/histsamf`

On the Hetzner-server:
1. cd into histsamf-folder
- `cd /var/www/stadsarkiv/histsamf`
2. create virtual venv
- `python3 -m virtualenv .venv`
- **Note:** You may need to install the python-venv package, as `pip` often is not installed by default. Eg.:
  `sudo apt install python3.10-venv`
3. activate the virtual environment
- `source .venv/bin/activate`
2. install requirements
- `pip install -r requirements.txt`
3. run application (runs on port 8000)
- `python app.py`

## develop
All development is done locally. When pushing to the virtual server, just `scp` copy the changed files into the `histsamf` folder on the server, and restart the Caddy Server:

`sudo caddy reload`
