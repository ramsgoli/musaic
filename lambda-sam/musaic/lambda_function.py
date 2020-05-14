import spotipy
import tempfile
from urllib import urlretrieve
import multiprocessing
from os import listdir, path, rename, path, environ
import shutil
from mosaic import compose, TileProcessor, TargetImage
import boto3
from collections import Counter


class LambdaHandler:
    def __init__(self, event):
        self.playlist_id = event["playlist_id"]
        self.file_name = event["file_name"]
        self.access_token = event["access_token"]
        self.is_dev = event.get("dev", False)

    def create_musaic(self):
        self.sp = spotipy.Spotify(auth=self.access_token)

        # get all unique album ids
        album_ids = self.get_album_ids()

        # download album cover
        album_covers_dir = tempfile.mkdtemp()
        self.download_album_cover_art(album_ids, album_covers_dir)

        # fetch image stored in s3
        input_image_path = self.get_image_from_s3()

        # generate mosaic
        tiles_data = TileProcessor(album_covers_dir).get_tiles()
        image_data = TargetImage(input_image_path).get_data()
        output_image_path, counts = compose(image_data, tiles_data, album_covers_dir)

        self.counter = Counter(counts)

        # save generated image to s3
        output_image_key = "generated/{}".format(self.file_name)
        self.object_url = self.save_image_to_s3(output_image_path, output_image_key)

        # clean up
        shutil.rmtree(album_covers_dir)

    def response(self):
        return {
            "statusCode": 200,
            "body": {
                "object_url": self.object_url,
                "counts": self.counter.most_common(5)
            }
        }

    def get_album_ids(self):
        user_id = self.sp.me()["id"]
        fields = "items(track(album(id))),next"
        data = self.sp.user_playlist_tracks(user_id, playlist_id=self.playlist_id, fields=fields)
        ids = set([item["track"]["album"]["id"] for item in data["items"] if item["track"]["album"]["id"]])

        while data["next"]:
            data = self.sp.next(data)
            for item in data["items"]:
                if item["track"]["album"]["id"]:
                    ids.add(item["track"]["album"]["id"])

        return ids

    def download_album_cover_art(self, album_ids, temp_dir):
        processes = []
        album_ids = list(album_ids)

        for i in range(0, len(album_ids), 20):
            albums = self.sp.albums(album_ids[i:i+20])
            image_info = [(album["name"], album["images"][0]["url"]) for album in albums["albums"]]

            # for each image URL, instantiate a process to download
            for image in image_info:
                p = multiprocessing.Process(target=self.download_album_cover_func, args=(image, temp_dir))
                processes.append(p)
                p.start()

        # wait for all images to finish downloading
        for process in processes:
            process.join()

        print "Finished downloading all files"

    def download_album_cover_func(self, image, directory):
        file_name = image[0]
        file_path = path.join(directory, file_name)
        urlretrieve(image[1], file_path)

    def get_image_from_s3(self):
        INPUT_IMAGE = '/tmp/input_image.jpg'

        client = boto3.resource('s3')
        bucket_path = 'musaic-dev' if self.is_dev else 'musaic'
        bucket = client.Bucket(bucket_path)
        with open(INPUT_IMAGE, 'wb') as f:
            bucket.download_fileobj("uploads/{}".format(self.file_name), f)

        return INPUT_IMAGE

    def save_image_to_s3(self, image_path, image_key):
        client = boto3.resource('s3')
        bucket_path = 'musaic-dev' if self.is_dev else 'musaic'
        bucket = client.Bucket(bucket_path)
        bucket.upload_file(image_path, image_key)

        OBJECT_URL = "https://{}.s3-us-west-1.amazonaws.com/{}"
        return OBJECT_URL.format(bucket_path, image_key)


def lambda_handler(event, context):
    lambda_handler = LambdaHandler(event)
    lambda_handler.create_musaic()

    return lambda_handler.response()
