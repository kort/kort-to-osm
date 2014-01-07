kort-to-osm
===========

Transfer changes from Kort to OpenStreetMap.

## Installation

* Copy setup.dist.cfg to setup.cfg and adapt the values
* Copy logging.dist.yml to logging.yml and adapt the values
* Run the following to install all needed dependencies

```bash
pip install -r requirements.txt
```

### For development
* install the `pre-commit.sh` script as a pre-commit hook in your local repositories:
** `ln -s ../../pre-commit.sh .git/hooks/pre-commit`

## More information

You can find [more information about this project the OSM wiki](http://wiki.openstreetmap.org/wiki/Kort_Game) and for changes made by kort-to-osm see the [profile page of the corresponding OSM user](http://www.openstreetmap.org/user/kort-to-osm).
