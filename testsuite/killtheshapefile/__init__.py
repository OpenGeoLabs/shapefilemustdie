import requests
import tempfile
import subprocess
import re
import zipfile
import os
import logging
from timeit import timeit
import json

DATA_URL="https://github.com/OpenGeoLabs/shapefilemustdie/releases/download/v1.0.0/test-data.zip"
#DATA_URL="file:///home/jachym/tmp/x/test-data.zip"

FORMATS=(
    ["ESRI Shapefile", "shp"],
    ["GPKG", "gpkg"],
    ["GML", "gml"],
    ["GeoJSON", "geojson"] 
    #["FileGDB", "gdb"]
)

TEMP_DIR = None

def create_tempdir(parent=None):

    global TEMP_DIR
    tempdir = tempfile.mkdtemp(prefix="killtheshapefile", dir=parent)
    TEMP_DIR = tempdir
    logging.info("Created temporary file {}".format(TEMP_DIR))
    return tempdir

def download_data(tempdir, inpt=None):

    if not inpt:
        r = requests.get(DATA_URL, stream=True)
        d = r.headers['content-disposition']
        fname = re.findall("filename=(.+)", d)[0]
        localfile = os.path.join(tempdir, fname)
        logging.info("Downloading data")

        with open(localfile, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
    else:
        localfile=inpt

    zip_ref = zipfile.ZipFile(localfile, 'r')
    zip_ref.extractall(tempdir)
    zip_ref.close()
    files = os.listdir(tempdir)
    shps = [f for f in files if f.find("shp") > 0]
    return shps[0]

def convert_to(inpt, frmt, tempdir):

    logging.info("Converting {} to {}".format(inpt, frmt[0]))
    basename = os.path.basename(inpt)
    root_name = os.path.splitext(basename)[0]
    fullpath_in = os.path.join(tempdir, inpt)
    dest_filename = os.path.join(tempdir, "{}.{}".format(root_name, frmt[1]))

    subprocess.run(["ogr2ogr", "-f", frmt[0], dest_filename, fullpath_in])

    return [frmt[0], frmt[1], dest_filename]


def makeformats(tempdir, shp):

    formats = []
    for frmt in FORMATS:
        if frmt[0] != FORMATS[0]:
            result = convert_to(shp, frmt, tempdir)
            formats.append(result)
    return formats

def get_size(formats):

    size = {}
    for frmt in formats:
        if frmt[0] == "ESRI Shapefile":
            name, ext = os.path.splitext(frmt[-1])
            size[frmt[0]] = os.stat(frmt[-1]).st_size +\
                            os.stat(name + ".dbf").st_size + \
                            os.stat(name + ".shx").st_size
        else:
            size[frmt[0]] = os.stat(frmt[-1]).st_size

    return size

def get_metadata_time(formats, repeat=1):

    duration = {}
    for frmt in formats:
        fn = frmt[-1]
        frmt_name = frmt[0]

        if frmt_name == "GeoJSON":
            duration[frmt_name] = None
            continue

        name, ext = os.path.splitext(fn)
        layer = os.path.basename(name)
        time = timeit(
            stmt = "subprocess.run(" + str(["ogrinfo", "-so", fn, layer])+ ", stdout=subprocess.PIPE)",
            setup = "import subprocess", number = repeat)
        duration[frmt_name] = time

    return duration

def get_fid_time(formats, fid = None, repeat=1):

    if fid is None:
        fid = str(63347)
    else:
        fid = str(fid)

    duration = {}
    for frmt in formats:
        fn = frmt[-1]
        frmt_name = frmt[0]

        if frmt_name == "GeoJSON":
            duration[frmt_name] = None
            continue

        name, ext = os.path.splitext(fn)
        layer = os.path.basename(name)
        time = timeit(
            stmt = "subprocess.run(" + str(["ogrinfo", "-fid", fid, fn, layer])+ ", stdout=subprocess.PIPE)",
            setup = "import subprocess", number = repeat)
        duration[frmt_name] = time

    return duration

def get_where_time(formats, where=None, repeat=1):

    if not where:
        where = "name='OBS De Hobbit'"

    duration = {}
    for frmt in formats:
        fn = frmt[-1]
        frmt_name = frmt[0]

        if frmt_name == "GeoJSON":
            duration[frmt_name] = None
            continue

        name, ext = os.path.splitext(fn)
        layer = os.path.basename(name)
        time = timeit(
            stmt = "subprocess.run(" + str(["ogrinfo", "-where", where, fn, layer])+ ", stdout=subprocess.PIPE)",
            setup = "import subprocess", number = repeat)
        duration[frmt_name] = time

    return duration

def get_spat_time(formats, spat=None, repeat=1):

    if not spat:
        spat = ["5.421254", "52.129629", "5.421254", "52.129629"]
    else:
        spat = [str(c) for c in spat]

    duration = {}
    for frmt in formats:
        fn = frmt[-1]
        frmt_name = frmt[0]

        if frmt_name == "GeoJSON":
            duration[frmt_name] = None
            continue

        name, ext = os.path.splitext(fn)
        layer = os.path.basename(name)
        time = timeit(
            stmt = "subprocess.run(" + str(["ogrinfo", "-spat"] + \
                spat + [fn, layer]) + ", stdout=subprocess.PIPE)",
            setup = "import subprocess", number = repeat)
        duration[frmt_name] = time

    return duration

def get_seq_time(formats, repeat=1):

    duration = {}
    for frmt in formats:
        fn = frmt[-1]
        frmt_name = frmt[0]

        if frmt_name == "GeoJSON":
            duration[frmt_name] = None
            continue

        name, ext = os.path.splitext(fn)
        layer = os.path.basename(name)
        time = timeit(
            stmt = "subprocess.run(" + str(["ogrinfo", fn, layer]) + ", stdout=subprocess.PIPE)",
            setup = "import subprocess", number = repeat)
        duration[frmt_name] = time

    return duration

def prepare_data(tempdir=None, inpt=None):
    tempdir = create_tempdir(tempdir)
    shp = download_data(tempdir, inpt)
    formats = makeformats(tempdir, shp)
    return formats

def make_stats(formats, output, repeat=1, where=None, fid=None, spat=None):

    stats = {}
    stats["size"] = get_size(formats)
    stats["metadata"] = get_metadata_time(formats, repeat)
    stats["fid"] = get_fid_time(formats, fid, repeat)
    stats["where"] = get_where_time(formats, where, repeat)
    stats["spat"] = get_spat_time(formats, spat, repeat)
    stats["seq"] = get_seq_time(formats, repeat)
    with open(os.path.join(output, "stats.json"), "w") as out:
        out.write(json.dumps(stats, indent=2))
