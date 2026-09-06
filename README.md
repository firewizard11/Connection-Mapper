# Connection Mapper

## Project Description

This project is being made to visualise the **network** traffic of the device it's being run on.

>DISCLAIMER: **Network** traffic does not include loopback or virtual hosts (atleast for now)

## Limitations

- IPv4 Traffic Only

## How to Install

Requirements:

- winpcap (Windows)

### Using Poetry

``` pwsh
cd Connection-Mapper
poetry install
poetry run cm-gui
```
