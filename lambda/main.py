import json
import spotipy
import tempfile
from urllib import urlretrieve
import multiprocessing
from os import listdir, path, rename
import shutil
from mosaic import mosaic

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

def download_album_cover_art(sp, playlist_ids, image_path, temp_dir):

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

    print "Finished downloading all files"

    # generate mosaic
    mosaic(image_path, temp_dir)

    # move output file
    rename(path.join(temp_dir, "mosaic.jpeg"), "/Users/ramsgoli/output.jpeg")


def lambda_handler(event, context):
    playlist_id = event["playlist_id"]
    image_data = event["image_data"]
    access_token = event["access_token"]

    # get all album covers in this playlist id
    sp = spotipy.Spotify(auth=access_token)
    
    # get all unique album ideas 
    playlist_ids = get_playlist_ids(sp, playlist_id)

    # download all album cover for this playlist
    temp_dir = tempfile.mkdtemp()
    download_album_cover_art(sp, playlist_ids, image_data, temp_dir)

    with open(path.join(temp_dir, "mosaic.jpeg"), "rb") as imageFile:
	str_data = base64.b64encode(imageFile.read())
	encoded_img = str_data.decode("utf-8")

    # clean up
    shutil.rmtree(temp_dir)

    return {
	"isBase64Encoded": True,
	"statusCode": 200,
	"headers": { "content-type": "image/jpeg"},
	"body":  encoded_img
    }

