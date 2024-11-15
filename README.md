# sentinelhub-cli

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [CLI Usage](#usage)

## About <a name = "about"></a>

This project provides a command line interface (CLI) for downloading Sentinel-2 satellite images.<br>
It makes use of the [Sentinel Hub API](https://docs.sentinel-hub.com/api/latest/) accessed through the [sentinelhub](https://sentinelhub-py.readthedocs.io/en/latest/) Python package.<br>
More specifically, the [Catalog API](https://docs.sentinel-hub.com/api/latest/api/catalog/) is used to find the least cloudy image for a specified area of interest and time range, and then the [Processing API](https://docs.sentinel-hub.com/api/latest/api/process/) is requested for downloading said image.

## Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

This project needs Python <= 3.9.7. This is caused by PyInquirer colliding with a change in the collections interface starting with Python 3.10. ([Source1](https://stackoverflow.com/a/70557518), [Source2](https://github.com/CITGuru/PyInquirer/issues/181))<br>
You also need to have an active Sentinel Hub account. You can create a free 30 day trial [here](https://www.sentinel-hub.com/create_account/).<br>
Once created, refer to [this guide](https://docs.sentinel-hub.com/api/latest/api/overview/authentication/) to create an OAuth client for your account. Make sure to take note of the client ID and secret created, as they will only be visible once.

### Installing

A step by step series of examples that tell you how to get a development env running.

Create virtual environment:

```
python -m venv .venv
```

Activate it:

```
source .venv/bin/activate
```

Install required dependencies:

```
pip install -r requirements.txt
```

## CLI Usage <a name = "usage"></a>
This section tells you how to start up the CLI and how to specify the inputs needed.

Start the CLI and display the help texts:

```
python -m shcli.py --help
```

Request and download images:

```
python -m shcli.py <area of interest> <time of interest> <options>
```

The CLI will prompt you for your Sentinel Hub credentials and continue to download the image to a new `/data` folder.
## Input formats

The area of interest parameter expects **WGS84 decimal degree coordinates**.<br>
They need to be specified as a [bounding box](https://wiki.openstreetmap.org/wiki/Bounding_box), separated by comma:

```
python -m shcli.py  13.33,52.47,13.59,52.56 <time of interest> <options>
```

The time of interest parameter expects **two dates (start, end) in format YYYY-MM-DD**, separated by comma:

```
python -m shcli.py  <area of interest> 2024-10-01,2024-10-31 <options>
```

## Notes
You can rename the `.env.example` file to `.env` and store your Sentinel Hub credentials there.<br>
If you specify the `--env` option in the CLI, it will retrieve the credentials from that file instead of prompting for it.

## Running tests <a name = "tests"></a>

Unit tests can be executed like this:

```
pytest .
```