import csv
import re
from io import StringIO
from pathlib import Path

import pandas as pd
from chardet import detect
from lxml import etree
from typing import Optional, Dict, List


class CsvXmlImporter:
    __filenames: List[str] or None
    __combinedcsvfile: str
    dfx: pd.DataFrame or None
    __pdreadcsvsettings: Optional[Dict]

    def __init__(
            self,
            filenames: Optional[str or list] = None,
            **pdreadcsvsettings
    ):
        self.__pdreadcsvsettings = pdreadcsvsettings

        self.__filenames = []
        if filenames:
            self.set_files(filenames)
        else:
            self.dfx = None

    def __validate_filenames(self):
        """check if all given filenames are correct"""
        if self.__filenames[0].endswith(".csv"):
            for f in self.__filenames:
                if not f.endswith(".csv"):
                    raise ValueError(f"Invalid filenames extension: {f} should be .csv")

        elif self.__filenames[0].endswith((".xml", ".xsl")):
            xslfound = False
            for f in self.__filenames:
                if not f.endswith((".xml", ".xsl")):
                    raise ValueError(f"Invalid filenames extension: {f} should be .xml or .xsl")
                if f.endswith(".xsl"):
                    if xslfound:
                        raise ValueError(f"Multiple .xsl files passed")
                    else:
                        xslfound = True
            if not xslfound:
                raise ValueError(f"No .xsl filenames for parsing .xml to .csv passed")

        for f in self.__filenames:
            if not Path(f).exists():
                raise FileNotFoundError(f"File: {f} not found")

    def __call_pdloadcsv(self):
        self.dfx = pd.read_csv(
            StringIO(self.__combinedcsvfile),
            **self.__pdreadcsvsettings
        )

    def __read_csv(self):
        csvfiles = []
        for fn in self.__filenames:
            enc = detect(Path(fn).read_bytes())["encoding"]
            self.__pdreadcsvsettings.update(encoding=enc)
            f = Path(fn).read_text(encoding=enc)
            csvfiles.append(f)
        self.__merge_csvfiles(*csvfiles)

    def __read_xmltocsv(self, **xslparam):
        xslfilename = [x for x in self.__filenames if x.endswith(".xsl")][0]
        self.__filenames.remove(xslfilename)
        transformer = etree.XSLT(etree.parse(xslfilename))
        csvfiles = []
        for fn in self.__filenames:
            csvfiles.append(str(transformer(etree.parse(fn), **xslparam)))
        self.__merge_csvfiles(*csvfiles)

    def __merge_csvfiles(self, *files: str):
        """combines all passed .csv files into one buffer if they match"""
        self.__combinedcsvfile = files[0]
        filesettings = self.__ascertain_settings(self.__combinedcsvfile)
        for f in files[1:]:
            if filesettings["names"] != self.__ascertain_settings(f)["names"]:
                raise ValueError("Files could not be merged")
            self.__combinedcsvfile += f'{filesettings["lineterminator"]}{f}'
        filesettings.pop("lineterminator", None)
        self.__pdreadcsvsettings.update(filesettings)  # TODO move this elsewhere maybe

    def __ascertain_settings(self, file):
        """ascertain settings by checking file content"""
        settings = {}
        with StringIO(file) as f:
            sample = f.readline()
            startsecondline = f.tell()
            sample += f.readline()

            dialect = csv.Sniffer().sniff(sample)
            if csv.Sniffer().has_header(sample):
                f.seek(startsecondline)
            else:
                f.seek(0)
                settings.update(header=None)

            firstline = next(csv.reader(f, dialect=dialect))
            headernames = []
            for i, item in enumerate(firstline):
                headernames.append(f'{i}_{self.__check_type(item)}')
            settings.update(
                delimiter=dialect.delimiter,
                doublequote=dialect.doublequote,
                escapechar=dialect.escapechar,
                lineterminator=dialect.lineterminator,
                quotechar=dialect.quotechar,
                quoting=dialect.quoting,
                skipinitialspace=dialect.skipinitialspace,
                names=headernames,
            )

        settings.update(
            true_values=["WAHR", "wahr", "Wahr", "true", "True", "TRUE", "ja", "JA", "Ja"],
            false_values=["FALSCH", "falsch", "Falsch", "false", "False", "FALSE", "nein", "NEIN", "Nein"],
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
        }
        for key in types:
            if types[key].match(string):
                return key
        return "String"

    def set_files(self, filenames: str or list):
        # check if handed files are correct
        if type(filenames) == str:
            self.__filenames = [filenames]
        else:
            self.__filenames = [*filenames]  # convert tuples in list
        self.__validate_filenames()

        if self.__filenames[0].endswith((".xml", ".xsl")):
            self.__read_xmltocsv()
        elif self.__filenames[0].endswith(".csv"):
            self.__read_csv()

        self.__call_pdloadcsv()

    def set_settings(self, **kwargs):
        """applies new passed parameters and reloads the .csv file with new settings"""
        self.__pdreadcsvsettings.update(kwargs)
        self.__call_pdloadcsv()

    def get_settings(self):
        return self.__pdreadcsvsettings

    def return_dict(self):
        return self.dfx.to_dict0() if self.dfx is not None else None

    def return_pddf(self):
        return self.dfx

    def return_nparray(self):
        # TODO check if all columns contain numbers, if true return nparray
        pass
