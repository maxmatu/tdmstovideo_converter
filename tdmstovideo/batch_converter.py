import argparse
from convert import convert


def get_tdmsfile_path(fld, name, what):
    """
        Given a subfolder it returns the path to either video or metadata .tdms

        :param fld: string with path to folder to look in
        :param name: string with with name of file, will be looking for 'name.tdms' in fld
        :param what: either 'video' or 'metadata', used for meaningful error messages
    """
    tdms = [f for f in os.listdir(fld) if name in f and f.endswith(".tdms")]
    if not tdms:
        raise FileNotFoundError("Could not find {} with name {} in folder {}".format(
                            what, name, fld))
    if len(tdms) > 1:
        raise ValueError("Found more than one {} .tdms file in folder {} using name {}.\
                         Expected only one.".format(
                        what, fld, name))
    return tdms[0]

def convert_batch(fld, videoname, metadataname, dest_folder=None):
    """ Utility function to facilitate batch processing of videos to convert.
        It expects that the videos are organised in subfolders in a main folder.
        It also expects that all videos and all metadata have the same name.

        :param videoname: str, name of the video .tdms files (.fld/subfld/videoname.tdms)
        :param metadataname: str, name of the metadata .tdms files (.fld/subfld/metadataname.tdms)
        :param dest_folder: if a str is passed it should be the path to a folder to save the .mp4 into
    """
    # Iterate over each subfolder
    subfolders = [f.path for f in os.scandir(fld) if f.is_dir()]
    print("Converting videos from {} folders".format(len(subfolders)))

    for i, subfld in enumerate(subfolders):
        print("Processing subfolder {} of {}".format(i+1, len(subfolders)))
        basepath, subf = os.path.split(subfld)

        # Get path to video and metadata tdms
        videotmds = get_tdmsfile_path(subfld, videoname, 'video')
        metadatatdms = get_tdmsfile_path(subfld, metadataname, 'metadata')

        # Get path to video to save
        if not dest_folder:
            dest_folder = basepath # save in same folder where the video .tdms is 
        else:
            if not os.path.isdir(dest_folder):
                os.mkdir(dest_folder)

        name = "{}_{}.mp4".format(subf, videoname) # TODO make this customizable
        output_path = os.path.join(dest_folder, name)

        # convert
        convert(videotmds, metadatatdms, output_path=output_path)
    
    # If we reached this point everything went well.
    print("{} subfolders processed. Job done.".format(i+1))

def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        dest="videoname",
        type=str,
        help="name of video .tdms",
    )
    parser.add_argument(
        dest="metadataname",
        type=str,
        help="name of metadata .tdms",
    )

    parser.add_argument(
        "-df",
        "--dest-fld",
        dest="dest_folder",
        type=str,
        default=False,
        help="Path to folder where the videos .mp4 will be saved.",
    )

    return parser


def main():
    args = get_parser().parse_args()
    convert_batch(
        args.videoname,
        args.metadataname,
        dest_folder=args.dest_folder,
    )


if __name__ == "__main__":
    main()
