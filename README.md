# SEEGFusion

Fuse a CT image with an MRI image from a Stereotactic ElectroEncephalography (SEEG).

This method  is explained in the following article

[10.3390/diagnostics13223420](https://doi.org/10.3390/diagnostics13223420)

![Fusion method](images/image_fusion.png)

## Prerequisites

To use SEEGFusion, the following software and toolkits are required

* SimpleITK
* ROBEX

## ROBEX Installation

Download ROBEX from the following link: [ROBEX](https://www.nitrc.org/frs/download.php/5994/ROBEXv12.linux64.tar.gzjk)

Extract the files and move them to a folder, it can be in the folder `opt/`

```Shell
tar -xf ROBEXv12.linux64.tar.gz
sudo mv ROBEX /opt/
```

Add the directory to the environment variables in `~/.bashrc`

```Shell
ROBEX=/opt/ROBEX
export ROBEX

PATH=${PATH}:$ROBEX
```

Validate that the Systems detect the ROBEX commands

```Shell
source ~/.bashrc

runROBEX.sh
```

![ROBEX Installed](images/ROBEX_installed.png)

## SimpleITK Installation

Install using Python pip, [SimpleITK](https://simpleitk.readthedocs.io/en/master/gettingStarted.html)

```shell
pip install SimpleITK
```

---------------------

## Set up virtual environment for Python

```shell
python -m venv venv
source  venv/bin/activate
pip install -r python/requirements.txt
```

### Fuse 2 images

To fuse two images, use the script in `python/src/Fuse.py`

```shell
python Fuse.py ct_path mri_path output_path
```
