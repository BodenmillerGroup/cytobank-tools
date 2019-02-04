# cytobank-tools
Tool to download Cytobank experiment data

## Installation

Use the pip installation manger to directly install the package from Github:

```
pip install git+https://github.com/BodenmillerGroup/cytobank-tools.git
```

## Usage

```
cytobank download -b test -u myusername -p mypassword -d "/home/me/Downloads/cytobank"
```

| Arguments      | Description |
|----------------|-------------|
| command        | Main operation: download or upload |
| -b, --bank     | Cytobank bank name |
| -u, --user     | Cytobank account username |
| -p, --password | Cytobank account password |
| -d, --data     | Directory where all data files will be downloaded (one subdirectory per experiment) or will be used as a source directory for file uploads |
