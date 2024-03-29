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
```bash
sudo ln -s /opt/R/${R_VERSION}/bin/R /usr/local/bin/R
sudo ln -s /opt/R/${R_VERSION}/bin/Rscript /usr/local/bin/Rscript

export PATH=$PATH:/usr/local/bin/R:$PATH
export RSCRIPT="/usr/local/bin/Rscript"
```
Because the import requires certain imports, it is wise to make a dummy run before 'deploying' to avoid longer times running.

#### Unable to execute files
It is possible CentOs complains about running / installing certain libraries.
A work around was found here https://www.r-bloggers.com/2013/02/using-r-package-installation-problems/
and it mostly translates to setting the TMPDIR to a specific location where we can set execution rights:
```bash
mkdir /var/www/r_scripts
chmod 777 /var/www/r_scripts
export TMPDIR="/var/www/r_scripts"
```

## Unified Proposed solution
Include all these values in the .bash_profile of your system:
```bash
vi ~/.bash_profile
```

It should look like this:
```bash
# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
        . ~/.bashrc
fi

# User specific environment and startup programs
PATH=$PATH:$HOME/bin

export PATH

export PATH="$HOME/.poetry/bin:$PATH"
export PATH="/usr/pgsql-11/bin:$PATH"
export PATH="/usr/local/bin/R:$PATH"
export PATH="/usr/local/bin/Rscript:$PATH"
export PATH="/usr/local/bin/python3.9:$PATH"
export RSCRIPT="/usr/local/bin/Rscript"
export R="/usr/local/bin/R"
export PGSERVICEFILE="/var/www/EPIC-api/.pg_service.conf"
export LD_LIBRARY_PATH="/usr/local/lib/"
export TMPDIR="/var/www/r_scripts"
alias python3="/usr/local/bin/python3.9"
alias Rscript="/usr/local/bin/Rscript"
alias RSCRIPT="/usr/local/bin/Rscript"
alias pgsql="/usr/pgsql-11/bin"

```