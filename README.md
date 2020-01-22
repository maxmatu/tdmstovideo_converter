Python scripts to convert `.tdms` video files from mantis to `.mp4`

## Installation
Open your anaconda prompt and use the following commands to create an environment to use the convert.
```
conda create -n tdmsconverter python=3.7
```
Once the environment is created activate it with `conda activate tdmsconverter` and install other packages:
```
pip install numpy opencv-python npTDMS tqdms
```

Don't forget to clone this repository somewhere. 

All done!

## Usage
### Single file
The simplest way to use the converter is with this command (in the anaconda prompot with `tdmsconverter` environemnt activated):
```
  cd path_to_where_this_repo_is_cloned
  python converter.py path_to_video path_to_metadata
```

`converter.py` takes two arguments: `path_to_video` should be the path to the `video.tdms` you need to convert while
`path_to_metadata` should be the path to the `metadata.tdms` file produced by mantis. 

If you want to specify the path where the video.mp4 should be saved you can use the `-op` argument. Otherwise the file will be saved as `../tdmsvideo.mp4`.

### Batch processing
You can use the converter to process multiple videos at once. 
The converter expects that your files are organised like so:
```
  folder
    subfolder1
        videoname.tdms
        metadataname.tdms
    subfolder2
        videoname.tdms
        metadataname.tdms
    ...
  ```
  
If that is the case, then you can use:
```
  cd path_to_where_this_repo_is_cloned
  python batch_converter.py path_to_folder videoname metadataname
```

If you wish you can pass the additional argument `--dest-fld path_to_dest_folder` to specify a folder where the videos will be saved. Alternative each video.mp4 file will be saved in its respective subfolder. The video.mp4 files will be saved as: `../subfoldername_videoname.mp4`


## Other
If you forget what the arguments to each script are you can always to something like:
`python converter.py -h` to get a reminder. 

For any issue/feature request get in touch or submit an issue. 




  
