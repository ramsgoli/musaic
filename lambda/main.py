import json
import spotipy
import tempfile
from urllib import urlretrieve
import multiprocessing
from os import listdir, path
import shutil

def download_album_cover_func(url, directory):
    file_name = url.split("/")[-1]
    file_path = path.join(directory, file_name)
    urlretrieve(url, file_path)

def get_playlist_ids(sp, playlist_id):
    user_id = sp.me()["id"]
    fields = "items(track(album(id))),next"
    data = sp.user_playlist_tracks(user_id, playlist_id=playlist_id, fields=fields)
    ids = set([item["track"]["album"]["id"] for item in data["items"] if item["track"]["album"]["id"]])

    while data["next"]:
        data = sp.next(data)
        for item in data["items"]:
            if item["track"]["album"]["id"]:
                ids.add(item["track"]["album"]["id"])

    return ids

def download_album_cover_art(sp, playlist_ids):
    temp_dir = tempfile.mkdtemp()

    processes = []
    playlist_ids = list(playlist_ids)

    for i in range(0, len(playlist_ids), 20):
        albums = sp.albums(playlist_ids[i:i+20])
        image_urls = [album["images"][0]["url"] for album in albums["albums"]]

        # for each image URL, instantiate a process to download
        for image_url in image_urls:
            p = multiprocessing.Process(target=download_album_cover_func, args=(image_url, temp_dir))
            processes.append(p)
            p.start()

    # wait for all images to finish downloading
    for process in processes:
        process.join()

    # list all images downloaded
    print(listdir(temp_dir))

    # clean up
    shutil.rmtree(temp_dir)



def lambda_handler(event, context):
    playlist_id = event["playlist_id"]
    image_data = event["image_data"]
    access_token = event["access_token"]

    # get all album covers in this playlist id
    sp = spotipy.Spotify(auth=access_token)
    
    # get all unique album ideas 
    playlist_ids = get_playlist_ids(sp, playlist_id)

    # download all album cover for this playlist
    download_album_cover_art(sp, playlist_ids)

event = {
    "playlist_id": "1tzytA4QOHs4HYfIcOGsNV",
    "image_data": "lkjflsdkj",
    "access_token": "BQD01V7vAfYcKdhhrXjSLbKyr0yNmaI73BBeM0evBFxQu0RfmBY-6DieUcioS6UB_fLv6mekSkPlCs-wVbmIIDlMRJGLl3eDBMXR0LkI1DwvIRNFQkNMSTiOXJZfsOFCBbPWHh059UHxp-xfC2nDQTjz6e759ubhZpo6CaG_3u2TBZqR-Ui1HaGX"
}

context = {}

lambda_handler(event, context)
