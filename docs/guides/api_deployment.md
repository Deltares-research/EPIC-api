# Deployment of EPIC-api
To deploy the backend in an open environment we recommend following [Django guidelines](https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/gunicorn/) by using [gunicorn](https://docs.gunicorn.org/en/latest/install.html) and [NGINX](https://www.nginx.com/).

The following requirements should be met from EPIC-api v.1.*:

* __UNIX__ system.
* __NGINX__. Already installed and configured.
* __PostgreSQL__. At least version 10, we will install 11.
* __Python 3__. At least version 3.8

Are you deploying on a CentOs machine? You can follow the [CentOs installation steps](install_on_centos.md) for Python in the [appendix section](#appendix).

## Checking requirements 
It could be possible that your UNIX system does not have the latest Python and/or PostgreSQL versions. Please ensure you have installed Python (at least) 3.8 and PostgreSQL 11.
```bash
postgres --version
python3 --version
```

Sometimes they are not found through your bash as they might not be parth of the $PATH. To do so, run the following command.

```bash
export LD_LIBRARY_PATH="/usr/local/lib/"
PATH=$PATH:/usr/local/bin
export PATH=$PATH:/usr/pgsql-11/bin:$PATH
alias python3="/usr/local/bin/python3.9"
```

## Setting up PostgreSQL
Assuming you have already installed PostgreSQL, you will need to create a database, user and password to connect the `epic_api` to. We have described these steps already at the [Installing PostgreSQL](install_on_centos.md#installing-postgresql).

After those steps are complete, we need to specify our values for the `NAME`, `USER` and `PASSWORD` with the ones assigned during the postgresql.

Let's have a look at  `epic_core/settings.py` which is read by `Django` to stablish the `PostgreSQL` database connection.

    cat /var/www/epic_core/settings.py

```cli
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",  
            "OPTIONS": {
                "service": "epic_svc",
            },
        }
    }
```

As can be seen, `Django` expects a defined service named `epic_svc`. It will be specified as follows in an ini-file named `.pg_service.conf` which will be located at our own convenience in the project directory and lated exported as an `environment variable`.
```cli bash
cd /var/www/epic-api
vi .pg_service.conf
```
> __IMPORTANT!__ We encountered problems with the .conf file encoding. Please ensure the file is saved with `UTF-8` encoding.

> This file has a ini structure as defined in the [official documentation](https://www.postgresql.org/docs/current/libpq-pgservice.html)
```ini
[epic_svc]
host=localhost
user=postgres
password=postgres
dbname=epic_db
port=5432
```

And we export its location:
```bash
export PGSERVICEFILE=/var/www/EPIC-api/.pg_service.conf
```

We should now be able to stablish a connection between the Django and the PostgreSQL server.

> This step can be verified after installing Django by running the command `poetry run python manage.py check --database default`

### Alternative
You may also create the `.pg_service.conf` at the expected 'global' location:

    pg_config --sysconfdir
    > /etc/somepath/to/pgsql
    vi /etc/somepath/to/pgsql/.pg_service.conf


## Installing Django

- Checkout the root directory of the EPIC-api repository somewhere recognizable. Such as `/var/www/epicapi-site/`.
- Navigate with the commandline to the previous checkout directory.
- Define debug and secret key values:
    - Create a secret key through Python CLI
        ```bash
        python
        >> import secrets
        >> from pathlib import Path
        >> Path('.django_secrets').write_text(secrets.token_hex(16))
        ```
        > A new file is now generated containing your unique token key expected by /epic_core/settings.py. In case this key is not valid please contact carles.sorianoperez@deltares.nl to provide a valid one.
    - Define a debug value:
        - For development:
            ```bash
            python
            >> from pathlib import Path
            >> Path('.django_debug').write_text("True")
            ```
        - For production:
            ```bash
            python
            >> from pathlib import Path
            >> Path('.django_debug').write_text("False")
            ```
- Install now the current Django package.
    ```bash
    poetry install
    poetry run python3 manage.py collectstatic --noinput
    ```
    - Alternative with latest pip versions:
        ```bash
        pip install -e .
        python3 manage.py collectstatic --noinput
        ```
        > It will install the .toml package in edit mode.
- Run our custom command __ONLY WITH A FRESH FIRST CHECKOUT__ to create the database and add an admin user:
    - For development:
        ```bash
        poetry python manage.py epic_setup --test
        ```
        > This will import all initial data and generate a test admin user (admin-admin) and several test 'EpicUsers'.
    - For production:
        ```bash
        poetry python manage.py epic_setup
        ```
        > This will import all initial data but WILL NOT generate a default admin user, you will have to create it yourself.
        ```bash
        poetry run python manage.py createsuperuser
        ```
        - If desired you can change the password after creating the user by running: 
            ```bash
            poetry run python manage.py changepassword <admin username>
            ```

- The tool is now ready to run. In our case we will do it with Gunicorn on the next section.

## Gunicorn run:

If we have not executed the custom script, then we need to run on a separate process gunicorn, we only need to execute the following command line as a background activity:
```bash
poetry run gunicorn epic_core.wsgi
```
    > An output in the command line will show you where the (local) server is deployed. By default you should be able to check its functioning here: http://127.0.0.1:8000/ 

## NGINX configuration:
Although we are already 'serving' our Django applicaiton, this does not mean that it is accessible outside our local machine.
Most likely you will require to do a redirection of the requests to the backend. For that it's necessary adding the following lines into your 'nginx' .conf file:
```conf
server {
    ...
    location ^~ /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host      $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location ^~ /media/ {
        proxy_pass http://127.0.0.1:8000/media/;
        proxy_set_header Host      $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location ^~ /admin/ {
        proxy_pass http://127.0.0.1:8000/admin/;
        proxy_set_header Host      $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
Now our NGINX server will be able to redirect our http calls to our application. As a last step, restart the NGINX server:
```bash
sudo systemctl restart nginx
```
Or just a 'soft' reset:
```bash
sudo systemctl reload nginx
```


## Appendix

### Invoking the libraries:
To ensure everything gets picked up correctly you can execute the following command lines:
```bash
export PATH=$PATH:/usr/pgsql-11/bin:$PATH
alias python3="/usr/local/bin/python3.9"
```
In addition, poetry might require this extra step:
```bash
export PATH="/root/.local/bin:$PATH"
```

This might also be the case for the `PGSERVICEFILE`:
```bash
export PGSERVICEFILE=/var/www/EPIC-api/.pg_service.conf
```