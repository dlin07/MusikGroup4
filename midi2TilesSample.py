# some video settings
VIDEO_DPI = 1000
VIDEO_FPS = 60
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 720

# the proportion of keyboard display
KB_RATIO = 0.1

# speed of the falling tiles (pixels per sec)
# notice that this value also affect the height of each tile
TILE_VELOCITY = 500

from midi2Tiles import pianoTileCreator

ptc = pianoTileCreator.PianoTileCreator(video_width=VIDEO_WIDTH,
                                        video_height=VIDEO_HEIGHT,
                                        video_dpi=VIDEO_DPI,
                                        video_fps=VIDEO_FPS,
                                        KB_ratio=KB_RATIO,
                                        tile_velocity=TILE_VELOCITY,
                                        key_color="green",
                                        showKeyVelocity=True)
ptc.loadMidiFile("<input midi file>",verbose=True)
ptc.render("<output video file>",verbose=True)