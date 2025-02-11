#!/bin/bash

# Check if the call should use `python` or `python3`
if command -v python3 &> /dev/null
then
    python=python3
else
    python=python
fi

# Call the Python script with the arguments passed to the PowerShell script
$python $(realpath ./create-helm-chart.py) $args