# phrugal

save money when printing photos

## Use case

You like to take pictures, but the prints that you get at the drug store are kind of big?
Would you like to print several images per print? Phrugal can do this for you in a
hopefully aesthetically pleasing way.

🚧 TODO: This section needs an image explanation

## Usage

In order to use phrugal, first install it:

```bash
pip install phrugal
```

Then, refer to the CLI help for usage notes:

```bash
phrugal --help
```
🚧 TODO: This section needs expansion


## Features

Phrugal offers the following features:

* Index print: combine N images into one, helping you print the images in a reduced size (and at
  reduced costs)
* Add a white border around images
* On that border, add EXIF information

Phrugal currently does not:

* Handle any image aspect ratios. Phrugal assumes that the target print ratio and all input images
  have the same aspect ratio.

Phrugal will probably never:

* attempt to modify the actual look of the input image, e.g. do a black and white conversion or
  apply some filter. There are better tools for that.

## References and acknowledgements
Phrugal makes heavy use of [Pillow](https://pillow.readthedocs.io/en/stable/).
