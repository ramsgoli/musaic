import json
import spotipy
import tempfile
from urllib import urlretrieve
import multiprocessing
from os import listdir, path, rename, path
import shutil
from mosaic import mosaic
import base64
import boto3

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

def download_album_cover_art(sp, playlist_ids, temp_dir):

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


def write_photo_data_to_file(file_data, temp_dir):
    file_path = path.join(temp_dir, "input_image.jpeg")
    fh = open(file_path, "wb")
    fh.write(file_data.decode('base64'))
    fh.close()

    return file_path

def get_image_from_s3(image_key):
    INPUT_IMAGE = 'input_image.jpg'

    client = boto3.resource('s3')
    bucket = client.Bucket('musaic')
    with open(INPUT_IMAGE, 'wb') as f:
        bucket.download_fileobj(image_key, f)

    return INPUT_IMAGE

def lambda_handler(event, context):
    playlist_id = event["playlist_id"]
    file_name = event["file_name"]
    access_token = event["access_token"]

    sp = spotipy.Spotify(auth=access_token)
    
    # get all unique album ids 
    playlist_ids = get_playlist_ids(sp, playlist_id)

    # download album cover
    temp_dir = tempfile.mkdtemp()
    download_album_cover_art(sp, playlist_ids, temp_dir)

    # fetch image stored in s3
    image_path = get_image_from_s3(file_name)

    # generate mosaic
    mosaic(image_path, temp_dir)

    # Convert image into utf-8 encoded base64
    with open(path.join(temp_dir, "mosaic.jpeg"), "rb") as imageFile:
      str = base64.b64encode(imageFile.read())
      encoded_img = str.decode("utf-8")

    print(encoded_img)
    # clean up
    #shutil.rmtree(temp_dir)

    return {
	"isBase64Encoded": True,
	"statusCode": 200,
	"headers": { "content-type": "image/jpeg"},
    }

if __name__ == '__main__':
    event = {
        "playlist_id": "1tzytA4QOHs4HYfIcOGsNV",
        "file_name": "photo.jpg",
        "access_token": "BQDjVaNEhOhqHHWAvLUcz81RGgDJBBIy85iCD5A8WBQ173UP_OS2Shr1H-3VEpldzvorx6-5TUUAs6ZUisrfQo4sWvVd2zeRdYq1SPt-CHVkpzOWR1cgb0l7NcKeaUh8TRJAEdqVW9bxTCalXmuvOcK9vcQJxXN9xAES7tNOh_kPYM9QVDhALA"
    }
    context = "context"
    lambda_handler(event, context)
