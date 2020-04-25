import json
import spotipy
import tempfile
from urllib import urlretrieve
import multiprocessing
from os import listdir, path, rename, path, environ
import shutil
from mosaic import mosaic
import base64
import boto3
from collections import Counter 

def download_album_cover_func(image, directory):
    file_name = image[0]
    file_path = path.join(directory, file_name)
    urlretrieve(image[1], file_path)

def get_album_ids(sp, playlist_id):
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

def download_album_cover_art(sp, album_ids, temp_dir):
    processes = []
    album_ids = list(album_ids)

    for i in range(0, len(album_ids), 20):
        albums = sp.albums(album_ids[i:i+20])
        image_info = [(album["name"], album["images"][0]["url"]) for album in albums["albums"]]

        # for each image URL, instantiate a process to download
        for image in image_info:
            p = multiprocessing.Process(target=download_album_cover_func, args=(image, temp_dir))
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

def get_image_from_s3(DEV, image_key):
    INPUT_IMAGE = '/tmp/input_image.jpg'

    client = boto3.resource('s3')
    bucket_path = 'musaic-dev' if DEV else 'musaic'
    bucket = client.Bucket(bucket_path)
    with open(INPUT_IMAGE, 'wb') as f:
        bucket.download_fileobj("uploads/{}".format(image_key), f)

    return INPUT_IMAGE

def save_image_to_s3(DEV, image_path, image_key):
    client = boto3.resource('s3')
    bucket_path = 'musaic-dev' if DEV else 'musaic'
    bucket = client.Bucket(bucket_path)
    bucket.upload_file(image_path, image_key)

    OBJECT_URL = "https://{}.s3-us-west-1.amazonaws.com/{}"
    return OBJECT_URL.format(bucket_path, image_key)

def lambda_handler(event, context):
    # get correct env
    try:
        playlist_id = event["playlist_id"]
        file_name = event["file_name"]
        access_token = event["access_token"]
        DEV = event.get("dev", False)

        # Create a spotify client to access their playlists
        sp = spotipy.Spotify(auth=access_token)
        
        # get all unique album ids 
        album_ids = get_album_ids(sp, playlist_id)

        # download album cover
        album_covers_dir = tempfile.mkdtemp()
        download_album_cover_art(sp, album_ids, album_covers_dir)

        # fetch image stored in s3
        input_image_path = get_image_from_s3(DEV, file_name)

        # generate mosaic
        output_image_path, counts = mosaic(input_image_path, album_covers_dir)

        counter = Counter(counts)

        # save generated image to s3
        output_image_key = "generated/{}".format(file_name)
        object_url = save_image_to_s3(DEV, output_image_path, output_image_key)

        # clean up
        shutil.rmtree(album_covers_dir)

        return {
            "statusCode": 200,
            "body": {
                "object_url": object_url,
                "counts": json.loads(json.dumps(counter.most_common(5)))
            }
        }

    except Exception as e:
        # Log the error to cloudwatch
        print(e)
        
        return {
            "statusCode": 400
        }


if __name__ == '__main__':
    event = {
        "playlist_id": "1tzytA4QOHs4HYfIcOGsNV",
        "file_name": "photo.jpg",
        "access_token": "BQD8D0f_ljx-CK4eGCJzY0fQOmFKW8E6M_fhWoX-sW3S9y8h8DDANTAIGFuZ7A3isSvKl1eTzkz1uXa7Y4Y-aVgGjFx82B0SRhxL4Yn--dhcrL27zNTdmyMf3tZeV07krBe_z-Lg3SoIJBwsXRXhQLLSb6YfoA-sze8t3ERg0RqMtl2Y-urIvA"
    }
    context = "context"
    lambda_handler(event, context)
