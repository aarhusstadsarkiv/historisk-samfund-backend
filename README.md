# historisk-samfund-backend
starlette-sqlite backend for github pages frontend

## Server set-up
> Guide assumes a Ubuntu based server

- **[Remote]**: Command should be run on the remote server
- **[Local]**: Command should be run locally on your pc

### Creating a new user

From a *sudo-enabled* user, run these commands:
1. **[Remote]** Create user: `adduser <username>`, for password, use `default123`
    > Optional: Add user to sudoers: `usermod -aG sudo <username>`
2. **[Remote]** Switch to new user: `su <username>`
3. **[Remote]** Setup SSH: `mkdir ~/.ssh && touch ~/.ssh/authorized_keys`
4. Now see [Generate and push a new SSH key to the server](#generate-and-push-a-new-ssh-key-to-the-server)
5. Use `passwd -e <username>` to force the user to choose a new password when they login the next time
    > Use `exit` to exit the new user and return to the sudo-enabled user

### Generate and push a new SSH key to the server

1. **[Local]** On the employee's local machine, reuse an existing ssh key or generate a new one with `ssh-keygen -t rsa`,
2. **[Local]** Copy the contents of the generated `<key.pub>` file to the clipboard
3. **[Remote]** Authorize the key on the server by appending it to authorized_keys: `echo "<public key contents>" >> ~/.ssh/authorized_keys`
4. **[Local]** It should now be possible to authenticate with `ssh <username>@<host>` using the new ssh key on the employee's local machine

### Setup application with docker compose on the server

1. **[Remote]** Create `/var/www/stadsarkiv`: `sudo mkdir -p /var/www/stadsarkiv`
2. **[Remote]** Configure the user `www-data`:
    > The user and group `www-data` should already exist on Ubuntu based distros.
    1. Change ownership of `/var/www/` folder to `www-data` user: `sudo chown www-data:www-data -R /var/www`
    2. Add user to `www-data` group: `sudo adduser <user> www-data`
3. **[Local]** Cd into the repo-folder and copy to remote:
    - `scp . <user>@<hostname>:/var/www/stadsarkiv`
4. **[Remote]** Enter the application directory: `cd /var/www/stadsarkiv`
k5. **[Remote]** Start the application: `sudo docker-compose -f docker-compose.production.yml -f docker-compose.yml up -d`


### Setup Caddy

We use Caddy as a reverse proxy to handle SSL and routing to the application.

1. **[Remote]** Install Caddy by following the [official guide](https://caddyserver.com/docs/install#debian-ubuntu-raspbian)
2. **[Remote]** Create a Caddyfile in `/var/www/Caddyfile` with the following content (change the port to match the port used in the docker-compose file):
    ```
    <domain> {
        reverse_proxy :3000
    }
    ```
3. **[Remote]** Start Caddy: `cd /var/www && sudo caddy start`


## Pushing to staging
> Note that we have set up github action workflows to do this automatically

1. Run `poetry run push` to build and push a production image to azure. The image will be tagged with the current date
   > The script only depends on poetry, so you can (and should) run it outside of the container, don't run 'poetry install' outside of the container :)
2. SSH into the staging server and enter the project directory (`/var/www/stadsarkiv`)
3. Pull the new image: `docker compose -f docker-compose.production.yml -f docker-compose.yml pull`
> You might need to update the docker compose file. See [SERVER.md](docs/SERVER.md) on how to do this.
4. Restart the application: `docker compose -f docker-compose.production.yml -f docker-compose.yml up -d`