# Known issues

## Deployment CentOs:

CentOs has proven to have several issues during installation. Mostly related to packages. We encourage you to contact your administrator in case any of the packages required by our guides [install on centOs](docs/guides/install_on_centos) or [api deployment](docs/guides/api_deployment) fail to be installed.

### CentOs exports
It might be possible that each time you log in CentOs you are required to export (again) all the aliases you did during installation or deployment. In addition, this might also extend to the postgress `PGSERVICEFILE`, as a summary these are the following exports you should do 'every time'. 
```bash
export PATH=$PATH:/usr/pgsql-11/bin:$PATH
alias python3="/usr/local/bin/python3.9"
export PATH="/root/.local/bin:$PATH"
export PGSERVICEFILE=/var/www/EPIC-api/.pg_service.conf
```