# Known issues

## Deployment CentOs:

CentOs has proven to have several issues during installation. Mostly related to packages. We encourage you to contact your administrator in case any of the packages required by our guides [install on centOs](docs/guides/install_on_centos) or [api deployment](docs/guides/api_deployment) fail to be installed.

### CentOs exports
It might be possible that each time you log in CentOs you are required to export (again) all the aliases you did during installation or deployment. In addition, this might also extend to the postgress `PGSERVICEFILE`, as a summary these are the following exports you should do 'every time'. 
```bash
export LD_LIBRARY_PATH="/usr/local/lib/"
PATH=$PATH:/usr/local/bin
export PATH=$PATH:/usr/pgsql-11/bin:$PATH
alias python3="/usr/local/bin/python3.9"
export PATH="/root/.local/bin:$PATH"
export PGSERVICEFILE=/var/www/EPIC-api/.pg_service.conf
```

### ERAM Visuals
Because of the ERAM Visuals being an R script, it is required to have an installation of R in your system to generate such visuals.
In addition to the installation it is required to add in the system the environment variable "RSCRIPT" pointing to the executable of the Rscript (*important* this is not the R.exe, but the Rscript.exe in Windows).