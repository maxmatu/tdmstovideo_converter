Python scripts to convert `.tdms` video files from mantis to `.mp4`

## Installation
Open your anaconda prompt and use the following commands to create an environment to use the convert.
```
conda create -n tdmsconverter python=3.7
```
Once the environment is created activate it with `conda activate tdmsconverter` and install other packages:
```
pip install numpy opencv-python npTDMS
```

Don't forget to clone this repository somewhere. 

All done!

## Usage
The simplest way to use the converter is with this command (in the anaconda prompot with `tdmsconverter` environemnt activated):
```
  cd path_to_where_this_repo_is_clonded
  python converter.py path_to_video path_to_metadata
```

`converter.py` takes two arguments: `path_to_video` should be the path to the `video.tdms` you need to convert while
`path_to_metadata` should be the path to the `metadata.tdms` file produced by mantis. 
