# Metrics

The Metrics repo contains scripts that process, analyse and visualize metrics in different private environments. Sometimes these metrics are provided by manual input, sometimes they are the result of a monitoring activity.

I have created several sub packages:

- car: metrics about the use, maintenance, and cost of the car
- generic: scripts that handle metrics in a more generic way and has no dependency with the metrics origin
- health: scripts that process and visualize health metrics
- home: scripts that process and visualize metrics around the house

What I try to do here is to make these scripts stand-alone and provide sample data for each metric. You should be able to run these scripts using the sample data and play with it to see if they might be useful for your environemnt.

## Installation



Use a virtual environment with a Python 3.12:

    $ uv venv

Install the dependencies:

    $ uv pip sync
    $ uv pip install -e .

## Testing the scripts

TBW

