import csv
import re
from io import StringIO
from pathlib import Path
from typing import Optional, Dict, List

import pandas as pd
from chardet import detect
from lxml import etree


class CsvXmlImporter:
    __filenames: List[str] or None
    dfx: pd.DataFrame
    __pdreadcsvsettings: Optional[Dict]

    def __init__(
            self,
            filenames: Optional[str or list] = None,
            **pdreadcsvsettings
    ):
        self.__pdreadcsvsettings = pdreadcsvsettings
        self.__xslparameter = {}
        self.__filenames = []

        if filenames:
            self.update_files(*filenames if type(filenames) == list else filenames)
        else:
            self.dfx = pd.DataFrame()

    @staticmethod
    def __validate_filenames(*filenames):
        """check if all given filenames are correct"""
        for filename in filenames:
            if not filename.endswith((".xml", ".csv")):
                raise ValueError(f'File {filename} has invalid file extension')

    def __read_csv(self, filename):
        enc = detect(Path(filename).read_bytes())["encoding"]
        self.__pdreadcsvsettings.update(encoding=enc)  # TODO maybe delete this
        return Path(filename).read_text(encoding=enc)

    def __read_xml(self, filename):
        return str(self.__xmltransformer(etree.parse(filename), **self.__xslparameter))

    def __ascertain_settings(self, file):
        """ascertain settings by checking file content"""
        settings = {}
        with StringIO(file) as f:
            sample = f.readline() + f.readline()
            dialect = csv.Sniffer().sniff(sample)

            settings.update(
                dialect=dialect,
                delimiter=dialect.delimiter,
                doublequote=dialect.doublequote,
                escapechar=dialect.escapechar,
                lineterminator=dialect.lineterminator,
                quotechar=dialect.quotechar,
                quoting=dialect.quoting,
                skipinitialspace=dialect.skipinitialspace,
            )

        settings.update(
            true_values=["WAHR", "wahr", "Wahr", "true", "True", "TRUE", "ja", "JA", "Ja"],
            false_values=["FALSCH", "falsch", "Falsch", "false", "False", "FALSE", "nein", "NEIN", "Nein"],
        )

        return settings

    def __ascertain_header(self, file):
        settings = {}

        with StringIO(file) as f:
            sample = f.readline() + f.readline()

            if csv.Sniffer().has_header(sample):
                settings.update(
                    header=0
                )
            else:
                f.seek(0)
                firstline = next(
                    csv.reader(
                        f,
                        delimiter=self.__pdreadcsvsettings["delimiter"],
                        doublequote=self.__pdreadcsvsettings["doublequote"],
                        escapechar=self.__pdreadcsvsettings["escapechar"],
                        quotechar=self.__pdreadcsvsettings["quotechar"],
                        quoting=self.__pdreadcsvsettings["quoting"],
                        skipinitialspace=self.__pdreadcsvsettings["skipinitialspace"],
                    )
                )
                headernames = []
                for i, item in enumerate(firstline):
                    headernames.append(f'{i}_{self.__check_type(item)}')
                settings.update(
                    header=None,
                    names=headernames
                )

        return settings

    @staticmethod
    def __check_type(string):
        """check whether given input string matches any of the predetermined types
            returns matching type or 'String'"""
        types = {
            "Coordinate": re.compile(
                "^(N|S)?0*\d{1,2}°0*\d{1,2}(′|')0*\d{1,2}\.\d*(″|\")(?(1)|(N|S)) (E|W)?0*\d{1,2}°0*\d{1,2}(′|')0*\d{1,2}\.\d*(″|\")(?(5)|(E|W))$"
            ),
            # email regex source: https://stackoverflow.com/questions/201323/how-to-validate-an-email-address-using-a-regular-expression
            "Email": re.compile(
                "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            ),
            "Web-URL": re.compile(
                "^((ftp|http|https):\/\/)?(www.)?(?!.*(ftp|http|https|www.))[a-zA-Z0-9_-]+(\.[a-zA-Z]+)+((\/)[\w#]+)*(\/\w+\?[a-zA-Z0-9_]+=\w+(&[a-zA-Z0-9_]+=\w+)*)?$"
            ),
            "Time": re.compile(
                "^[0-2]\d:[0-6]\d:[0-6]\d$"
            ),
            "Date": re.compile(
                "^[0-3]?[0-9][/.][0-3]?[0-9][/.](?:[0-9]{2})?[0-9]{2}$"
            ),
            "Bool": re.compile(
                "(?i)^(wahr|falsch|true|false|ja|nein)$"
            ),
            "Int": re.compile(
                "^\d*$"
            ),
            "Float": re.compile(
                "^\d*(\.|,)\d*$"
            ),
        }
        for key in types:
            if types[key].match(string):
                return key
        return "String"

    def update_files(self, *filenames: str):
        # read csv files as string into buffer
        if filenames and [*filenames] != self.__filenames:
            self.__validate_filenames(*filenames)

            self.__filebuffer = [None] * len(filenames)  # TODO move to __init__
            for i, filename in enumerate(filenames):
                if filename.endswith(".csv"):
                    self.__filebuffer[i] = self.__read_csv(filename)

            self.__filenames = [*filenames]

        if self.__filenames:
            # read xml files as csv string into buffer
            for i, filename in enumerate(self.__filenames):
                if filename.endswith(".xml"):
                    self.__filebuffer[i] = self.__read_xml(filename)

            # guess settings without overwriting existing ones
            settings = self.__ascertain_settings(self.__filebuffer[0])
            self.__pdreadcsvsettings.update(
                delimiter=settings["delimiter"] if "delimiter" not in self.__pdreadcsvsettings else
                self.__pdreadcsvsettings["delimiter"],
                doublequote=settings["doublequote"] if "doublequote" not in self.__pdreadcsvsettings else
                self.__pdreadcsvsettings["doublequote"],
                escapechar=settings["escapechar"] if "escapechar" not in self.__pdreadcsvsettings else
                self.__pdreadcsvsettings["escapechar"],
                quotechar=settings["quotechar"] if "quotechar" not in self.__pdreadcsvsettings else
                self.__pdreadcsvsettings["quotechar"],
                quoting=settings["quoting"] if "quoting" not in self.__pdreadcsvsettings else
                self.__pdreadcsvsettings["quoting"],
                skipinitialspace=settings["skipinitialspace"] if "skipinitialspace" not in self.__pdreadcsvsettings else
                self.__pdreadcsvsettings["skipinitialspace"],
                true_values=settings["true_values"] if "true_values" not in self.__pdreadcsvsettings else
                self.__pdreadcsvsettings["true_values"],
                false_values=settings["false_values"] if "false_values" not in self.__pdreadcsvsettings else
                self.__pdreadcsvsettings["false_values"],
            )

            # merge filestrings in buffer to one dataframe
            self.dfx = pd.DataFrame()
            for file in self.__filebuffer:
                self.dfx = self.dfx.append(
                    pd.read_csv(
                        StringIO(file),
                        **self.__pdreadcsvsettings,
                        **self.__ascertain_header(file)
                    )
                )

    def set_xslfile(self, filename):
        tree = etree.parse(filename)
        self.__xmltransformer = etree.XSLT(tree)
        self.__xslparameter = {x.attrib["name"]: x.attrib["select"] for x in tree.getroot() if "param" in x.tag}

    def set_xslparameter(self, **kwargs):
        self.__xslparameter = kwargs

    def get_xslparameter(self):
        return self.__xslparameter

    def reset(self):
        self.dfx = pd.DataFrame()
        self.__pdreadcsvsettings = {}
        self.__filenames = None

    def set_settings(self, **kwargs):
        """applies new passed parameters and reloads files with new settings"""
        self.__pdreadcsvsettings.update(kwargs)
        self.update_files()

    def get_settings(self):
        return self.__pdreadcsvsettings

    def return_dict(self):
        return self.dfx.to_dict()

    def return_pddf(self):
        return self.dfx

    def return_nparray(self):
        # TODO check if all columns contain numbers, if true return nparray
        pass
