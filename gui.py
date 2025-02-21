import sys
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtWidgets import QFileDialog, QFrame, QHeaderView, QApplication, QHBoxLayout, QWidget, QVBoxLayout, \
    QListWidget, QPushButton, QLabel, QLineEdit, QStatusBar, QMainWindow, QTableWidget, QTableWidgetItem, QGridLayout, \
    QSizePolicy, QTableView
from PyQt6.QtGui import QFont

import favorite_api
# from PySide6 import QtCore, QtWidgets, QtGui
import favorite_api as fav

class StageTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
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
        converted.append([int(stage["id"]), stage["name"], surface, stage_length_km, stage["short_country"], stage["author"], item_new, item_exists])
    return converted

class ListBoxExample(QWidget):
    def __init__(self):
        super().__init__()

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
        self.maps_table = QTableWidget()
        self.maps_table.setMinimumHeight(200)
        self.maps_table.horizontalHeader().sectionClicked.connect(self.table_item_clicked)


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

        # Dialog
        self.file_dialog = QFileDialog()
        self.file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        self.file_dialog.setDirectory("C:\\")


        # Line Edits
        self.search_box = QLineEdit()
        self.search_box.setMaxLength(10)
        self.search_box.setPlaceholderText("Search Maps")
        # self.search_box.textChanged.connect(self.searched)
        self.save_as_line = QLineEdit()
        self.save_as_line.setPlaceholderText("Save As")
        self.rbr_folder_line = QLineEdit()
        self.rbr_folder_line.setPlaceholderText("RBR install folder")


        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")

        #TableView

        self.maps_tableview = QTableView()
        self.maps_tableview.setSortingEnabled(True)
        # self.maps_tableview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.favs_tableview = QTableView()
        self.favs_tableview.setSortingEnabled(True)
        # layout.addWidget(self.maps_tableview,14,0)

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
        # self.maps_tableview.setMinimumWidth(500)
        # self.maps_table.setMinimumWidth(500)

        # maps_layout = QHBoxLayout()
        # maps_layout.addWidget(self.maps_table)
        fav_buttons_layout = QVBoxLayout()
        self.add_fav_button.setMinimumHeight(40)
        self.remove_fav_button.setMinimumHeight(40)
        fav_buttons_layout.addWidget(self.add_fav_button)
        fav_buttons_layout.addWidget(self.remove_fav_button)
        # maps_layout.addLayout(fav_buttons_layout)
        # maps_layout.addWidget(self.favs_list_widget)
        # layout.addLayout(maps_layout,8,0,1,3)

        layout.addWidget(self.map_list_lbl,8,0,alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.maps_tableview,9,0)
        # layout.addWidget(self.maps_table,9,0)

        layout.addWidget(self.fav_list_lbl,8,2,alignment=Qt.AlignmentFlag.AlignCenter)
        # self.favs_list_widget.setMaximumWidth(200)

        layout.addWidget(self.favs_tableview,9,2)
        # layout.addWidget(self.favs_list_widget,9,2)


        layout.addLayout(fav_buttons_layout,9,1)
        # layout.addWidget(self.add_fav_button,9,1)
        # layout.addWidget(self.remove_fav_button,10,1)

        save_as_layout = QHBoxLayout()
        save_as_layout.addWidget(self.save_as_line)
        self.save_as_button.setMinimumHeight(30)
        self.save_as_button.setMinimumWidth(120)
        save_as_layout.addWidget(self.save_as_button)

        layout.addLayout(save_as_layout,11,2)
        self.set_default_fav_button.setMinimumHeight(40)
        self.set_default_fav_button.setFont(QFont('Arial', 15))
        layout.addWidget(self.set_default_fav_button,12,0,1,3)
        layout.addWidget(self.status_bar,13,0,1,3)





        self.setLayout(layout)

        # FavoriteMgr setup
        self.myfav = fav.FavoriteMgr('C:\\Users\\User\\PycharmProjects\\rbr_favorit\\testing')

        if self.myfav.path:
            self.rbr_folder_line.setText(self.myfav.path)
            self.set_rbr_folder()


    # def update_maps_table_view(self):
    #     stages_data = convert_stages_to_model_data(self.myfav.load_stages())
    #     model = StageTableModel(stages_data)
    #     self.maps_tableview.setModel(model)

    def init_data(self):
        pass

    def show_file_dialog(self):
        dir = QFileDialog.getExistingDirectory(None, "Choose RBR install folder","C:\\", QFileDialog.Option.ShowDirsOnly)
        if dir != "":
            self.rbr_folder_line.setText(dir)
            self.set_rbr_folder()

    def set_default_favs(self):
        file_path = self.myfav.save_favorite("", default=True)
        self.set_status(f"Saved favorites as {file_path}")

    def load_favorite_file(self):
        current_row = self.fav_files_list_widget.currentRow()
        fav_file_name = self.fav_files_list_widget.item(current_row).text()
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
        print(f"Setting rbr folder to: {rbr_folder_text}")
        if rbr_folder_text != "":
            if self.myfav.set_default_path(rbr_folder_text):
                self.myfav.load_favorite("", default=True)
                self.load_favorites_list()
                self.load_fav_files()
                self.fill_maps_table(refresh=True)

                self.load_stages()

                self.set_status(f"Updated RBR install folder to: {rbr_folder_text}")
            else:
                self.set_status("Wrong folder, could not load Maps!")

    def load_stages(self):
        """
        Loads the stage TableView with data
        :return:
        """
        self.stage_data = convert_stages_to_model_data(self.myfav.load_stages())
        model = StageTableModel(self.stage_data)

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1) # Search all columns.
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setSourceModel(model)
        self.search_box.textChanged.connect(self.proxy_model.setFilterFixedString)

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
                self.myfav.add_favorite(selected_id)
            self.load_favorites_list()
        # if self.maps_table.selectedItems():
        #     current_row = self.maps_table.currentRow()
        #     current_id = self.maps_table.item(current_row,0).text()
        #     self.myfav.add_favorite(current_id)
        #     self.load_favorites_list()



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
                self.myfav.remove_favorite(selected_id)
                # self.myfav.add_favorite(selected_id)
            self.load_favorites_list()



        # selected_items = self.favs_list_widget.selectedItems()
        # current_row = self.favs_list_widget.currentRow()
        # if current_row < 0:
        #     return
        # map_selected = self.favs_list_widget.item(current_row).text()
        # details = fav.get_map_details(map_selected)
        # if details['id'] in self.myfav.favorites:
        #     self.myfav.remove_favorite(details['id'])
        #     self.load_favorites_list()

    def save_as_favorites(self):
        """
        Called when the save as favorites button is pressed and saves the current selected favorites as a file with name from the text in the save_as_line widget
        :return:
        """
        save_text = self.save_as_line.text()
        if save_text == "":
            self.set_status("Please provide a name for the favorite")
        else:
            file_path = self.myfav.save_favorite(save_text)
            self.load_fav_files()
            self.set_status(f"Saved favorites as {file_path}")

    def searched(self):
        """
        Called when text changes in the search box
        :return:
        """
        # search_text = self.search_box.text()
        #self.map_list_widget.findItems(search_text, Qt.MatchFlag.MatchContains)
        # map_list = self.myfav.search_maps(self.search_box.text())
        # self.set_map_list(map_list)
        self.fill_maps_table(refresh=True)

    def set_map_list(self, map_list):
        """
        Called to change the map list
        :param map_list:
        :return:
        """
        #self.map_list_widget = QListWidget()
        self.map_list_widget.clear()
        self.map_list_widget.addItems(map_list)

    def load_favorites_list(self):
        """
        Loads the current favorites in the List widget
        :return:
        """
        # self.favs_list_widget.clear()
        # self.favs_list_widget.addItems(self.myfav.get_favorites_names())

        stage_data = convert_stages_to_model_data(self.myfav.get_current_favorite_stages())
        model = StageTableModel(stage_data)

        proxy_model = QSortFilterProxyModel()
        # proxy_model.setFilterKeyColumn(-1) # Search all columns.
        # proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        proxy_model.setSourceModel(model)
        # self.search_box.textChanged.connect(proxy_model.setFilterFixedString)

        self.favs_tableview.setModel(proxy_model)
        self.favs_tableview.doubleClicked.connect(self.remove_from_favorites)




    def load_fav_files(self):
        """
        Loads the existing favorite files in the List widget
        :return:
        """
        self.fav_files_list_widget.clear()
        self.fav_files_list_widget.addItems(self.myfav.load_favorite_files())

    def set_status(self, text):
        """
        Changes the status bar text
        :param text: text to show
        :return:
        """
        self.status_bar.showMessage(text)

    def fill_maps_table(self, refresh=False):
        """
        Fills the maps table with info on every existing stage from the current rbr Maps folder
        :param refresh: used to filter the maps according to the search widget
        :return:
        """

        all_maps = self.myfav.load_maps()
        if refresh:
            all_maps = self.myfav.search_maps(self.search_box.text())
            self.maps_table.setRowCount(0)
        all_stages = {}
        for item in all_maps:
            map_info = favorite_api.get_map_details(item)
            details = self.myfav.get_stage_details(map_info["id"])
            all_stages[map_info['id']] = details
        #testing
        all_stages = self.myfav.stages
        self.maps_table.setRowCount(len(all_stages))
        table_headers = ["ID", "Name", "Surface", "Length", "Country", "Author", "New"]
        self.maps_table.setColumnCount(len(table_headers))
        self.maps_table.setHorizontalHeaderLabels(table_headers)
        self.maps_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # testing
        # for i, stage in enumerate(all_stages.values()):
        for i, stage in enumerate(all_stages):
            item_id = QTableWidgetItem()
            item_id.setData(Qt.ItemDataRole.DisplayRole, int(stage["id"]))
            # item_id.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
            item_name = QTableWidgetItem(stage["name"])
            surface = "Gravel"
            if stage["surface_id"] == "1":
                surface = "Tarmac"
            elif stage["surface_id"] == "3":
                surface = "Snow"
            item_surface = QTableWidgetItem(surface)
            stage_length_km = round(int(stage["length"])/1000, 1)
            # hack to use float and sort correctly
            item_length = QTableWidgetItem()
            item_length.setData(Qt.ItemDataRole.DisplayRole, stage_length_km)
            item_country = QTableWidgetItem(stage['short_country'])
            item_author = QTableWidgetItem(stage['author'])
            item_new = QTableWidgetItem(("True" if stage["new_update"] == "1" else "False"))
            self.maps_table.setItem(i, 0, item_id)
            self.maps_table.setItem(i, 1, item_name)
            self.maps_table.setItem(i, 2, item_surface)
            self.maps_table.setItem(i, 3, item_length)
            self.maps_table.setItem(i, 4, item_country)
            self.maps_table.setItem(i, 5, item_author)
            self.maps_table.setItem(i, 6, item_new)
            self.maps_table.sortItems(0)

    def table_item_clicked(self):
        current_col = self.maps_table.currentColumn()
        self.maps_table.sortItems(current_col, self.get_sort())
        print("derp")

    def get_sort(self):
        if self.sort_order is None:
            self.sort_order = Qt.SortOrder.AscendingOrder
        elif self.sort_order == Qt.SortOrder.AscendingOrder:
            self.sort_order = Qt.SortOrder.DescendingOrder
        else:
            self.sort_order = Qt.SortOrder.AscendingOrder
        return self.sort_order

    def closeEvent(self, event):
        """
        Called when the windows exits
        :param event:
        :return:
        """
        self.myfav.save_settings()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ListBoxExample()
    window.show()
    sys.exit(app.exec())
