import sys, logging, argparse, os
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtWidgets import QFileDialog, QFrame, QHeaderView, QApplication, QHBoxLayout, QWidget, QVBoxLayout, \
    QListWidget, QPushButton, QLabel, QLineEdit, QStatusBar, QMainWindow, QTableWidget, QTableWidgetItem, QGridLayout, \
    QSizePolicy, QTableView, QComboBox, QMessageBox
from PyQt6.QtGui import QFont, QIcon

import favorite_api
# from PySide6 import QtCore, QtWidgets, QtGui
import favorite_api as fav

logger = None
icon_name = "rbr_icon.ico"
# Try to find the icon, check also the _internal folder
if not os.path.isfile(icon_name):
    internal_path = os.path.join("_internal", icon_name)
    if os.path.isfile(internal_path):
        icon_name = internal_path


class StageTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        if len(self._data) > 0:
            return len(self._data)
        else:
            return 0

    def columnCount(self, index):
        if len(self._data) > 0:
            return len(self._data[0])
        else:
            return 0

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                if section == 0:
                    return "ID"
                elif section == 1:
                    return "Name"
                elif section == 2:
                    return "Surface"
                elif section == 3:
                    return "Length"
                elif section == 4:
                    return "Country"
                elif section == 5:
                    return "Author"
                elif section == 6:
                    return "New"
                elif section == 7:
                    return "Installed"
                elif section == 8:
                    return "Avg. Rating"


class StagesFilterProxyModel(QSortFilterProxyModel):

    stage_length_filter_values = ["Length", "0-3", "3-6", "6-9", "9-12", "12+"]
    stage_rating_filter_values = ["Rating", "0-1", "1-2", "2-3", "3-4", "4-5"]

    def __init__(self):
        super().__init__()
        self.filter_surface = ""
        self.filter_country = ""
        self.filter_text = ""
        self.filter_length = ""
        self.filter_installed = ""
        self.filter_new = ""
        self.filter_rating = ""

    def setFilterSurface(self, surface):
        logger.debug(f"Setting surface filter to: {surface}")
        self.filter_surface = surface
        self.invalidateFilter()  # Triggers a refresh of the filtering

    def setFilterCountry(self, country):
        logger.debug(f"Setting country filter to: {country}")
        self.filter_country = country
        self.invalidateFilter()  # Triggers a refresh of the filtering

    def setFilterNameOrID(self, text):
        logger.debug(f"Setting NameOrId filter to: {text}")
        self.filter_text = text
        self.invalidateFilter()  # Triggers a refresh of the filtering

    def setFilterLength(self, index):
        logger.debug(f"Setting length filter to: {index}")
        self.filter_length = index
        self.invalidateFilter()  # Triggers a refresh of the filtering

    def setFilterInstalled(self, text):
        logger.debug(f"Setting installed filter to: {text}")
        self.filter_installed = text
        self.invalidateFilter()  # Triggers a refresh of the filtering

    def setFilterNew(self, text):
        logger.debug(f"Setting new filter to: {text}")
        self.filter_new = text
        self.invalidateFilter()  # Triggers a refresh of the filtering

    def setFilterRating(self, index):
        logger.debug(f"Setting rating filter to: {index}")
        self.filter_rating = index
        self.invalidateFilter()  # Triggers a refresh of the filtering


    def filterAcceptsRow(self, sourceRow, sourceParent):
        model = self.sourceModel()
        acceptable = True
        if self.filter_surface and self.filter_surface != "Surface":
            index = model.index(sourceRow, 2)  # Filtering based on column 2 (Surface)
            acceptable = acceptable & (model.data(index) == self.filter_surface)
        if self.filter_country and self.filter_country != "Country":
            index = model.index(sourceRow, 4)  # Filtering based on column 4 (Country)
            acceptable = acceptable & (model.data(index) == self.filter_country)
        if self.filter_text:
            index1 = model.index(sourceRow, 0)  # Filtering based on column 0 (ID)
            index2 = model.index(sourceRow, 1)  # Filtering based on column 1 (Name)
            id_check = self.filter_text.lower() in str(model.data(index1))
            name_check = self.filter_text.lower() in model.data(index2).lower()
            acceptable = acceptable & (id_check | name_check)
        if self.filter_length and self.filter_length != 0:
            index = model.index(sourceRow, 3)  # Filtering based on column 3 (Length)
            result = False
            length_value = model.data(index)
            if self.filter_length == 1:
                # between 0 and 3
                result = (length_value > 0 and length_value <= 3)
            if self.filter_length == 2:
                # between 3 and 6
                result = (length_value > 3 and length_value <= 6)
            if self.filter_length == 3:
                # between 6 and 9
                result = (length_value > 6 and length_value <= 9)
            if self.filter_length == 4:
                # between 9 and 12
                result = (length_value > 9 and length_value <= 12)
            if self.filter_length == 5:
                # between 12+
                result = (length_value > 12)
            acceptable = acceptable & result
        if self.filter_installed and self.filter_installed != "Installed":
            index = model.index(sourceRow, 7)  # Filtering based on column 7 (Installed)
            acceptable = acceptable & (self.filter_installed == model.data(index))
        if self.filter_new and self.filter_new != "New":
            index = model.index(sourceRow, 6)  # Filtering based on column 7 (Installed)
            acceptable = acceptable & (self.filter_new == model.data(index))
        if self.filter_rating and self.filter_rating != 0:
            index = model.index(sourceRow, 8)  # Filtering based on column 8 (Rating)
            result = False
            rating_value = model.data(index)
            if self.filter_rating == 1:
                # between 0 and 1
                result = (rating_value > 0 and rating_value <= 1)
            if self.filter_rating == 2:
                # between 1 and 2
                result = (rating_value > 1 and rating_value <= 2)
            if self.filter_rating == 3:
                # between 2 and 3
                result = (rating_value > 2 and rating_value <= 3)
            if self.filter_rating == 4:
                # between 3 and 4
                result = (rating_value > 3 and rating_value <= 4)
            if self.filter_rating == 5:
                # between 4 and 5
                result = (rating_value > 4 and rating_value <= 5)
            acceptable = acceptable & result
        return acceptable



def convert_stages_to_model_data(stages):
    """
    Create a 2d array with the stages
    :param stages:
    :return:
    """
    converted = []
    for stage in stages:
        surface = "Gravel"
        if stage["surface_id"] == "1":
            surface = "Tarmac"
        elif stage["surface_id"] == "3":
            surface = "Snow"
        stage_length_km = round(int(stage["length"])/1000, 1)
        item_new = ("Yes" if stage["new_update"] == "1" else "No")
        item_exists = ("Yes" if stage["exists"] == True else "No")
        converted.append([int(stage["id"]), stage["name"], surface, stage_length_km, stage["short_country"], stage["author"], item_new, item_exists, stage['avg_rating']])
    return converted

class ListBoxExample(QWidget):
    def __init__(self):
        super().__init__()

        # INIT
        self.setWindowIcon(QIcon(icon_name))
        self.stage_data = None
        self.proxy_model = None

        # INIT GUI

        self.sort_order = None
        self.setWindowTitle("RBR favorites manager")
        self.setGeometry(100, 100, 600, 600)

        layout = QGridLayout()

        # Labels
        self.map_list_lbl = QLabel("Maps")
        self.fav_list_lbl = QLabel("Chosen favorites")
        self.rbr_folder_lbl = QLabel("RBR install folder")
        self.all_favs_lbl = QLabel("Favorites files")

        # QListWidgets
        # Map list
        self.map_list_widget = QListWidget()

        # Tables
        # self.maps_table = QTableWidget()
        # self.maps_table.setMinimumHeight(200)
        # self.maps_table.horizontalHeader().sectionClicked.connect(self.table_item_clicked)


        # Create QListWidget (ListBox)
        self.favs_list_widget = QListWidget()

        self.fav_files_list_widget = QListWidget()

        # Buttons
        self.add_fav_button = QPushButton(">")
        self.add_fav_button.clicked.connect(self.add_to_favorites)
        self.remove_fav_button = QPushButton("<")
        self.remove_fav_button.clicked.connect(self.remove_from_favorites)
        self.save_as_button = QPushButton("Save favorites As")
        self.save_as_button.clicked.connect(self.save_as_favorites)
        self.save_rbr_folder_button = QPushButton("Set RBR install folder")
        self.save_rbr_folder_button.clicked.connect(self.set_rbr_folder)
        self.load_favorite_button = QPushButton("Load favorite")
        self.load_favorite_button.clicked.connect(self.load_favorite_file)
        self.set_default_fav_button = QPushButton("Use selected favorites!")
        self.set_default_fav_button.clicked.connect(self.set_default_favs)
        self.show_file_dialog_button = QPushButton("Select folder")
        self.show_file_dialog_button.clicked.connect(self.show_file_dialog)
        self.load_url_button = QPushButton("Load stages from URL")
        self.load_url_button.clicked.connect(self.load_favorites_from_url)

        # Dialog
        self.file_dialog = QFileDialog()
        self.file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        self.file_dialog.setDirectory("C:\\")


        # Line Edits
        self.search_box = QLineEdit()
        self.search_box.setMaxLength(10)
        self.search_box.setPlaceholderText("Search Maps")
        self.save_as_line = QLineEdit()
        self.save_as_line.setPlaceholderText("Save As")
        self.rbr_folder_line = QLineEdit()
        self.rbr_folder_line.setPlaceholderText("RBR install folder")
        self.url_load_favorites_line = QLineEdit()
        self.url_load_favorites_line.setPlaceholderText("Load favorites from URL")


        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")

        #TableView

        self.maps_tableview = QTableView()
        self.maps_tableview.setSortingEnabled(True)
        self.favs_tableview = QTableView()
        self.favs_tableview.setSortingEnabled(True)

        rbr_folder_hlayout = QHBoxLayout()
        rbr_folder_hlayout.addWidget(self.rbr_folder_lbl)
        rbr_folder_hlayout.addWidget(self.rbr_folder_line)
        self.show_file_dialog_button.setMinimumHeight(30)
        self.show_file_dialog_button.setMinimumWidth(100)
        rbr_folder_hlayout.addWidget(self.show_file_dialog_button)

        fav_files_layout = QHBoxLayout()
        fav_files_layout.setSpacing(10)
        self.fav_files_list_widget.setMaximumHeight(100)
        self.load_favorite_button.setMinimumWidth(200)
        self.load_favorite_button.setMinimumHeight(50)
        fav_files_layout.addWidget(self.fav_files_list_widget)
        fav_files_layout.addWidget(self.load_favorite_button)



        layout.addLayout(rbr_folder_hlayout,1,0,1,3)
        self.save_rbr_folder_button.setMinimumHeight(30)
        layout.addWidget(self.save_rbr_folder_button,2,0,1,3)

        sep1 = QLabel()
        sep1.setFrameStyle(QFrame.Shape.HLine)
        sep1.setLineWidth(2)
        layout.addWidget(sep1,3,0,1,3)

        layout.addWidget(self.all_favs_lbl,4,0)
        layout.addLayout(fav_files_layout,5,0,1,3)

        sep2 = QLabel()
        sep2.setFrameStyle(QFrame.Shape.HLine)
        sep2.setLineWidth(2)
        layout.addWidget(sep2,6,0,1,3)

        layout.addWidget(self.search_box,7,0)
        fav_buttons_layout = QVBoxLayout()
        self.add_fav_button.setMinimumHeight(40)
        self.remove_fav_button.setMinimumHeight(40)
        fav_buttons_layout.addWidget(self.add_fav_button)
        fav_buttons_layout.addWidget(self.remove_fav_button)

        layout.addWidget(self.map_list_lbl,8,0,alignment=Qt.AlignmentFlag.AlignCenter)

        # Filters

        filters_layout = QHBoxLayout()
        self.surface_filter = QComboBox()
        self.surface_filter.addItem("Surface")
        self.surface_filter.addItem("Tarmac")
        self.surface_filter.addItem("Gravel")
        self.surface_filter.addItem("Snow")
        self.surface_filter.currentTextChanged.connect(self.stage_surface_filter_apply)
        self.country_filter = QComboBox()
        countries = ["Country","AR","AT","AU","BE","BR","CA","CH","CN","CY","CZ","DE","EE","ES","FI","FI","FR","GB","GR","HU","IE","IT","JP","KE","LB","LT","LV","MC","MG","MX","NL","NZ","PL","PT","RO","SE","SI","SK","SM","UA","US"]
        for country in countries:
            self.country_filter.addItem(country)
        self.country_filter.currentTextChanged.connect(self.stage_country_filter_apply)
        self.length_filter = QComboBox()
        for length in StagesFilterProxyModel.stage_length_filter_values:
            self.length_filter.addItem(length)
        self.length_filter.currentIndexChanged.connect(self.stage_length_filter_apply)
        self.rating_filter = QComboBox()
        for rate in StagesFilterProxyModel.stage_rating_filter_values:
            self.rating_filter.addItem(rate)
        self.rating_filter.currentIndexChanged.connect(self.stage_rating_filter_apply)
        self.installed_filter = QComboBox()
        self.installed_filter.addItem("Installed")
        self.installed_filter.addItem("Yes")
        self.installed_filter.addItem("No")
        self.installed_filter.currentTextChanged.connect(self.stage_installed_filter_apply)
        self.new_filter = QComboBox()
        self.new_filter.addItem("New")
        self.new_filter.addItem("Yes")
        self.new_filter.addItem("No")
        self.new_filter.currentTextChanged.connect(self.stage_new_filter_apply)
        filters_layout.addWidget(self.surface_filter)
        filters_layout.addWidget(self.length_filter)
        filters_layout.addWidget(self.country_filter)
        filters_layout.addWidget(self.new_filter)
        filters_layout.addWidget(self.installed_filter)
        filters_layout.addWidget(self.rating_filter)
        layout.addLayout(filters_layout,9,0)


        layout.addWidget(self.maps_tableview,10,0)

        layout.addWidget(self.fav_list_lbl,9,2,alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.favs_tableview,10,2)

        layout.addLayout(fav_buttons_layout,10,1)

        favorite_options_layout = QVBoxLayout()
        save_as_layout = QHBoxLayout()
        save_as_layout.addWidget(self.save_as_line)
        self.save_as_button.setMinimumHeight(30)
        self.save_as_button.setMinimumWidth(120)
        save_as_layout.addWidget(self.save_as_button)
        favorite_options_layout.addLayout(save_as_layout)
        load_url_layout = QHBoxLayout()
        load_url_layout.addWidget(self.url_load_favorites_line)
        self.load_url_button.setMinimumHeight(30)
        load_url_layout.addWidget(self.load_url_button)
        favorite_options_layout.addLayout(load_url_layout)

        layout.addLayout(favorite_options_layout,12,2)
        self.set_default_fav_button.setMinimumHeight(40)
        self.set_default_fav_button.setFont(QFont('Arial', 15))
        layout.addWidget(self.set_default_fav_button,13,0,1,3)



        layout.addWidget(self.status_bar,15,0,1,3)

        self.setLayout(layout)

        # FavoriteMgr setup
        self.myfav = fav.FavoriteMgr('C:\\Users\\User\\PycharmProjects\\rbr_favorit\\testing')

        if self.myfav.path:
            self.rbr_folder_line.setText(self.myfav.path)
            self.set_rbr_folder()


    def load_favorites_from_url_clicked(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Warning!")
        dlg.setText("Loading a URL will replace the current favorites. Is this OK?")
        # dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Ok:
            self.load_favorites_from_url()



    def load_favorites_from_url(self):
        url = self.url_load_favorites_line.text()
        logger.info(f"Loading favorites from URL: {url}")
        if url != "":
            if self.myfav.load_favorites_from_url(url):
                logger.info(f"Loaded stages from: {url}")
                self.set_status(f"Loaded stages from {url}")
                self.load_favorites_list()
            else:
                logger.error(f"Not able to load favorites from: {url}")
                self.set_status("Not able to load the stages from the given URL")


    def stage_surface_filter_apply(self, text):
        """
        Apply surface filter to maps
        :param text:
        :return:
        """
        self.proxy_model.setFilterSurface(text)

    def stage_country_filter_apply(self, text):
        """
        Apply country filter to maps
        :param text:
        :return:
        """
        self.proxy_model.setFilterCountry(text)

    def stage_text_filter_apply(self, text):
        """
        Apply text filter to maps
        :param text:
        :return:
        """
        self.proxy_model.setFilterNameOrID(text)

    def stage_length_filter_apply(self, index):
        """
        Apply length filter to maps
        :param index:
        :return:
        """
        self.proxy_model.setFilterLength(index)

    def stage_rating_filter_apply(self, index):
        """
        Apply rating filter to maps
        :param index:
        :return:
        """
        self.proxy_model.setFilterRating(index)

    def stage_installed_filter_apply(self, text):
        """
        Apply installed filter to maps
        :param text:
        :return:
        """
        self.proxy_model.setFilterInstalled(text)

    def stage_new_filter_apply(self, text):
        """
        Apply new filter to maps
        :param text:
        :return:
        """
        self.proxy_model.setFilterNew(text)


    def show_file_dialog(self):
        dir = QFileDialog.getExistingDirectory(None, "Choose RBR install folder","C:\\", QFileDialog.Option.ShowDirsOnly)
        if dir != "":
            logger.info(f"Chosen RBR install folder: {dir}")
            self.rbr_folder_line.setText(dir)
            self.set_rbr_folder()

    def set_default_favs(self):
        logger.info("Saving favorites as default")
        file_path = self.myfav.save_favorite("", default=True)
        self.set_status(f"Saved favorites as {file_path}")

    def load_favorite_file(self):
        current_row = self.fav_files_list_widget.currentRow()
        fav_file_name = self.fav_files_list_widget.item(current_row).text()
        logger.info(f"Loading favorite file: {fav_file_name}")
        self.myfav.load_favorite(fav_file_name)
        self.load_favorites_list()
        self.save_as_line.setText(fav_file_name.split(".")[0])
        self.set_status(f"Loaded favorites from: {fav_file_name}")


    def set_rbr_folder(self):
        """
        Sets the current RBR install folder to the one from the rbr_folder_line widget and loads all the widgets with info from this RBR install dir
        :return:
        """
        rbr_folder_text = self.rbr_folder_line.text()
        logger.info(f"Setting rbr folder to: {rbr_folder_text}")
        if rbr_folder_text != "":
            if self.myfav.set_default_path(rbr_folder_text):
                self.myfav.load_favorite("", default=True)
                self.load_favorites_list()
                self.load_fav_files()
                # self.fill_maps_table(refresh=True)

                self.load_stages()

                self.set_status(f"Updated RBR install folder to: {rbr_folder_text}")
            else:
                self.set_status("Wrong folder, could not load Maps!")

    def load_stages(self):
        """
        Loads the stage TableView with data
        :return:
        """
        logger.info("Loading stages tableview")
        self.stage_data = convert_stages_to_model_data(self.myfav.load_stages())
        model = StageTableModel(self.stage_data)

        self.proxy_model = StagesFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1) # Search all columns.
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setSourceModel(model)
        # self.search_box.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.search_box.textChanged.connect(self.stage_text_filter_apply)

        self.maps_tableview.setModel(self.proxy_model)
        self.maps_tableview.doubleClicked.connect(self.add_to_favorites)


    def add_to_favorites(self):
        """
        Adding a map to the favorites
        :return:
        """
        # check if there are selected items
        indexes = self.maps_tableview.selectionModel().selectedIndexes()
        if indexes:
            for index in indexes:
                model = self.maps_tableview.model()
                selected_id = model.data(model.index(index.row(),0))
                logger.info(f"Adding favorite: {selected_id}")
                self.myfav.add_favorite(selected_id)
            self.load_favorites_list()


    def remove_from_favorites(self):
        """
        Remove a map from favorites
        :return:
        """
        indexes = self.favs_tableview.selectionModel().selectedIndexes()
        if indexes:
            for index in indexes:
                model = self.favs_tableview.model()
                selected_id = model.data(model.index(index.row(),0))
                logger.info(f"Removing favorite: {selected_id}")
                self.myfav.remove_favorite(selected_id)
                # self.myfav.add_favorite(selected_id)
            self.load_favorites_list()


    def save_as_favorites(self):
        """
        Called when the save as favorites button is pressed and saves the current selected favorites as a file with name from the text in the save_as_line widget
        :return:
        """
        save_text = self.save_as_line.text()
        if save_text == "":
            self.set_status("Please provide a name for the favorite")
        else:
            logger.info(f"Saving favorites as: {save_text}")
            file_path = self.myfav.save_favorite(save_text)
            self.load_fav_files()
            self.set_status(f"Saved favorites as {file_path}")


    def load_favorites_list(self):
        """
        Loads the current favorites in the List widget
        :return:
        """
        logger.info("Loading favorites tableview")
        stage_data = convert_stages_to_model_data(self.myfav.get_current_favorite_stages())
        model = StageTableModel(stage_data)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(model)

        self.favs_tableview.setModel(proxy_model)
        self.favs_tableview.doubleClicked.connect(self.remove_from_favorites)


    def load_fav_files(self):
        """
        Loads the existing favorite files in the List widget
        :return:
        """
        logger.info("Loading favorite files")
        self.fav_files_list_widget.clear()
        self.fav_files_list_widget.addItems(self.myfav.load_favorite_files())

    def set_status(self, text):
        """
        Changes the status bar text
        :param text: text to show
        :return:
        """
        logger.info(f"Setting status message:{text}")
        self.status_bar.showMessage(text)

    # def fill_maps_table(self, refresh=False):
    #     """
    #     Fills the maps table with info on every existing stage from the current rbr Maps folder
    #     :param refresh: used to filter the maps according to the search widget
    #     :return:
    #     """
    #
    #     all_maps = self.myfav.load_maps()
    #     if refresh:
    #         all_maps = self.myfav.search_maps(self.search_box.text())
    #         self.maps_table.setRowCount(0)
    #     all_stages = {}
    #     for item in all_maps:
    #         map_info = favorite_api.get_map_details(item)
    #         details = self.myfav.get_stage_details(map_info["id"])
    #         all_stages[map_info['id']] = details
    #     #testing
    #     all_stages = self.myfav.stages
    #     self.maps_table.setRowCount(len(all_stages))
    #     table_headers = ["ID", "Name", "Surface", "Length", "Country", "Author", "New"]
    #     self.maps_table.setColumnCount(len(table_headers))
    #     self.maps_table.setHorizontalHeaderLabels(table_headers)
    #     self.maps_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    #     # testing
    #     # for i, stage in enumerate(all_stages.values()):
    #     for i, stage in enumerate(all_stages):
    #         item_id = QTableWidgetItem()
    #         item_id.setData(Qt.ItemDataRole.DisplayRole, int(stage["id"]))
    #         # item_id.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
    #         item_name = QTableWidgetItem(stage["name"])
    #         surface = "Gravel"
    #         if stage["surface_id"] == "1":
    #             surface = "Tarmac"
    #         elif stage["surface_id"] == "3":
    #             surface = "Snow"
    #         item_surface = QTableWidgetItem(surface)
    #         stage_length_km = round(int(stage["length"])/1000, 1)
    #         # hack to use float and sort correctly
    #         item_length = QTableWidgetItem()
    #         item_length.setData(Qt.ItemDataRole.DisplayRole, stage_length_km)
    #         item_country = QTableWidgetItem(stage['short_country'])
    #         item_author = QTableWidgetItem(stage['author'])
    #         item_new = QTableWidgetItem(("True" if stage["new_update"] == "1" else "False"))
    #         self.maps_table.setItem(i, 0, item_id)
    #         self.maps_table.setItem(i, 1, item_name)
    #         self.maps_table.setItem(i, 2, item_surface)
    #         self.maps_table.setItem(i, 3, item_length)
    #         self.maps_table.setItem(i, 4, item_country)
    #         self.maps_table.setItem(i, 5, item_author)
    #         self.maps_table.setItem(i, 6, item_new)
    #         self.maps_table.sortItems(0)

    # def table_item_clicked(self):
    #     current_col = self.maps_table.currentColumn()
    #     self.maps_table.sortItems(current_col, self.get_sort())
    #     print("derp")

    # def get_sort(self):
    #     if self.sort_order is None:
    #         self.sort_order = Qt.SortOrder.AscendingOrder
    #     elif self.sort_order == Qt.SortOrder.AscendingOrder:
    #         self.sort_order = Qt.SortOrder.DescendingOrder
    #     else:
    #         self.sort_order = Qt.SortOrder.AscendingOrder
    #     return self.sort_order

    def closeEvent(self, event):
        """
        Called when the windows exits
        :param event:
        :return:
        """
        logger.info("Shuting down, saving settings!")
        self.myfav.save_settings()

def setup_logging(debug_mode=False):
    """Configure logging for the entire application."""
    if debug_mode:
        # Ensure the logs directory exists
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        # Configure root logger to write to file
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s][%(filename)s][%(funcName)s][%(levelname)s]: %(message)s',
            filename=os.path.join(log_dir, 'debug.log'),
            filemode='a'  # 'w' overwrites the file each run, 'a' would append
        )
        logging.debug("Debug logging started")
    else:
        # Configure to discard all messages
        logging.basicConfig(
            level=logging.CRITICAL + 1  # Higher than any defined level
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Enable debug logging to file')
    args = parser.parse_args()

    # Configure logging based on arguments
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    logger.debug("Started debugging!")

    app = QApplication(sys.argv)
    window = ListBoxExample()
    window.show()
    sys.exit(app.exec())
