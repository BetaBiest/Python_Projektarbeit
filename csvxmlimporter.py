import csv
from pathlib import Path

import pandas as pd
from chardet import detect
from typing import Optional, Dict


class CsvXmlImporter:
    __file: str
    __currloaded: str
    __dfx: pd.DataFrame
    __pdreadcsvsettings: Dict

    def __init__(
            self,
            file: str,
            **pdreadcsvsettings
    ):
        self.__pdreadcsvsettings = pdreadcsvsettings
        self.__file = file
        # check if handed file is okay
        if not Path(file).exists():
            raise FileNotFoundError(f"File: {file} not found")
        self.__currloaded = file[-4::]
        if self.__currloaded != ".csv" and self.__currloaded != ".xml":
            raise ValueError(f"File: {file} has invalid file extension")

        self.guess_settings()
        self.__load_file()

    def __load_file(self):
        if self.__currloaded == ".csv":
            self.__load_csv()
        elif self.__currloaded == ".xml":
            self.__load_xml()

    def __load_csv(self):
        # TODO hand over all settings
        self.__dfx = pd.read_csv(
            self.__file,
            **self.__pdreadcsvsettings
        )

    def __load_xml(self):
        # TODO load xml and save to csv
        # self.load_csv(filename)
        pass

    def set_settings(self, **kwargs):
        changedsettings = dict(kwargs.items() - self.__pdreadcsvsettings.items())

        if changedsettings:
            for setting in changedsettings:
                # TODO validate userinput before applying settings
                pass
            self.__pdreadcsvsettings.update(changedsettings)

            if self.__currloaded == ".csv":
                self.__load_csv()
            elif self.__currloaded == ".xml":
                self.__load_xml()

    def guess_settings(self):
        """guess settings after seeing csv file for first time"""
        enc = detect(Path(self.__file).read_bytes())
        with open(self.__file, mode="r", encoding=enc["encoding"]) as f:
            # read first few lines as samples
            sample = ""
            for _ in range(3):
                sample += f.readline()

            # sniff the sample
            # FIXME set options for header properly
            # self.__pdreadcsvsettings["headlinepresent"] = csv.Sniffer().has_header(sample)
            dialect = csv.Sniffer().sniff(sample)

        # TODO guess dtpye
        # TODO read header names if headline is present

        self.__pdreadcsvsettings.update(
            encoding=enc["encoding"],
            sep=dialect.delimiter,
            skipinitialspace=dialect.skipinitialspace,
            quotechar=dialect.quotechar,
            doublequote=dialect.doublequote,
            quoting=dialect.quoting,
            escapechar=dialect.escapechar,
            # lineterminator=dialect.lineterminator
        )

        # if not specified by the user use common german/engl true false values
        if "true_values" not in self.__pdreadcsvsettings:
            self.__pdreadcsvsettings["true_values"] = ["WAHR", "wahr", "Wahr", "true", "True", "TRUE", "doch"]
        if "false_values" not in self.__pdreadcsvsettings:
            self.__pdreadcsvsettings["false_values"] = ["FALSCH", "falsch", "Falsch", "false", "False", "FALSE", "nein"]

    def return_dict(self):
        return self.__dfx.to_dict()
