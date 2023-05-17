# Coeus: A Universal Search Engine for  Additive Manufacturing [![Python 3][badge-python3]]((https://www.python.org/))  [<img src="https://mirrors.creativecommons.org/presskit/icons/heart.black.png" alt="License CC" title="License CC" width="3.5%">](https://creativecommons.org/licenses/by/4.0/) 

## Coeus Overview

![alt text][overview]
Coeus provides 3D search capabilities through use of depth based images and silhouettes. This allows for several different inputs, as the base shape descriptor relies on 3D information extracted from 2D photographs. These raw object views are first converted into 2.5D depth based images. Afterwards, a 2D  fourier transform is performed, local maxima "peaks" corresponding to shape inflection points are detected, and SHA-1 based  signature is generated based on the distance between the peaks

#### How to cite this work

The journal article describing Coeus can be accessed [here](https://ieeexplore.ieee.org/document/10113214).
The article can be cited as follows:
```
L. Folkerts, N. Kater, and N. G. Tsoutsos,
"Coeus: A Universal Search Engine for  Additive Manufacturing",
in IEEE Access, vol. XX, pp. YYYY-ZZZZ, 2023, doi: 10.1109/ACCESS.2023.3271890.
```

## Installation
```
git clone https://github.com/TrustworthyComputing/Coeus.git
cd Coeus/src
pip3 install -r requirements.txt
```

## Usage
This work relies on and [MarrNet/Genre](https://github.com/xiumingzhang/GenRe-ShapeHD) for depth based image creation and
[Fourier Fingerprint Search (FFS)](https://github.com/TrustworthyComputing/Fourier-Fingerprint-Search)  for the signature and database backend. 

We provide a subset of MarrNet ouputs for immediate testing. The full dataset and MarrNet outputs of files can be found [here](https://drive.google.com/drive/folders/1K3xGPXmYrD-I3b46lG7FwCY2E178RX6w).

### Learn
Coeus supports two modes, `learn` and `search`. For  `learn` mode, you can use the png2array_main.py directed to the everyday_shapehd dataset. Here, each subfolder is typed with the class label separated with a hyphen. To run the code with a MarrNet output, direct the file to the everyday_shapehd output.

``
python3 png2array_main.py --mode learn --file ../sample_data/ --num_of_objects 30 
``
### Search

Similarly, we can test an output dataset by using the search mode. The number of matches to the subdirectory is returned.

``
python3 png2array_main.py --mode search --file ../sample_data/ --num_of_objects 30 
``



<p align="left">
    <img src="./images/NSF.png" height="8%" width="8%">
    This material is based upon work supported by the National Science Foundation under Grant No. 2234974. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the National Science Foundation.
</p>


<p align="left">
    <img src="./images/twc.png" height="8%" width="8%">
    This material was developed by the Trustworthy Computing Group at the University of Delaware.
</p>

[overview]: ./images/SystemOverview.PNG
[badge-python3]: https://img.shields.io/badge/python-3-blue.svg?style=flat-square

