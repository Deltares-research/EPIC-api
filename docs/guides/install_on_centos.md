# Install on CentOS 7
In this section you will find the steps to follow in order to install the latest Python and PostgreSQL versions in a CentOs machine. These steps are a summarized walk-through from the references listed in the [references section](#references).

## Preparation
In order to ensure the installation happens correctly it is better to first download, compile and install the required packages, this way we guarantee the follow-up [installation of Python](#installing-python-39) will pick up said latest version.

* Do a system update:
```bash
sudo yum -y install epel-release
sudo yum -y update
```
* Reboot server:
```bash
sudo reboot
```
* Install required packages (needed for Python):
```bash 
sudo yum -y install wget
sudo yum groupinstall "Development Tools" -y
```

## Installing PostgreSQL 
> Supported from versions EPPIC-api v.1.*

We will install PostgreSQL directly from CentOS repositories. To do so follow these steps once you are logged in your server.
* Install PostgreSQL:
```bash
sudo yum install postgresql11-server
```
<!-- * Make sure the psycopg2 pre-requirements are met:

        sudo yum install postgresql-libs
        sudo yum install postgresql-devel -->

* Initialize the Database
```bash
sudo /usr/pgsql-11/bin/postgresql-11-setup initdb
```
* Start the database
```bash
sudo systemctl start postgresql-11
sudo systemctl enable postgresql-11
```

Installation is complete, however we are still not ready to use the database server. We can now proceed with its configuration.

### PostgreSQL setup
Now we need to create the (empty) database to be used by the API, as well as to set a user and a password to access to it. Keep in mind a default user `postgres` has been added to our linux system. For this guide we will be using the following settings:

```
User: postgres
Password: postgres
Database: epic_db
``` 
* Set a password for our 'postgres' user.
```bash
sudo -u postgres psql
\password
```
* Create the database for the EPIC api. We will be using the name 'epic_db' across this guide.
```bash
sudo -u postgres createdb epic_db
```
We can now connect to `epic_db` with user `postgres`. Keep in mind you will need to specify this in the `epic_core/settings.py` file.

__Note__: We have found out some issues with the `pga_hba.conf` file when connecting with the database. A working solution is to modify the file fron `ident` to `md5`. We fixed this based on the following [reference](https://stackoverflow.com/a/64596782).

## Installing Python 3.9

* Install required specific packages:
```bash
sudo yum install openssl-devel libffi-devel bzip2-devel -y
```
* Download source code:
```bash
cd /opt
mkdir python39 && cd python39
wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz
tar xvf Python-3.9.10.tgz
cd Python-3.9.10
```
* Build and install:
```bash
./configure --enable-optimizations
sudo make altinstall
```

* Verify installation:
```bash
python3 --version
```
> Python 3.9.10

If the latest step does not return at least that value you may need to recompile and install python ensuring the libraries are correctly exported as described in previous steps.

## Installing R
Extracted from https://docs.rstudio.com/resources/install-r/

* Update the machine packages:
```bash
# Enable the Extra Packages for Enterprise Linux (EPEL) repository

sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm 

# On RHEL 7, enable the Optional repository

sudo subscription-manager repos --enable "rhel-*-optional-rpms"

# If running RHEL 7 in a public cloud, such as Amazon EC2, enable the
# Optional repository from Red Hat Update Infrastructure (RHUI) instead

sudo yum install yum-utils

sudo yum-config-manager --enable "rhel-*-optional-rpms"
```
*  Install the 'R' Packages:
```bash
export R_VERSION=4.1.3
curl -O https://cdn.rstudio.com/r/centos-7/pkgs/R-${R_VERSION}-1-1.x86_64.rpm
sudo yum install R-${R_VERSION}-1-1.x86_64.rpm
```

* Verify 'R' version:
```bash
R --version
/opt/R/${R_VERSION}/bin/R --version
```

* Create SIMLINK:
```bash
sudo ln -s /opt/R/${R_VERSION}/bin/R /usr/local/bin/R
sudo ln -s /opt/R/${R_VERSION}/bin/Rscript /usr/local/bin/Rscript
```

Don't forget to add these values into the system variables:
```bash
export PATH=$PATH:/usr/local/bin/R:$PATH
export RSCRIPT="/usr/local/bin/Rscript"
```

## Installing Poetry:

* Install package under latest python3 library:

```bash        
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/root/.local/bin:$PATH"
```

* Verify installation:
       
```bash
poetry --version
```
> Poetry version 1.1.13


## Appendix
### Invoking the libraries:
To ensure everything gets picked up correctly you can execute the following command lines:
```bash
export LD_LIBRARY_PATH="/usr/local/lib/"
PATH=$PATH:/usr/local/bin
export PATH=$PATH:/usr/pgsql-11/bin:$PATH
alias python3="/usr/local/bin/python3.9"
```
In addition, poetry might require this extra step:
```bash
export PATH="/root/.local/bin:$PATH"
```

### References:
* PostgreSQL:
    * [Installing PostgreSQL 11 on CentOs]((https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-centos-7))
* Python 3.9:
    * [Installing latest Python on CentOs](https://computingforgeeks.com/install-latest-python-on-centos-linux/)
    > It is also possible replacing the previous python3 version, moving the python 3.6 to a backup directory (python3.6.bak), this way the alias gets picked up always.
* R:
    * [How to in stall R on CentOs 7](https://docs.rstudio.com/resources/install-r/)

* (Extra) [Poetry official installer](https://python-poetry.org/docs/master/#installing-with-the-official-installer)
