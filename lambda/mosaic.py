import sys
import os
from PIL import Image
from multiprocessing import Process, cpu_count, Pipe

# Change these 3 config parameters to suit your needs...
TILE_SIZE      = 50        # height/width of mosaic tiles in pixels
TILE_MATCH_RES = 5        # tile matching resolution (higher values give better fit but require more processing)
ENLARGEMENT    = 8        # the mosaic image will be this many times wider and taller than the original

TILE_BLOCK_SIZE = TILE_SIZE / max(min(TILE_MATCH_RES, TILE_SIZE), 1)
WORKER_COUNT = max(cpu_count() - 1, 1)
OUT_FILE = 'mosaic.jpeg'
EOQ_VALUE = None

class TileProcessor:
    def __init__(self, tiles_directory):
        self.tiles_directory = tiles_directory

    def __process_tile(self, tile_path):
        try:
            img = Image.open(tile_path)
            # tiles must be square, so get the largest square that fits inside the image
            w = img.size[0]
            h = img.size[1]
            min_dimension = min(w, h)
            w_crop = (w - min_dimension) / 2
            h_crop = (h - min_dimension) / 2
            img = img.crop((w_crop, h_crop, w - w_crop, h - h_crop))

            large_tile_img = img.resize((TILE_SIZE, TILE_SIZE), Image.ANTIALIAS)
            small_tile_img = img.resize((TILE_SIZE/TILE_BLOCK_SIZE, TILE_SIZE/TILE_BLOCK_SIZE), Image.ANTIALIAS)

            return (large_tile_img.convert('RGB'), small_tile_img.convert('RGB'))
        except:
            return (None, None)

    def get_tiles(self):
        large_tiles = []
        small_tiles = []

        print 'Reading tiles from \'%s\'...' % (self.tiles_directory, )

        # search the tiles directory recursively
        for root, subFolders, files in os.walk(self.tiles_directory):
            for tile_name in files:
                tile_path = os.path.join(root, tile_name)
                large_tile, small_tile = self.__process_tile(tile_path)
                if large_tile:
                    large_tiles.append(large_tile)
                    small_tiles.append(small_tile)
        
        print 'Processed %s tiles.' % (len(large_tiles),)

        return (large_tiles, small_tiles)

class TargetImage:
    def __init__(self, image_path):
        self.image_path = image_path

    def get_data(self):
        print 'Processing main image...'
        img = Image.open(self.image_path)
        w = img.size[0] * ENLARGEMENT
        h = img.size[1]    * ENLARGEMENT
        large_img = img.resize((w, h), Image.ANTIALIAS)
        w_diff = (w % TILE_SIZE)/2
        h_diff = (h % TILE_SIZE)/2
        
        # if necesary, crop the image slightly so we use a whole number of tiles horizontally and vertically
        if w_diff or h_diff:
            large_img = large_img.crop((w_diff, h_diff, w - w_diff, h - h_diff))

        small_img = large_img.resize((w/TILE_BLOCK_SIZE, h/TILE_BLOCK_SIZE), Image.ANTIALIAS)

        image_data = (large_img.convert('RGB'), small_img.convert('RGB'))

        print 'Main image processed.'

        return image_data

class TileFitter:
    def __init__(self, tiles_data):
        self.tiles_data = tiles_data

    def __get_tile_diff(self, t1, t2, bail_out_value):
        diff = 0
        for i in range(len(t1)):
            #diff += (abs(t1[i][0] - t2[i][0]) + abs(t1[i][1] - t2[i][1]) + abs(t1[i][2] - t2[i][2]))
            diff += ((t1[i][0] - t2[i][0])**2 + (t1[i][1] - t2[i][1])**2 + (t1[i][2] - t2[i][2])**2)
            if diff > bail_out_value:
                # we know already that this isnt going to be the best fit, so no point continuing with this tile
                return diff
        return diff

    def get_best_fit_tile(self, img_data):
        best_fit_tile_index = None
        min_diff = sys.maxint
        tile_index = 0

        # go through each tile in turn looking for the best match for the part of the image represented by 'img_data'
        for tile_data in self.tiles_data:
            diff = self.__get_tile_diff(img_data, tile_data, min_diff)
            if diff < min_diff:
                min_diff = diff
                best_fit_tile_index = tile_index
            tile_index += 1

        return best_fit_tile_index

def fit_tiles(row_start, row_end, x_tile_count, tiles_data, original_img_small, conn):
    # this function gets run by the worker processes, one on each CPU core
    tile_fitter = TileFitter(tiles_data)

    coords_list = []

    for x in range(x_tile_count):
        for y in range(row_start, row_end):
            large_box = (x * TILE_SIZE, y * TILE_SIZE, (x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE)
            small_box = (x * TILE_SIZE/TILE_BLOCK_SIZE, y * TILE_SIZE/TILE_BLOCK_SIZE, (x + 1) * TILE_SIZE/TILE_BLOCK_SIZE, (y + 1) * TILE_SIZE/TILE_BLOCK_SIZE)
            img_data = list(original_img_small.crop(small_box).getdata())
            img_coords = large_box
            tile_index = tile_fitter.get_best_fit_tile(img_data)
            coords_list.append((img_coords, tile_index))

    print("I'm finished")
    conn.send(coords_list)
    print("sent data")
    conn.close()
    print("closed connection")

class ProgressCounter:
    def __init__(self, total):
        self.total = total
        self.counter = 0

    def update(self):
        self.counter += 1
        sys.stdout.write("Progress: %s%% %s" % (100 * self.counter / self.total, "\r"))
        sys.stdout.flush();

class MosaicImage:
    def __init__(self, original_img):
        self.image = Image.new(original_img.mode, original_img.size)
        self.x_tile_count = original_img.size[0] / TILE_SIZE
        self.y_tile_count = original_img.size[1] / TILE_SIZE
        self.total_tiles  = self.x_tile_count * self.y_tile_count

    def add_tile(self, tile_data, coords):
        img = Image.new('RGB', (TILE_SIZE, TILE_SIZE))
        img.putdata(tile_data)
        self.image.paste(img, coords)

    def save(self, path):
        self.image.save(path)

def compose(original_img, tiles, tiles_path):
    print 'Building mosaic, press Ctrl-C to abort...'
    print('number of workers: ', WORKER_COUNT)
    original_img_large, original_img_small = original_img
    tiles_large, tiles_small = tiles

    mosaic = MosaicImage(original_img_large)

    all_tile_data_large = map(lambda tile : list(tile.getdata()), tiles_large)
    all_tile_data_small = map(lambda tile : list(tile.getdata()), tiles_small)

    # create a list to keep all processes
    processes = []

    # create a process per instance
    parent_connections = []

    num_rows = mosaic.y_tile_count / WORKER_COUNT

    try:
        for p in range(WORKER_COUNT):
            # create a pipe for communication
            parent_conn, child_conn = Pipe()
            parent_connections.append(parent_conn)

            # determine which tiles this process will work on
            start_row = p * num_rows
            end_row = min(start_row + num_rows, mosaic.y_tile_count)

            # create the process, pass instance and connection
            process = Process(target=fit_tiles, args=(start_row, end_row, mosaic.x_tile_count, all_tile_data_small, original_img_small, child_conn))
            processes.append(process)

        # start all processes
        for process in processes:
            process.start()

        # assemble final image
        for parent_connection in parent_connections:
            data = parent_connection.recv()
            for img_coords, best_fit_tile_index in data:
                tile_data = all_tile_data_large[best_fit_tile_index]
                mosaic.add_tile(tile_data, img_coords)

        # make sure that all processes have finished
        for process in processes:
            process.join()

    except KeyboardInterrupt:
        print '\nHalting, saving partial image please wait...'

    finally:
        image_path = os.path.join(tiles_path, OUT_FILE)
        print 'Writing file to ', image_path

        mosaic.save(image_path)
        print '\nFinished, output is in', image_path

        return image_path


def mosaic(img_path, tiles_path):
    tiles_data = TileProcessor(tiles_path).get_tiles()
    image_data = TargetImage(img_path).get_data()
    return compose(image_data, tiles_data, tiles_path)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: %s <image> <tiles directory>\r' % (sys.argv[0],)
    else:
        mosaic(sys.argv[1], sys.argv[2])

