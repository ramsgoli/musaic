from collections import defaultdict
import spotipy
import tempfile
from urllib import urlretrieve
import multiprocessing
from os import listdir, path, rename, path, environ
import shutil
from mosaic import MusaicHandler, TileProcessor, TargetImage
import boto3
from collections import Counter


class LambdaHandler:
    def __init__(self, event):
        self.playlist_id = event["playlist_id"]
        self.file_name = event["file_name"]
        self.access_token = event["access_token"]
        self.is_dev = event.get("dev", False)
        self.album_info = defaultdict()
        self.is_stock = False

        if self.file_name.startswith("preloaded"):
            self.is_stock = True
            self.file_name = "/".join(self.file_name.split('/')[1:])

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
        musaic_handler = MusaicHandler(image_data, tiles_data, album_covers_dir)
        output_image_path = musaic_handler.compose(self.album_info)

        # save generated image to s3
        output_image_key = "generated/{}".format(self.file_name)
        object_url = self.save_image_to_s3(output_image_path, output_image_key)

        # clean up
        shutil.rmtree(album_covers_dir)

        sorted_album_ids_by_counts = sorted(self.album_info, key=lambda x: self.album_info[x]['count'], reverse=True)
        top_albums = {album_id: self.album_info[album_id] for album_id in sorted_album_ids_by_counts[:5]}

        return {
            "statusCode": 200,
            "body": {
                "object_url": object_url,
                "top_albums": top_albums
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
                file_name = image[0]
                file_url = image[1]
                album_id = file_url.split("/")[-1]

                # set album info in self.album_info
                self.album_info[album_id] = {
                    'count': 0,
                    'url': file_url,
                    'name': file_name
                }

                p = multiprocessing.Process(target=self.download_album_cover_func, args=(file_url, album_id, temp_dir))
                processes.append(p)
                p.start()

        # wait for all images to finish downloading
        for process in processes:
            process.join()

        print "Finished downloading all files"

    def download_album_cover_func(self, file_url, album_id, directory):
        file_path = path.join(directory, album_id)
        urlretrieve(file_url, file_path)


    def get_image_from_s3(self):
        INPUT_IMAGE = '/tmp/input_image.jpg'

        client = boto3.resource('s3')
        bucket_path = 'musaic-dev' if self.is_dev else 'musaic'
        bucket = client.Bucket(bucket_path)
        with open(INPUT_IMAGE, 'wb') as f:
            if self.is_stock:
                file_name = self.file_name.split('/')[-1]
                bucket.download_fileobj("preloaded/{}".format(file_name), f)
            else:
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
    handler = LambdaHandler(event)
    return handler.create_musaic()
