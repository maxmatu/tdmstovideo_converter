import sys
sys.path.append('./')  

import warnings as warn
import cv2

import os
from tempfile import mkdtemp
from tqdm import tqdm
from collections import namedtuple
from nptdms import TdmsFile
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import shutil
import matplotlib.pyplot as plt
import time

from files_load_save import *
from video_editor import Editor



class VideoConverter:
    def __init__(self, filepath, output='.mp4', output_folder=None, extract_framesize=True, n_processes=1):
        if filepath is None:
            return

        self.tdms_converter_parallel_processes = n_processes

        self.editor = Editor()
        if filepath is not None:
            if not isinstance(filepath, list):
                filepath = [filepath]

            # Loop over each file in list of paths
            for fpath in filepath:
                self.filep = fpath
                self.output = output
                self.extract_framesize = extract_framesize

                self.folder, self.filename = os.path.split(self.filep)
                self.filename, self.extention = os.path.splitext(self.filename)

                if output_folder is not None:
                    self.folder = output_folder
                self.codecs = dict(avi='png', mp4='mpeg4')

                # check if converted video exists in the target folders
                files_with_same_name = [f for f in os.listdir(self.folder) if self.filename in f and self.extention not in f]
                if files_with_same_name:
                    print('Fle {} was already converted. We found files like {} \n\n '.format(self.filename, files_with_same_name[0]))
                    continue
                if output in self.filep:
                    warn.warn('The file is already in the desired format {}'.format(output))
                else:
                    # Check format of original file and call appropriate converter
                    if self.extention in ['.mp4', '.mp4', '.mov']: self.videotovideo_converter()
                    elif self.extention == '.tdms':
                        if not self.output == '.mp4':
                            raise ValueError('TDMS --> Video conversion only supports .mp4 format for output video')
                        self.tdmstovideo_converter()
                    else:
                        raise ValueError('Unrecognised file format {}'.format(self.extention))




    @staticmethod
    def opencv_mp4_to_avi_converter(videopath, savepath):
        cap = cv2.VideoCapture(videopath)
        if not cap.isOpened():
            print('Could not process this one')
            # raise ValueError('Could not load video file')

        fps = cap.get(cv2.CAP_PROP_FPS)
        width, height = int(cap.get(3)), int(cap.get(4))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        videowriter = cv2.VideoWriter(savepath, fourcc, fps, (width , height ), False)
        print('Converting video: ', videopath)
        framen = 0
        while True:
            if framen % 1000 == 0: print('Frame: ', framen)
            framen += 1
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            videowriter.write(gray)
        videowriter.release()




    @staticmethod
    def extract_framesize_from_metadata(videotdms):
        """extract_framesize_from_metadata [takes the path to the video to be connverted and 
            uses it to extract metadata about the acquired video (frame widht and height...)]
        
        Arguments:
            videotdms {[str]} -- [path to video.tdms]
        Returns:
            frame width, height and number of frames in the video to be converted
        """
        print('Extracting metadata...', videotdms)
        # Find the tdms video
        paths = load_yaml(paths_file)
        
        metadata_fld = os.path.join(paths['raw_data_folder'], paths['raw_metadata_folder'])

        videoname = os.path.split(videotdms)[-1]
        try:
            metadata_file = [os.path.join(metadata_fld, f) for f in os.listdir(metadata_fld)
                                if videoname in f][0]
        except:
            print("Could not load metadata for {} in folder {}".format(videoname, metadata_fld))
            raise ValueError("Could not load metadata for {} in folder {}".format(videoname, metadata_fld))
        
        # Get info about the video data
        # video = TdmsFile(videotdms)
        # video_bytes = video.object('cam0', 'data').data
        video_size = os.path.getsize(videotdms)


        # Get info about the metadata
        metadata = TdmsFile(metadata_file)

        # Get values to return
        metadata_object = metadata.object()
        props = {n:v for n,v in metadata_object.properties.items()} # fps, width, ...  code below is to print props out

        if props['width'] > 0:
            tot = np.int(round(video_size/(props['width']*props['height'])))  # tot number of frames 
            if tot != props['last']:
                raise ValueError('Calculated number of frames doesnt match what is stored in the metadata: {} vs {}'.format(tot, props['last']))
        else:
            tot = 0

        return props, tot




    def tdmstovideo_converter(self):
        def write_clip(arguments, limits=None, clean_name=False):
            """ create a .cv2 videowriter and start writing """
            vidname, w, h, framerate, data = arguments
            if clean_name:
                vidname = '{}.mp4'.format(vidname)
            else:
                vidname = '{}__{}.mp4'.format(vidname, limits[0])
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            videowriter = cv2.VideoWriter(os.path.join(self.folder, vidname), fourcc,
                                            framerate, (w, h), iscolor)

            for framen in tqdm(range(limits[0], limits[1]+1)):
                videowriter.write(data[framen])
            videowriter.release()

        ###################################################################################################################################

        start = time.time()
        
        print("Ready to convert: ", self.filep)

        props, tot_frames = self.extract_framesize_from_metadata(self.filep)

        print("Got metadata\n")
        # ? set up options
        # Number of parallel processes for faster writing to video
        num_processes = self.tdms_converter_parallel_processes
        iscolor = False  # is the video RGB or greyscale
        print('Preparing to convert video, saving .mp4 at {}fps using {} parallel processes'.format(props['fps'], num_processes))
        print('Total number of frames {}'.format(tot_frames))

        # * Get file from winstore
        # temp_file = load_tdms_from_winstore(self.filep)
        # tempdir = os.path.split(temp_file)[0]

        # ? alternatively just create a temp folder where to store the memmapped tdms
        # Open video TDMS 
        try:    # Make a temporary directory where to store memmapped tdms
            os.mkdir(os.path.join("D:\\", 'Temp'))
        except:
            pass
        tempdir = os.path.join("D:\\", 'Temp')

        print('Opening TDMS: ', self.filename + self.extention)
        print("Opening binary at: ", self.filep)
        bfile = open(self.filep, 'rb')

        print('  ...binary opened, opening mmemmapped')
        openstart = time.time()
        tdms = TdmsFile(bfile, memmap_dir=tempdir)  # open tdms binary file as a memmapped object
        openingend = time.time()

        print('     ... memmap opening took: ', np.round(openingend-openstart, 2))
        print('Extracting data')
        tdms = tdms.__dict__['objects']["/'cam0'/'data'"].data.reshape((tot_frames, props['height'], props['width']), order='C')
        tdms = tdms[:, :, :(props['width']+props['padding'])]  # reshape

        # Write to Video
        print('Writing to Video {} - {} parallel processes'.format(self.filename, num_processes))
        params = (self.filename, props['width'], props['height'], props['fps'], tdms)  # To create a partial of the writer func

        if num_processes == 1:
            limits = [0, tot_frames-1]
            write_clip(params, limits, clean_name=True)
            clip_names = ['{}.mp4'.format(self.filename)]
        else:
            # Get frames range for each video writer that will run in parallel
            # vid 1 will do A->B, vid2 B+1->C ...
            frame_numbers = [i for i in range(int(tot_frames))]
            splitted = np.array_split(frame_numbers, num_processes)
            limits = [(int(x[0]), int(x[-1])) for x in splitted]
            print(limits)
            
            # Create partial function
            partial_writer = partial(write_clip, params)

            # start writing
            pool = ThreadPool(num_processes)
            _ = pool.map(partial_writer, limits)
            clip_names = ['{}__{}.mp4'.format(self.filename, lim[0]) for lim in limits]

        # Check if all the frames have been converted
        readers = {}
        print('\n\n\nSaved clips: ', clip_names)
        frames_counter = 0
        for clip in clip_names:  
            # Open each clip and get number of frames
            cap = cv2.VideoCapture(os.path.join(self.folder, clip))
            nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frames_counter += nframes
            print(clip, ' has frames: ', nframes)
        print('Converted clips have {} frames, original clip had: {}'.format(frames_counter, tot_frames))
        if not tot_frames == frames_counter:
            raise ValueError('Number of frames in converted clip doesnt match that of original clip')

        # Remove temp file
        ##os.remove(temp_file)

        # fin
        end = time.time()
        print('Video writing and extra handling tooK : ', np.round(end-openingend, 2))
        print('Converted {} frames in {}s\n\n'.format(tot_frames, round(end-start)))