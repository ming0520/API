"""
/*+----------------------------------------------------------------------
 ||
 ||  Class Timecode
 ||
 ||         Author:  Zhong Ming Tan
 ||
 ||        Purpose:  To make a robust timecode object and improve the existing python timecode class
 ||
 ||  Inherits From:  None
 ||
 ||     Interfaces:  None
 ||
 |+-----------------------------------------------------------------------
 ||
 ||      Constants:  None
 ||
 |+-----------------------------------------------------------------------
 ||
 ||   Constructors:  None
 ||
 ||  Class Methods:  set_fps(float), set_by_seconds(int), set_by_frames(int), set_by_timecode(str),
 ||                  ceil_frames(), floor_frames(),round_frame() ,get_fps():float, get_seconds():int,
 ||                  get_timecode():string, get_time():array, get_frames():int
 ||
 ||  Inst. Methods:  [List the names, arguments, and return types of all
 ||                   public instance methods.]
 ||
 ++-----------------------------------------------------------------------*/
"""
class Timecode:

    def __init__ (self, fps=30,hours=0,minutes=0,seconds=0,frames=0):
        self.framerate = float(fps)
        self.hours = int(hours)
        self.minutes = int(minutes)
        self.seconds = int(seconds)
        self.frames = int(frames)

    def set_fps(self,fps):
        self.framerate      =   float(fps)

    def set_by_seconds(self, input):
        self.set_by_frames(round(int(input)*self.framerate))
    
    def set_by_frames(self,frames):
        total_seconds       =   frames/self.framerate
        self.hours          =   int(total_seconds/3600)
        self.minutes        =   int(total_seconds/60%60)
        self.seconds        =   int(total_seconds%60)
        self.frames         =   round((total_seconds-int(total_seconds))*self.framerate)

    def set_by_timecode(self,timecode):
        splittedTimecode    =   timecode.split(':')
        self.hours          =   int(splittedTimecode[0])
        self.minutes        =   int(splittedTimecode[1])
        self.seconds        =   int(splittedTimecode[2])
        self.frames         =   int(splittedTimecode[3])

    def get_fps(self):
        return self.framerate

    def get_seconds(self):
        total_seconds = ((self.hours*3600) + (self.minutes*60) + (self.seconds))
        total_seconds = total_seconds + (self.frames/self.framerate)
        return total_seconds

    def get_time(self):
        return [self.hours,self.minutes,self.seconds,self.frames]
    
    def get_timecode(self):
        return '{h:02d}:{m:02d}:{s:02d}:{f:02d}'.format(h=self.hours,m=self.minutes,s=self.seconds,f=self.frames)
    
    def get_timecode_ffmpeg(self):
        return '{h:02d}:{m:02d}:{s:f}' \
        .format(h=self.hours,
                m=self.minutes,
                s=( float( self.seconds + (self.frames/self.framerate) ) )
               )        
    
    def get_frames(self):
        total_seconds = int((self.hours*3600) + (self.minutes*60) + (self.seconds))
        total_frames = int((total_seconds * self.framerate) + self.frames)
        return total_frames
    
    def ceil_frames(self):
        if self.frames > 0:
            ceil_seconds = self.get_seconds() + 1
            self.set_by_seconds(ceil_seconds)

    def floor_frames(self):
        if self.frames > 0:
            self.frames = 0
    
    def round_frames(self):
        threshold = self.framerate / 2
        if self.frames > threshold:
            self.ceil_seconds()
