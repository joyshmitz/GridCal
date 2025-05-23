# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
import os
import json
from typing import Dict, Union
from GridCalEngine.IO.file_system import get_create_gridcal_folder

from GridCal.Gui.Main.SubClasses.base_gui import BaseMainGui
from GridCal.Session.server_driver import ServerDriver
from GridCal.Gui.messages import warning_msg, yes_no_question


class ServerMain(BaseMainGui):
    """
    MainGUI
    """

    def __init__(self, parent=None) -> None:
        """
        Main constructor
        """

        # create main window
        BaseMainGui.__init__(self, parent=parent)

        # Server driver
        self.server_driver: ServerDriver = ServerDriver(url="", port=0, pwd="", secure=False)
        self.server_driver.connected_signal.connect(self.server_connected)
        self.server_driver.done_signal.connect(self.post_start_stop_server)  # connect the post function

        self.ui.server_tableView.setModel(self.server_driver.data_model)

        # menu
        self.ui.actionEnable_server_mode.triggered.connect(self.server_start_stop)

        # table double click
        self.ui.server_tableView.doubleClicked.connect(self.get_results)

    @staticmethod
    def server_config_file_path() -> str:
        """
        get the config file path
        :return: config file path
        """
        return os.path.join(get_create_gridcal_folder(), 'server_config.json')

    def server_config_file_exists(self) -> bool:
        """
        Check if the config file exists
        :return: True / False
        """
        return os.path.exists(self.server_config_file_path())

    def get_gui_server_config_data(self):
        """
        Get server data from the GUI
        :return:
        """
        return {"url": self.ui.server_url_lineEdit.text(),
                "port": self.ui.server_port_spinBox.value(),
                "user": "",
                "pwd": self.ui.server_pwd_lineEdit.text(),
                "secure": self.ui.secureServerConnectionCheckBox.isChecked(),}

    def save_server_config(self):
        """
        Save the GUI configuration
        :return:
        """
        data = self.get_gui_server_config_data()
        with open(self.server_config_file_path(), "w") as f:
            f.write(json.dumps(data, indent=4))

    def apply_server_config(self, data: Dict[str, Union[str, int]]) -> None:
        """
        Apply the server config
        :param data: Some local data
        """
        self.ui.server_url_lineEdit.setText(data.get("url", "localhost"))
        self.ui.server_port_spinBox.setValue(data.get("port", 8080))
        # "user": "",
        self.ui.server_pwd_lineEdit.setText(data.get("pwd", "1234"))
        self.ui.secureServerConnectionCheckBox.setChecked(data.get("secure", True))

    def load_server_config(self) -> None:
        """
        Load server configuration from the local user folder
        """
        if self.server_config_file_exists():
            with open(self.server_config_file_path(), "r") as f:
                try:
                    data = json.load(f)
                    self.apply_server_config(data=data)
                except json.decoder.JSONDecodeError as e:
                    print(e)
                    self.save_server_config()
                    self.show_error_toast("Server config file was erroneous, wrote a new one")

    def server_start_stop(self):
        """

        :return:
        """
        if self.ui.actionEnable_server_mode.isChecked():

            # create a new driver
            self.server_driver.set_values(url=self.ui.server_url_lineEdit.text().strip(),
                                          port=self.ui.server_port_spinBox.value(),
                                          pwd=self.ui.server_pwd_lineEdit.text().strip(),
                                          secure=self.ui.secureServerConnectionCheckBox.isChecked(),
                                          status_func=self.ui.server_status_label.setText)

            # save the last server config
            self.save_server_config()

            # run asynchronously
            self.server_driver.start()

        else:

            ok = yes_no_question(text="The server connection is running, are you sure that you want to stop it?",
                                 title="Stop Server")

            if ok:
                self.server_driver.cancel()
                self.ui.actionEnable_server_mode.setChecked(False)
            else:
                self.ui.actionEnable_server_mode.setChecked(True)

    def post_start_stop_server(self):
        """
        Post server run
        :return:
        """
        if not self.server_driver.is_running():
            if self.server_driver.logger.has_logs():
                self.show_error_toast(message="Could not connect to the server :/")
                self.ui.actionEnable_server_mode.setChecked(False)

    def server_connected(self):
        """
        Called upon server connection
        :return:
        """
        self.show_info_toast(message="Connected!")


    def get_results(self):
        """

        :return:
        """

        indices = self.ui.server_tableView.selectedIndexes()

        if len(indices) == 1:

            row_idx = indices[0].row()

            job = self.server_driver.data_model.jobs[row_idx]

            self.server_driver.download_results(job_id=job.id_tag,
                                                api_key="",
                                                local_filename=job.id_tag + '.results')

        self.show_info_toast("results received!")
