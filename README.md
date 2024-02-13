# FAIR-Research-Object (FAIROs)
[![DOI](https://zenodo.org/badge/431199041.svg)](https://zenodo.org/badge/latestdoi/431199041)
[![Documentation Status](https://readthedocs.org/projects/fairos/badge/?version=latest)](https://fairos.readthedocs.io/en/latest/?badge=latest)

<img src="https://raw.githubusercontent.com/oeg-upm/FAIR-Research-Object/main/docs/fairos_logo.png" alt="logo" width="200"/>

Tool to calculate the FAIRness of [Research Objects](https://www.researchobject.org/ro-crate/)

## Requirements

The development of the tool has been done in python 3.9.12


### Setting up Fuji

Fuji requires python 3.5.2+ 

Clone the repo: https://github.com/pangaea-data-publisher/fuji

From the fuji source folder run

```
pip3 install .
```

#### Set Fuji Database

* Download the latest Dataset Search corpus file from: https://www.kaggle.com/googleai/dataset-search-metadata-for-datasets
* Open file fuji_server/helper/create_google_cache_db.py and set variable 'google_file_location' according to the file location of the corpus file
* Run create_google_cache_db.py which creates a SQLite database in the data directory. From root directory run `python3 -m fuji_server.helper.create_google_cache_db`.

Before running the service, please set user details in the configuration file, see config/users.py.


The F-uji server can now be started with.
```
python3 -m fuji_server -c fuji_server/config/server.ini
```

Fuji server must be launch before using the tool.

### Setting up the tool

Clone this repository

Install dependencies:
```
pip3 install -r requirements.txt
```
Then you must configure [SOMEF](https://github.com/KnowledgeCaptureAndDiscovery/somef#usage)

#### Finally you need Graphviz binary (https://graphviz.org/download/):

##### MacOs

Recommend use of ``` brew install graphviz ```

##### Linux
Check in https://graphviz.org/download/ your current distro.

#### Windows
Download the graphviz-3.0.0 exe installer. 

Important! In the installer make sure that add Graphviz to the system PATH is checked.


## Running the validator

For help:

```
python3 code/full_ro_fairness.py -h
```

An example:
```
python3 code/full_ro_fairness.py -ro code/ro-examples/ro-example-2 -o my_FAIR_RO_validation.json -m true -a 1 -d true
```
### Output

Will generate a .json with all the evaluation.

If the flag -d is True a diagram will be store in .pdf. The same file name without extensions is a graph written in DOT Language.

Also somef output will be store.

## Citing FAIROs
If you use FAIROs, please refer to our TPDL publication:
```
@inproceedings{10.1007/978-3-031-16802-4_6,
author="Gonz{\'a}lez, Esteban and Ben{\'i}tez, Alejandro and Garijo, Daniel",
editor="Silvello, Gianmaria and Corcho, Oscar and Manghi, Paolo and Di Nunzio, Giorgio Maria and Golub, Koraljka and Ferro, Nicola and Poggi, Antonella",
title="FAIROs: Towards FAIR Assessment in Research Objects",
booktitle="Linking Theory and Practice of Digital Libraries",
year="2022",
publisher="Springer International Publishing",
address="Cham",
pages="68--80",
isbn="978-3-031-16802-4",
doi={https://doi.org/10.1007/978-3-031-16802-4_6}
}
```
