import os
import sys
import datetime
import time
import re

import deezer
import discordrpc

APP_ID = "1346187681024966757"

class CmusNowPlaying:
    def __init__(self, update_interval : datetime.time = datetime.time(second=1), album_art : str = ""):
        self.tags: list[str] = []

        self.artist: str = ""
        self.album: str = ""
        self.album_art: str = ""
        self.song: str = ""
        self.track: str = ""
        self.position: int = 0
        self.duration: int = 0
        self.release: str = ""

        self.update_tags()
        pass

    def get_tags(self) -> tuple:
        self.update_tags()
        for tag in self.tags:
            tag_arr = tag.split(' ')
            if tag_arr[0] == "tag":
                match tag_arr[1]:
                    case 'title':
                        self.song = tag[10:-1]
                    case 'artist':
                        self.artist = tag[11:-1]
                    case 'tracknumber':
                        self.track = tag[16:-1]
                    case 'album':
                        self.album = tag[10:-1]
                    case 'date':
                        self.release = tag[8:-1]
            elif tag_arr[0] == "duration":
                self.duration = int (tag_arr[1][:-1])
            elif tag_arr[0] == "position":
                self.position = int (tag_arr[1][:-1])
            elif tag_arr[0] == "file":
                self.album_art = '/'.join(tag_arr[1].split('/')[:-1]) + '/cover.jpg'

        return (self.song, self.artist, self.track, self.album, self.release, self.duration, self.position, self.album_art)


    def update_tags(self):
        os.system("cmus-remote --query | grep -e tag -e duration -e position -e file > cmus-nowplaying.txt")
        with open('cmus-nowplaying.txt', 'r') as f:
            self.tags = f.readlines()
        pass

def rpc_update(cmusnp: CmusNowPlaying, rpc: discordrpc.RPC):

    now_playing : str = ""
    start_time : int = 0
    dzc = deezer.Client()
    cover_sm = ""

    while(True):
        time.sleep(5)
        try:
           (title, artist, track, album, release, duration, position, album_art) = cmusnp.get_tags()
        except Exception as e:
           print(f"Error getting cmus tags: {e}")
           continue

        if(title != now_playing):
            now_playing = title
            start_time = int(time.time()) - position
        else:
            continue
        # Get album art from Deezer
        try:
            # album_trimmed = album.split('[')[0].split('(')[0] # remove suffixes (such as <Deluxe Edition>)
            album_trimmed = re.split(r'[\[\(\<]+', album)[0]
            cover_list = dzc.search_albums(f"{artist} {album_trimmed}")
            print(cover_list) # DEBUG
            cover_sm = cover_list[0].cover
        except Exception as e:
            print(f"Error: {e}.")
            print(f"Could not get album art for {artist} - {album}")
            cover_sm = "jigglypuff" # something has gone wrong if you see jigglypuff
        pass
        rpc.set_activity(
            large_text = f"{album}",
            state = f"{artist}",
            details = f"{title}",
            act_type = 2,
            ts_start = start_time, # why does this not work...
            ts_end = start_time + duration,
            # large_image = "",
            small_image = cover_sm,
        )
        pass
    pass

if __name__ == '__main__':
    # DEBUG -- SAMPLE USAGE

    cmusnp = CmusNowPlaying()
    rpc = discordrpc.RPC(app_id=APP_ID)
    # rpc = Presence(client_id=APP_ID)
    rpc_update(cmusnp, rpc)
    sys.exit()
