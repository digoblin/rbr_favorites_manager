import os, shutil, configparser, json, re
from csv import excel_tab

default_path = os.path.abspath('C:\\Richard Burns Rally\\')
#favorites_dir_path = os.path.join(default_path, "rsfdata", "cache")
#favorite_path = os.path.join(default_path, "rsfdata", "cache", "favorites.ini")
favorite_prefix = "favorite_"
# stages_json = default_path + rsfdata + cache + "stages_data.json"
script_path = os.path.dirname(os.path.realpath(__file__))
settings_file = os.path.join(script_path, "favorites_settings.ini")


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
        if os.path.isfile(settings_file):
            config = configparser.ConfigParser()
            config.read(settings_file)
            rbr_path = config["default"]["rbr_path"]
            if not self.set_default_path(rbr_path):
                print("Error loading settings file")
            print("Loaded rbr_path from settings")
            return rbr_path
        return None

    def save_settings(self):
        if self.path:
            config = configparser.ConfigParser()
            config["default"] = {}
            config["default"]["rbr_path"] = self.path
            with open(settings_file, 'w') as f:
                config.write(f)
            print("Settings saved!")

    def set_default_path(self, rbr_path):
        if not os.path.isdir(os.path.join(rbr_path,"Maps")):
            # Probably not the RBR install folder
            return False
        self.path = rbr_path
        self.favorite_path = os.path.join(self.path, "rsfdata", "cache", "favorites.ini")
        # self.favorites_dir_path = os.path.join(self.path, "rsfdata", "cache")
        self.favorites_dir_path = os.path.join(script_path, "favorites")
        self.stages_info_file = os.path.join(self.path, "rsfdata", "cache", "stages_data.json")
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
        items = os.listdir(os.path.join(self.favorites_dir_path))
        favorites_list = []
        for item in items:
            if os.path.isfile(os.path.join(self.favorites_dir_path, item)) and favorite_prefix in item:
                favorites_list.append(item.split(".")[0].replace(favorite_prefix, ""))
        return favorites_list

    def load_favorite(self, fav_name, default=False):
        """
        Load a favorite file
        :param fav_name: the favorite file name
        :param default: if choosing the default favorites file
        :return:
        """
        config = configparser.ConfigParser()
        if default:
            config_path = self.favorite_path
        else:
            config_path = os.path.join(self.favorites_dir_path, favorite_prefix + fav_name + ".ini")
        config.read(config_path)
        if default:
            # backup the car config only from the favorites, so we keep this info
            self.cars = config["FavoriteCars"]
        self.favorites = []
        for key in config["FavoriteStages"]:
            self.favorites.append(key)
        self.current_favorite_file = fav_name

    def get_current_favorite_stages(self):
        """
        Returns the current favorite stages as a list of stage objects
        :return:
        """
        stages = []
        for fav_id in self.favorites:
            stage = self.get_stage_details(fav_id)
            if stage:
                stages.append(stage)
        return stages

    def save_favorite(self, fav_name, default=False):
        config = configparser.ConfigParser()
        config["FavoriteCars"] = self.cars
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
            shutil.copy(self.favorite_path, backup_path)

    def load_maps(self):
        """
        retrieves all maps in the maps folder
        :return: list of map names
        """
        if len(self.all_maps) == 0:
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
            self.all_existing_maps = []
            existing_map_ids = extract_existing_map_ids(os.path.join(self.path, "Maps"))
            for existing_map in existing_map_ids:
                self.all_existing_maps.append(int(existing_map))
        return self.all_existing_maps

    def add_favorite(self, fav_id):
        if str(fav_id) not in self.favorites:
            self.favorites.append(str(fav_id))

    def remove_favorite(self, fav_id):
        self.favorites.remove(str(fav_id))

    def get_favorites_names(self):
        names = []
        for map_name in self.all_maps:
            map_id = map_name.split("-")[0]
            if map_id in self.favorites:
                names.append(map_name)
        return names

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
            self.stages = []
            with open(self.stages_info_file, 'r') as f:
                temp_stages = json.loads(f.read())
                self.load_existing_maps()
                for stage in temp_stages:
                    stage_copy = stage.copy()
                    if int(stage_copy["id"]) in self.all_existing_maps:
                        stage_copy.update({"exists":True})
                    else:
                        stage_copy.update({"exists":False})
                    self.stages.append(stage_copy)
        return self.stages

    def get_stage_details(self, stage_id):
        """
        Fetches the details for the given stage id
        :param stage_id: the stage id
        :return: dict - stage details
        """
        self.load_stages()
        for stage in self.stages:
            if stage["id"] == stage_id:
                return stage
        return None




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