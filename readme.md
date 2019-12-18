
![](doc/result_image.png) ![](doc/result_xml.png)

# Abstract
- This module helps you to call animeface-2009 on Python.
- Additionally, it can generate an XML file of detection results.

# Install
0. If you forget recursive clone, `$ git submodule update --init --recursive`
1. Build [animeface-2009(fork)](https://github.com/meow-noisy/animeface-2009).
    - To build, see `animeface-2009/README.md`
2. Prepair your own python environment
3. `$ pip install requirements.txt`

# How to use
## detect face in an anime image
- `python animeface_poor_caller.py [image you want test]`
    - and function outputs a result image where you run

## generate XML files
- `python animeface_result2xml.py [image directory] [output directory] [textfilepath imagelist]`
    - e.g. `animeface_result2xml.py input output filelist.txt`