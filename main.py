import os
import sys
import datetime
import time

import discordrpc

class CmusNowPlaying:
    def __init__(self, update_interval: datetime.time = datetime.time(second=1)):
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

def rpc_update():
    while(True):
        time.sleep(1)
        try:
           (title, artist, track, album, release, duration, position, album_art) = cmusnp.get_tags()
        except Exception as e:
           print(f"Error getting cmus tags: {e}")
           continue

        rpc.set_activity(
            large_text = f"{title}",
            state = f"{artist} - {title}",
            details = f"{album}",
            ts_start = position,
            ts_end = duration,
        )
        pass
    pass

if __name__ == '__main__':
    # DEBUG -- SAMPLE USAGE

    cmusnp = CmusNowPlaying()
    rpc = discordrpc.RPC(app_id="1346187681024966757")
    rpc.set_activity()
    rpc_update()
    sys.exit()
