import os, shutil, configparser, json, re, requests, csv, chardet, logging
from csv import excel_tab

default_path = os.path.abspath('C:\\Richard Burns Rally\\')
#favorites_dir_path = os.path.join(default_path, "rsfdata", "cache")
#favorite_path = os.path.join(default_path, "rsfdata", "cache", "favorites.ini")
favorite_prefix = "favorite_"
# stages_json = default_path + rsfdata + cache + "stages_data.json"
script_path = os.path.dirname(os.getcwd())
settings_file = os.path.join(script_path, "favorites_settings.ini")
ratings_file = os.path.join(script_path, "stage_ratings.csv")

logger = logging.getLogger(__name__)

class FavoriteMgr:
    def __init__(self, default=default_path):
        self.path = None
        self.favorite_path = None
        self.favorites_dir_path = None
        self.current_favorite_file = None
        self.stages_info_file = None
        self.stages = None

        # self.path = default
        # self.favorite_path = os.path.join(default, "rsfdata", "cache", "favorites.ini")
        # self.favorites_dir_path = os.path.join(default, "rsfdata", "cache")
        self.favorites = []
        self.cars = None
        self.all_maps = []
        self.all_existing_maps = []
        self.load_settings()
        # self.set_default_path(default)


    def load_settings(self):
        logger.info(f"Loading settings!")
        if os.path.isfile(settings_file):
            config = configparser.ConfigParser()
            config.read(settings_file)
            rbr_path = config["default"]["rbr_path"]
            if not self.set_default_path(rbr_path):
                logger.error(f"Error loading settings file")
            logger.info("Loaded rbr_path from settings")
            return rbr_path
        else:
            logger.info("No settings file!")
        return None

    def save_settings(self):
        logger.info("Saving settings")
        if self.path:
            config = configparser.ConfigParser()
            config["default"] = {}
            config["default"]["rbr_path"] = self.path
            with open(settings_file, 'w') as f:
                config.write(f)
            logger.info("Settings saved!")

    def set_default_path(self, rbr_path):
        logger.info(f"Setting default path to: {rbr_path}")
        if not os.path.isdir(os.path.join(rbr_path,"Maps")):
            # Probably not the RBR install folder
            logger.error("Maps subfolder not found! default path not set!")
            return False
        self.path = rbr_path
        self.favorite_path = os.path.join(self.path, "rsfdata", "cache", "favorites.ini")
        logger.debug(f"favorite_path: {self.favorite_path}")
        # self.favorites_dir_path = os.path.join(self.path, "rsfdata", "cache")
        self.favorites_dir_path = os.path.join(script_path, "favorites")
        logger.debug(f"favorites_dir_path: {self.favorites_dir_path}")
        self.stages_info_file = os.path.join(self.path, "rsfdata", "cache", "stages_data.json")
        logger.debug(f"stages_info_file: {self.stages_info_file}")
        try:
            os.mkdir(self.favorites_dir_path)
        except:
            # exception is raised if the dir exists
            pass
        self.load_maps()
        return True

    def load_favorite_files(self):
        """
        Search the favorites dir for favorite files
        :return:
        """
        logger.info("Loading favorite files")
        items = os.listdir(self.favorites_dir_path)
        favorites_list = []
        for item in items:
            if os.path.isfile(os.path.join(self.favorites_dir_path, item)) and favorite_prefix in item:
                logger.debug(f"Found favorite: {item}")
                favorites_list.append(item.split(".")[0].replace(favorite_prefix, ""))
        return favorites_list

    def load_favorite(self, fav_name, default=False):
        """
        Load a favorite file
        :param fav_name: the favorite file name
        :param default: if choosing the default favorites file
        :return:
        """
        try:
            logger.info(f"Loading favorite file: {fav_name} | default: {default}")
            config = configparser.ConfigParser()
            if default:
                config_path = self.favorite_path
            else:
                config_path = os.path.join(self.favorites_dir_path, favorite_prefix + fav_name + ".ini")
            logger.debug(f"Loading favorites from file: {config_path}")
            config.read(config_path)
            if default:
                logger.debug(f"Saving the cars!")
                # backup the car config only from the favorites, so we keep this info
                if "FavoriteCars" in config:
                    self.cars = config["FavoriteCars"]
            self.favorites = []
            for key in config["FavoriteStages"]:
                self.favorites.append(key)
            self.current_favorite_file = fav_name
        except Exception as err:
            logger.error(f"Error: {err}\nError loading favorite: {fav_name} | default: {default} | favorite_path: {self.favorite_path}")


    def get_current_favorite_stages(self):
        """
        Returns the current favorite stages as a list of stage objects
        :return:
        """
        logger.info("Getting current favorite stages")
        stages = []
        for fav_id in self.favorites:
            stage = self.get_stage_details(fav_id)
            if stage:
                stages.append(stage)
        return stages

    def save_favorite(self, fav_name, default=False):
        logger.info(f"Saving current favorites as: {fav_name} | default: {default}")
        config = configparser.ConfigParser()
        if self.cars:
            config["FavoriteCars"] = self.cars
        else:
            config["FavoriteCars"] = {}
        config["FavoriteStages"] = {}
        if default:
            self.backup_original()
            file_path = self.favorite_path
        else:
            file_path = os.path.join(self.favorites_dir_path, favorite_prefix + fav_name + ".ini")
        for fav in self.favorites:
            config["FavoriteStages"][fav] = "f"
        with open(file_path, "w") as f:
            config.write(f)
        return file_path

    def get_current_path(self):
        return self.path

    def backup_original(self):
        backup_path = os.path.join(self.favorites_dir_path, favorite_prefix + "original.ini")
        if not os.path.isfile(backup_path):
            logger.info("Backing up original favorites file")
            shutil.copy(self.favorite_path, backup_path)

    def load_maps(self):
        """
        retrieves all maps in the maps folder
        :return: list of map names
        """
        if len(self.all_maps) == 0:
            logger.info("Loading maps")
            self.all_maps = []
            if os.path.isdir(self.path):
                maps_dir = os.path.join(self.path, "Maps")
                for item in os.listdir(maps_dir):
                    if os.path.isdir(os.path.join(maps_dir, item)):
                        # maps.append(item)
                        if item not in self.all_maps:
                            self.all_maps.append(item)
        return self.all_maps

    def load_existing_maps(self):
        """
        retrieves all maps in the maps folder
        :return: list of map names
        """
        if len(self.all_existing_maps) == 0:
            logger.debug("Loading existing maps")
            self.all_existing_maps = []
            existing_map_ids = extract_existing_map_ids(os.path.join(self.path, "Maps"))
            for existing_map in existing_map_ids:
                self.all_existing_maps.append(int(existing_map))
        return self.all_existing_maps

    def add_favorite(self, fav_id):
        logger.info(f"Adding to favorites: {fav_id}")
        if str(fav_id) not in self.favorites:
            self.favorites.append(str(fav_id))

    def remove_favorite(self, fav_id):
        logger.info(f"Removing from favorites: {fav_id}")
        self.favorites.remove(str(fav_id))

    #TODO: REMOVE
    def get_favorites_names(self):
        names = []
        for map_name in self.all_maps:
            map_id = map_name.split("-")[0]
            if map_id in self.favorites:
                names.append(map_name)
        return names

    #TODO: REMOVE
    def search_maps(self, text):
        """
        Given the text, search for existing maps that contain the text
        :param text: search string
        :return: string list of all maps that contain the text
        """
        self.load_maps()
        maps = []
        for map_name in self.all_maps:
            if text.lower() in map_name.lower():
                maps.append(map_name)
        return maps

    def load_stages(self):
        """
        Loads the stages json file
        example format:
            "id": "525",
            "name": "Piren Tarmac",
            "deftime": "228",
            "length": "4424",
            "surface_id": "1",
            "stage_id": "525",
            "short_country": "SE",
            "author": "Mikael Jakobsson -Jacken-  (conversion by PeterB)",
            "tarmac": "100",
            "gravel": "0",
            "snow": "0",
            "new_update": "1",
            "author_web": "",
            "author_note": "",
            "fattrib": "241223"
        :return:
        """
        if self.stages is None:
            logger.info("Loading all stages")
            self.stages = []
            with open(self.stages_info_file, 'r') as f:
                temp_stages = json.loads(f.read())
                self.load_existing_maps()
                ratings = get_stages_ratings()
                for stage in temp_stages:
                    stage_copy = stage.copy()
                    sid = stage_copy['id']
                    if int(sid) in self.all_existing_maps:
                        stage_copy.update({"exists":True})
                    else:
                        stage_copy.update({"exists":False})
                    if sid in ratings:
                        stage_copy.update({'avg_rating':ratings[sid]})
                    else:
                        stage_copy.update({'avg_rating':0})
                    self.stages.append(stage_copy)
        return self.stages

    def get_stage_details(self, stage_id):
        """
        Fetches the details for the given stage id
        :param stage_id: the stage id
        :return: dict - stage details
        """
        logger.info(f"Getting stage details for: {stage_id}")
        self.load_stages()
        for stage in self.stages:
            if stage["id"] == stage_id:
                return stage
        return None

    def load_favorites_from_url(self, url):
        logger.info(f"Loading favorites from URL: {url}")
        stage_ids = get_stages_from_url(url)
        if stage_ids:
            self.favorites = stage_ids
            return True
        return False

#TODO: REMOVE
def get_map_details(map_name):
    try:
        map_id = map_name.split("-")[0]
        map_name = map_name.split("-")[1:]
        return {"id": map_id, "name": map_name}
    except Exception as err:
        print(f"Was not able to get map details from: {map_name}")
        return None

def extract_existing_map_ids(folder):
    """
    Traverse a folder and extract all ids found from the filenames
    :param filename:
    :param isdir:
    :return:
    """
    logger.info(f"Extracting existing maps from: {folder}")
    for item in os.listdir(folder):
        current_path = os.path.join(folder, item)
        if os.path.isdir(current_path):
            yield from extract_existing_map_ids(current_path)
        else:
            pattern = re.compile('track-(\d+).*?.ini')
            m = pattern.match(item)
            if m is not None:
                try:
                    stage_id = m.group(1)
                    yield stage_id
                except:
                    pass

def get_stages_ratings():
    """
    Returns the average rating from the ratings csv file
    :return:
    """
    logger.info("Getting stage ratings")
    ratings = {}
    try:
        encod = None
        with open(ratings_file, "rb") as file:
            encod = chardet.detect(file.read())  # Read a portion of the file
            logger.debug(f'ratings_file has encoding: {encod["encoding"]}')
        with open(ratings_file, 'r', encoding= encod['encoding'], errors="replace") as f:
            reader = csv.DictReader(f)
            for line in reader:
                sid = str(line['ID'])
                rating = line['Average Rating']
                ratings[sid] = float(rating)
    except Exception as err:
        logger.error(f"Error reading ratings file: {err}")
    return ratings

def get_stages_from_url(url):
    logger.info(f"Getting URL: {url}")
    response = requests.get(url)
    logger.debug(f"URL status code: {response.status_code}")
    stages = get_stages_from_page(response.text)
    return stages

def get_stages_from_page(page):
    logger.debug("Getting stages from page")
    result = []
    pattern = re.compile('ID: (\d+)')
    matches = re.findall(pattern, page)
    for match in matches:
        if match not in result:
            logger.debug(f"Found match: {match}")
            result.append(match)
    logger.debug(f"Found {len(result)} stages")
    return result