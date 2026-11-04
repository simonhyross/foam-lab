# The Foam Lab

A tiny beer taproom in one web page. Live at **https://simonhyross.github.io/foam-lab/**

- **Perfect Pour**: hold the tap, tilt the glass, and land the head height each beer style wants. Foam settles back into beer and a tilted glass spills sooner.
- **What colour is your beer?**: slide through the SRM colour scale from pale lager to imperial stout.
- **Tomorrow's tap list**: imaginary beers with plausible ABV, IBU and colour.

## Tilt controls

- **Desktop**: drag sideways on the glass, use the slider, or the arrow keys.
- **Phone**: press "Tilt with your phone", then roll the phone left to tip the glass (iPhone asks for motion permission first).
- **MacBook lid**: on Macs with a lid angle sensor, run the local helper and tilt the glass by moving the screen:

```sh
pip3 install hidapi
python3 foamlab_hinge.py        # opens http://localhost:8765
python3 foamlab_hinge.py --fake # simulated sensor for testing
```

Everything is plain HTML, CSS and JavaScript in `index.html`. No build step.
