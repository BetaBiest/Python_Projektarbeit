from tkinter import Tk, Menu, LabelFrame, Button, Listbox, Label, StringVar, Entry, Radiobutton, BooleanVar, Checkbutton
from tkinter.ttk import Combobox
from pandastable import Table

# from csvxmlImporter import CsvXmlImporter
# list of encodings that can be detected by chardet
encodings = (
    "Big5", "GB2312", "GB18030", "EUC-TW", "HZ-GB-2312", "ISO-2022-CN", "EUC-JP", "SHIFT_JIS", "ISO-2022-JP", "EUC-KR",
    "ISO-2022-KR", "KOI8-R", "MacCyrillic", "IBM855", "IBM866", "ISO-8859-5", "windows-1251", "ISO-8859-2",
    "windows-1250", "ISO-8859-5", "windows-1251", "ISO-8859-1", "windows-1252", "ISO-8859-7", "windows-1253",
    "ISO-8859-8", "windows-1255", "TIS-620", "UTF-32", "UTF-16", "UTF-8")


class Program:
    """Exampleprogram to show possible usage of the model csvxmlImporter"""

    def __init__(self):
        self.__settings = {}

        self.__root = Tk()
        menu = Menu(self.__root)
        self.__root.config(menu=menu)

        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        menu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit_program)

        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="?", command=self.ask_help)
        helpmenu.add_command(label="About", command=self.ask_about)

        # ***---*** source file frame dialog ***---***
        srcfilesframe = LabelFrame(self.__root, text="Sourcefiles")
        addbutton = Button(srcfilesframe,
                           text="Add Files",
                           command=self.add_files)
        addbutton.pack()
        removefilesbutton = Button(srcfilesframe,
                                   text="Remove Selected",
                                   command=self.remove_files)
        removefilesbutton.pack()
        removeallbutton = Button(srcfilesframe,
                                 text="Remove All",
                                 command=self.remove_all)
        removeallbutton.pack()
        self.__srcfileslistbox = Listbox(srcfilesframe, selectmode="extended")
        self.__srcfileslistbox.pack()
        Label(srcfilesframe, text="Encoding").pack()
        self.__settings["enc"] = StringVar()
        encCombobox = Combobox(srcfilesframe, textvariable=self.__settings["enc"], values=encodings, state="readonly")
        # TODO find better option for update
        encCombobox.bind("<FocusOut>", self.update_settings)
        encCombobox.pack()
        srcfilesframe.pack()

        # TODO implement xsl file dialog
        # ***---*** xsl file dialog ***---***
        # xslfileframe = LabelFrame(self.__root, text="XSL-File")

        # ***---*** file format settings dialog ***---***
        # small help function
        def limit_character(entry_text):
            if len(entry_text.get()) > 0:
                # take only last input character and throw away the rest
                entry_text.set(entry_text.get()[-1])

        def make_radiobuttons(button_value, button_labels, command=lambda *_: None):
            if isinstance(button_labels, tuple) or isinstance(button_labels, list):
                for item in button_labels:
                    Radiobutton(fileformatsettingsframe, text=item, variable=button_value,
                                value=item, command=command).pack()

        fileformatsettingsframe = LabelFrame(self.__root, text="File Format Settings")
        Label(fileformatsettingsframe, text="Separator").pack()
        self.__settings["separator"] = StringVar()
        seperatorentry = Entry(fileformatsettingsframe, textvariable=self.__settings["separator"], width=1)
        self.__settings["separator"].trace("w", lambda *_: limit_character(self.__settings["separator"]))
        seperatorentry.bind("<Return>", self.update_settings)
        seperatorentry.bind("<FocusOut>", self.update_settings)
        seperatorentry.pack()
        Label(fileformatsettingsframe, text="Field separator").pack()
        self.__settings["fieldseparator"] = StringVar()
        fieldseperatorentry = Entry(fileformatsettingsframe, textvariable=self.__settings["fieldseparator"], width=1)
        self.__settings["fieldseparator"].trace("w", lambda *_: limit_character(self.__settings["fieldseparator"]))
        fieldseperatorentry.bind("<Return>", self.update_settings)
        fieldseperatorentry.bind("<FocusOut>", self.update_settings)
        fieldseperatorentry.pack()
        Label(fileformatsettingsframe, text="Marking of field separator in fields").pack()
        markingoptions = ("double", "mark")  # TODO eventually define this as global enum
        self.__settings["markingoption"] = StringVar()
        self.__settings["markingoption"].set(markingoptions[1])
        make_radiobuttons(self.__settings["markingoption"], markingoptions, self.update_settings)
        Label(fileformatsettingsframe, text="Marking sign").pack()
        self.__settings["markingsign"] = StringVar()
        markingsignentry = Entry(fileformatsettingsframe, textvariable=self.__settings["markingsign"], width=1)
        self.__settings["markingsign"].trace("w", lambda *_: limit_character(self.__settings["markingsign"]))
        markingsignentry.bind("<Return>", self.update_settings)
        markingsignentry.bind("<FocusOut>", self.update_settings)
        markingsignentry.pack()
        Label(fileformatsettingsframe, text="Field marking mode").pack()
        markingmodes = ("all", "minimal", "non numeric", "none")  # TODO eventually define this as global enum
        self.__settings["markingmode"] = StringVar()
        self.__settings["markingmode"].set(markingmodes[1])
        make_radiobuttons(self.__settings["markingmode"], markingmodes, self.update_settings)
        Label(fileformatsettingsframe, text="Ignore spaces at beginning").pack()
        self.__settings["ignorespaces"] = BooleanVar()
        self.__settings["ignorespaces"].set(False)
        Checkbutton(fileformatsettingsframe, variable=self.__settings["ignorespaces"],
                    command=self.update_settings).pack()
        Label(fileformatsettingsframe, text="Headline present").pack()
        self.__settings["headlinepresent"] = BooleanVar()
        self.__settings["headlinepresent"].set(False)
        Checkbutton(fileformatsettingsframe, variable=self.__settings["headlinepresent"],
                    command=self.update_settings).pack()
        fileformatsettingsframe.pack()

        # TODO implement preview frame
        # ***---*** preview frame ***---***
        previewframe = LabelFrame(self.__root, text="Preview")
        Table(parent=previewframe, dataframe=None).show() # TODO hand over dataframe
        previewframe.pack()


        # save settings to check for changes on update
        self.__prevsettings = self.__unpack_settings(self.__settings)

    def run(self):
        self.__root.mainloop()

    def exit_program(self):
        self.__root.destroy()

    def add_files(self):
        # TODO implement add_files dialog
        pass

    def remove_files(self):
        # TODO implement remove_files function
        # ask Listbox via curselection which files to delete
        pass

    def remove_all(self):
        # TODO implement remove_all function
        pass

    @staticmethod
    def __unpack_settings(settings):
        """__unpack_settings takes settings in form of dict with tkinter variables and unpacks them"""
        return dict((key, settings[key].get()) for key in settings)

    def update_settings(self, *_):
        newsettings = self.__unpack_settings(self.__settings)
        if newsettings != self.__prevsettings:
            # figure out which settings changed
            changedsettings = dict(newsettings.items() - self.__prevsettings.items())
            for key in changedsettings:
                print(f'Key: {key}, Value: {changedsettings[key]}')
                # TODO do stuff here
            self.__prevsettings = newsettings
        pass

    def ask_help(self):
        # TODO add help dialog
        pass

    def ask_about(self):
        # TODO add about dialog
        pass


if __name__ == "__main__":
    Program().run()
