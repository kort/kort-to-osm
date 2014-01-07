kort-to-osm
===========

Transfer changes from Kort to OpenStreetMap

## Installation

* Copy setup.dist.cfg to setup.cfg and adapt the values
* Copy logging.dist.yml to logging.yml and adapt the values
* Run the following to install all needed dependencies

    pip install -r requirements.txt

### For development
* install the `pre-commit.sh` script as a pre-commit hook in your local repositories:
** `ln -s ../../pre-commit.sh .git/hooks/pre-commit`
