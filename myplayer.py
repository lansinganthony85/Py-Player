import tkinter
import os
import tkinter.filedialog
from pygame import mixer

# Anthony Lansing
# My MP3 Player
# An MP3 player where the user can load songs from a directory, play, pause, stop, and skip songs
# with the capability to adjust the volume
# MP3 buttons originally from publicdomainvectors.org

# Create a class that when initiated creates an instance of the MP3 player
class my_player:

    # constructor of the class where all the action takes place. A window is create that contains
    # all the functionality and appearance of the MP3 player when instantiated
    def __init__(self):
        
        # initialize the mixer and window to start using it
        mixer.init()
        self.window = tkinter.Tk()

        
        # load all the images needed for the MP3 player
        self.FILE_PHOTO = tkinter.PhotoImage(file="song.png").subsample(5,5)
        self.PLAY_PHOTO = tkinter.PhotoImage(file="play.png").subsample(3,3)
        self.PAUSE_PHOTO = tkinter.PhotoImage(file="pause.png").subsample(3,3)
        self.STOP_PHOTO = tkinter.PhotoImage(file="stop.png").subsample(5,5)
        self.NEXT_PHOTO = tkinter.PhotoImage(file="forward.png").subsample(5,5)
        self.BACK_PHOTO = tkinter.PhotoImage(file="backward.png").subsample(5,5)
        self.ICON = tkinter.PhotoImage(file='icon.png')
        
        # initialize variable indicating file type of songs for the MP3 player
        self.FILE_TYPE = '.mp3'

        self.COLOR = '#8E8E8E'
        self.FONT = ('Calibri', '12')
        
        # set the window color and title
        self.window.config(bg=self.COLOR)
        self.window.title('My MP3 Player')
        self.window.iconphoto(False, self.ICON)
        
        # initialize the frames to hold everything
        self.top_frame = tkinter.Frame(self.window, bg=self.COLOR)     #top frame to hold directory button and exit button
        self.mid_frame = tkinter.Frame(self.window, bg=self.COLOR)     #mid frame to hold the song list
        self.bottom_frame = tkinter.Frame(self.window, bg=self.COLOR)  #bottom frame to hold controls and volume bar

        self.file_list = []     #list to hold all the songs loaded in a directory
        self.folder = ''        #the folder path for all the songs
        
        # the song state keeps track of whether the song is being playered for the first time
        # represented as 0, being paused after initially starting to play, represented by 1, and
        # able to be unpaused, represented as 2
        self.song_state = tkinter.IntVar()
        
        self.songname = tkinter.StringVar() #when a song is selected, that info is stored here
        
        # create the load directory button which is just a label that contains an image
        self.dir_button = tkinter.Label(self.top_frame, image=self.FILE_PHOTO, bg=self.COLOR)
        
        # I use the bind function here to link the mouse click to the label so that when it is clicked,
        # the function is activated, essentially turning it into a button, but without the box shape. I
        # use a lambda expression for the command since bind has not command attribute
        self.dir_button.bind('<Button-1>', lambda action: self.load_directory())
        self.dir_button.pack(side='left')
        
        # create the exit button using the same method as above
        self.exit_button = tkinter.Button(self.top_frame, text="X", command=exit, padx=5)
        #self.exit_button.bind('<Button-1>', lambda action: exit())
        self.exit_button.pack(side='right')
        
        # create the song list using a Listbox. When clicked, two actions are performed as seen in the 
        # lambda expression: the song state is reset so that the MP3 player knows not to pause, and the
        # image of the button is set back to play so that the user visually understands that a new song
        # will be played when selected.
        self.song_list = tkinter.Listbox(self.mid_frame, selectmode=tkinter.SINGLE, height=15, width=50, bg=self.COLOR, font=self.FONT)
        self.song_list.bind('<Button-1>', lambda action: [self.song_state.set(0), self.play_button.config(image=self.PLAY_PHOTO)])
        self.song_list.pack(side='left')
        
        # create the scroll bar for the song list. This is essentially the same code from the textbook
        self.scroll_bar = tkinter.Scrollbar(self.mid_frame, orient=tkinter.VERTICAL, bg=self.COLOR)
        self.scroll_bar.pack(side='right', fill=tkinter.Y)
        self.scroll_bar.config(command=self.song_list.yview)
        self.song_list.config(yscrollcommand=self.scroll_bar.set)
        
        # create the back button, when clicked (thanks to the bind function), the skip_backward
        # function is activated
        self.back_button = tkinter.Label(self.bottom_frame, image= self.BACK_PHOTO, bg=self.COLOR)
        self.back_button.bind('<Button-1>', lambda action: self.skip_backward())
        self.back_button.pack(side='left')
        
        # create the stop button that stops the music
        self.stop_button = tkinter.Label(self.bottom_frame, image=self.STOP_PHOTO, bg=self.COLOR)
        self.stop_button.bind('<Button-1>', lambda action: self.stop())
        self.stop_button.pack(side='left')
        
        # create the play button
        self.play_button = tkinter.Label(self.bottom_frame, image=self.PLAY_PHOTO, bg=self.COLOR)
        self.play_button.bind('<Button-1>', lambda action: self.play_pause())
        self.play_button.pack(side='left')
        
        # create the next button that skips forward
        self.next_button = tkinter.Label(self.bottom_frame, image=self.NEXT_PHOTO,bg=self.COLOR)
        self.next_button.bind('<Button-1>', lambda action: self.skip_forward())
        self.next_button.pack(side='left')
        
        #create the volume bar
        self.vol_var = tkinter.DoubleVar() # variable that sets the default value of the volume bar
        self.vol_var.set(50) #default volume is 50%
        self.vol_scale = tkinter.Scale(self.bottom_frame, from_=0, to=100, digits=1, orient=tkinter.HORIZONTAL, command=self.set_vol, showvalue=0, variable=self.vol_var, bg=self.COLOR)
        self.vol_scale.pack(side='right')
        
        # pack the frames
        self.top_frame.pack(expand=True, fill=tkinter.BOTH)
        self.mid_frame.pack()
        self.bottom_frame.pack()
        
        # start the main loop
        tkinter.mainloop()
        
    
    # this function, depending on the song_state, will either start playing from the beginning
    # of the song, pause the song, or unpause the song    
    def play_pause(self):
        #play the song from the beginning if the song state is at 0
        if self.song_state.get() == 0:
            
            index = self.song_list.curselection()   # get the index of the song currently selected
            filename = self.song_list.get(index)    # get the name of the song from the index
            full_name = os.path.join(self.folder, filename) # the full PATH is needed to play the song
            
            mixer.music.load(full_name + self.FILE_TYPE)    # load the song into the player
            
            self.set_vol(self.vol_scale.get())      # when the player is first loaded, it might not play at default vol, so set here
            mixer.music.play()
            
            # change the image on the button and change the song's state
            self.play_button.config(image=self.PAUSE_PHOTO)
            self.song_state.set(1)
        
        # case to pause the song if the song_state is 1    
        elif self.song_state.get() == 1:
            self.play_button.config(image=self.PLAY_PHOTO) #change photo back to play image
            self.song_state.set(2)  # change the state to show that it can be unpaused
            mixer.music.pause()
        
        # last case is simply to unpause and change state/image
        else:
            self.play_button.config(image=self.PAUSE_PHOTO)
            self.song_state.set(1)
            mixer.music.unpause()
    
    # function that skips to the next song on the list
    def skip_forward(self):
        # first need to clear what it currently selected
        index = self.song_list.curselection()[0]
        self.song_list.selection_clear(index)
        
        self.song_state.set(0)     # reset the song state
        
        # if at the bottom of the list, we will got to the top of the list
        if index+1 == self.song_list.size():
            self.song_list.select_set(0)
        else:
            self.song_list.select_set(index+1)
            
        self.play_pause()

    # similar function to skip_forward above only we will be going backward
    def skip_backward(self):
        # like before, we must clear what is currently selected
        index = self.song_list.curselection()[0]
        self.song_list.selection_clear(index)
        
        self.song_state.set(0)     # reset the song state
        
        #now if we are at the top of the list, we must go to the bottom
        if index-1 < 0:
            self.song_list.select_set(self.song_list.size()-1)
        else:
            self.song_list.select_set(index-1)
            
        self.play_pause()

    # function that loads a directory and store all MP3's in a list
    def load_directory(self):
        # pop up a window and ask for the directory then load directory into a list
        self.folder = tkinter.filedialog.askdirectory()
        self.file_list = os.listdir(self.folder)
        
        # go over the list and add all songs to the listbox
        for file in self.file_list:
            if file.endswith(self.FILE_TYPE):
                name, ext = file.split('.')
                self.song_list.insert(tkinter.END, name)
    
    # function that stops whatever is being played
    def stop(self):
        mixer.music.stop()
        self.song_state.set(0) # reset the song state
        self.play_button.config(image=self.PLAY_PHOTO)
    
    # function that exits the MP3 player. The music stops, the mixer quits, and the window closes
    def exit(self):
        self.stop()
        mixer.quit()
        self.window.destroy()

    # functions that sets the volume according the volume bar. Two parameters are required: self which is this
    # object, and vol which is the value passed from the vol_scale
    def set_vol(self, vol):
        volume = int(vol)/100
        mixer.music.set_volume(volume)

# the main function that when it runs, an instance of the my_player class is created and the MP3 runs        
def main():
    mp3 = my_player()

# run main if not loaded as a module
if __name__ == '__main__':
    main()