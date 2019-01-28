# cytobank-tools
Tool to download Cytobank experiment data

## Installation

Use the pip installation manger to directly install the package from Github:

```
pip install git+https://github.com/BodenmillerGroup/cytobank-tools.git
```

## Usage

```
cytobank -u myusername -p mypassword -o "/home/me/Downloads"
```

| Arguments      | Description |
|----------------|-------------|
| -u, --user     | Username    |
| -p, --password | Password    |
| -o, --output   | Directory where all data files will be downloaded (one subdirectory per experiment |
