import os
import cv2
import numpy as np
from nptdms import TdmsFile
import time
import argparse
from tqdm import tqdm
tot_frames = 444888
def get_video_metadata(videotdms, metadatatdms):
    """
    Gets metadata about the video to be converted. These include fps, width and height of 
    frame and total number of frames in video.

    :param videotdms: path to video .tdms
    :param metadatdms: path to metadata .tdms
    :returns: a dictionary with the metadata and an integer with number of frames to convert
    :raises ValueError: if there's a mismatch between expected and reported number of frames
    """
    print(" extracting metadata from: ", metadatatdms)

    # Load metadata
    metadata = TdmsFile(metadatatdms)

    # Get values to return
    metadata_object = metadata.object()
    props = {n:v for n,v in metadata_object.properties.items()} # fps, width, ...  
    videosize = os.path.getsize(videotdms)
    # Check how many frames are in the video given frame size and # bites in video file
    #if props['width'] > 0:
        # Get size of video to be converted 
    #    videosize = os.path.getsize(videotdms)
    #    tot = np.int(round(videosize/(props['width']*props['height'])))  # tot number of frames 
    #    if tot != props['last']:
    #        raise ValueError('Calculated number of frames doesnt match what is stored in the metadata: {} vs {}'.format(tot, props['last']))
    #else:
    #    tot = 0

    return props#, tot


def write_clip(data, savename, tot_frames, w, h, framerate, iscolor=False):
    """ Create a .cv2 videowriter to write the video to file 
    
        :param data: data loaded from video .tdms
        :param savename: string with path so save the video at
        :param tot_frames: number of frames in video
        :param w: width of frame in pixels
        :param h: height of frame in pixels
        :param framerate: fps of video
        :param iscolor: set as True if want to save the video as color data
    """

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    videowriter = cv2.VideoWriter(savename, fourcc, framerate, (w, h), iscolor)

    for framen in tqdm(range(tot_frames)):
        videowriter.write(data[framen])
    videowriter.release()



def convert(videotdms, metadatatdms, fps=None, use_local_fld=False, output_path=False):
    """ 
        Converts a video from .tdms to .mp4. Needs to have access to a metadata .tdms file
        to get the expected frame size and number of frames to convert.

        :param videotdms: string with path to video .tdms
        :param metadatatdms: string with path to metadata .tdms
        :param fps: int, optional. To specify the fps of the output file
        :param use_local_fld: if a string is passed the memmapped .tdms file is saved in a user given folder
        :param output_path: if passed it should be a string with the path to where the video .mp4 will be saved
    """
    start = time.time()
    print("Ready to convert: ", videotdms)

    # Get output path
    if not output_path:
        savepath = videotdms.split(".")[0]+".mp4"
    else:
        savepath = output_path
        
    if os.path.isfile(savepath):
        print("The output file passed already exists {}".format(output_path))
        yn = input("Overwrite? [y/n] ")
        while yn.lower() not in ["y", "n"]:
            yn = input("Please reply 'y' or 'n' ")
        if yn.lower() == 'n':
            raise FileExistsError("Output path points to an already existing file: {}".format(savepath))
        else:
            print("Overwriting output file")

    # Get metadata
    props = get_video_metadata(videotdms, metadatatdms)
    if fps is None:
        fps = props['fps']

    # Get temp directory to store memmapped data
    if use_local_fld:
        # Copy the video to be converted to a local directory
        if not os.path.isdir(use_local_fld):
            raise ValueError("Passed 'use_local_fld' argument but it's not a valid directory': ", use_local_fld)
        tempdir = use_local_fld
    else:
        tempdir = os.path.split(videotdms)[0]

    # Open memmapped
    print('     Opening mmemmapped file in: ' + tempdir+"[this might take a while...]")
    openstart = time.time()
    tdms = TdmsFile(videotdms, memmap_dir=tempdir)  # open tdms binary file as a memmapped object
    openingend = time.time()

    print('         ... memmap opening took: {}s'.format(np.round(openingend-openstart, 2)))
    print('     Extracting data')
    tdms = tdms.__dict__['objects']["/'cam0'/'data'"].data.reshape((tot_frames, props['height'], props['width']), order='C')
    tdms = tdms[:, :, :(props['width']+props['padding'])]  # reshape

    # Write to Video
    print('     Writing video at: ', savepath)
    write_clip(tdms, savepath, tot_frames, props['width'], props['height'], fps)
    print('     Finished writing video in {}s.'.format(round(time.time()-openingend, 2)))

    # Check if all the frames have been converted
    cap = cv2.VideoCapture(savepath)
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print('     Converted video has {} frames, original video had: {}'.format(nframes, tot_frames))
    if not tot_frames == nframes:
        raise ValueError('Number of frames in converted clip doesnt match that of original clip')

    # fin
    end = time.time()
    print('     Converted {} frames in {}s\n\n'.format(tot_frames, round(end-start)))



def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        dest="videotdms",
        type=str,
        help="path to video .tdms",
    )
    parser.add_argument(
        dest="metadatatdms",
        type=str,
        help="path to metadata .tdms",
    )


    parser.add_argument(
        "-fps",
        "--fps",
        dest="fps",
        type=int,
        default=None,
        help="Fps of output video. Should match what you recorded at.",
    )

    parser.add_argument(
        "-op",
        "--output-path",
        dest="output_path",
        type=str,
        default=False,
        help="Path to where the video .mp4 will be saved.",
    )

    parser.add_argument(
        "-lf",
        "--local-folder",
        dest="use_local_fld",
        type=str,
        default=False,
        help="Path to a local folder used to save memmap.",
    )
    return parser


def main():
    args = get_parser().parse_args()
    convert(
        args.videotdms,
        args.metadatatdms,
        use_local_fld=args.use_local_fld,
        output_path=args.output_path,
        fps = args.fps,
    )


if __name__ == "__main__":
    main()
