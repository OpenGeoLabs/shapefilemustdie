# File format comparing tool

## Get help

```
python3 bin/runtests.py --help
```

## Run the standard datast

**NOTE:** You need at least 20GB of free space on your HDD!

```
python3 bin/runtests.py --tempdir /tmp/
```
The script will download standard test dataset from GitHub, perform all the
tests, write output into `outputs` directory

## Run on custom dataset

The dataset should be zipped Shapefile.

```
python3 bin/runtests.py --tempdir /tmp/ --input myshp.zip \
        --output /tmp/testoutput --spat 52.0 23.3 52.0, 23.3 --fid 10 \
        --where "name='value'" --repeat 5
```
Result will be stored in the `/tmp/testoutput` directory
