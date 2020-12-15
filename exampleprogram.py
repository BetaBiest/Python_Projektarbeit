from pandastable import Table, TableModel
from tkinter import Tk, Menu, Frame, LabelFrame, Button, Listbox, Label, StringVar, Entry, Radiobutton, BooleanVar, \
    Checkbutton, E, W, X, END
from tkinter.filedialog import askopenfilenames
from tkinter.messagebox import showerror
from tkinter.ttk import Combobox

from csvxmlimporter import CsvXmlImporter

# list of encodings that can be detected by chardet
encodings = (
    "Big5", "GB2312", "GB18030", "EUC-TW", "HZ-GB-2312", "ISO-2022-CN", "EUC-JP", "SHIFT_JIS", "ISO-2022-JP", "EUC-KR",
    "ISO-2022-KR", "KOI8-R", "MacCyrillic", "IBM855", "IBM866", "ISO-8859-5", "windows-1251", "ISO-8859-2",
    "windows-1250", "ISO-8859-5", "windows-1251", "ISO-8859-1", "windows-1252", "ISO-8859-7", "windows-1253",
    "ISO-8859-8", "windows-1255", "TIS-620", "UTF-32", "UTF-16", "UTF-8")


class Program:
    """Exampleprogram to show possible usage of the model csvxmlImporter"""
    __importer: CsvXmlImporter

    def __init__(self):
        self.__settings = {}
        self.__importer = CsvXmlImporter()

        self.__root = Tk()
        self.__root.minsize(560, 1)
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
        buttonframe = Frame(srcfilesframe)
        addbutton = Button(buttonframe,
                           text="Add Files",
                           command=self.add_files)
        addbutton.pack(fill=X)
        removefilesbutton = Button(buttonframe,
                                   text="Remove Selected",
                                   command=self.remove_files)
        removefilesbutton.pack(fill=X)
        removeallbutton = Button(buttonframe,
                                 text="Remove All",
                                 command=self.remove_all)
        removeallbutton.pack(fill=X)
        buttonframe.grid(column=1, row=1)
        self.__srcfileslistbox = Listbox(srcfilesframe, selectmode="extended", width=100)
        self.__srcfileslistbox.grid(column=2, row=1)
        Label(srcfilesframe, text="Encoding").grid(column=1, row=2, sticky=E)
        self.__settings["encoding"] = StringVar()
        encCombobox = Combobox(srcfilesframe, textvariable=self.__settings["encoding"], values=encodings,
                               state="readonly")
        # TODO find better option for update
        encCombobox.bind("<FocusOut>", self.update_settings)
        encCombobox.grid(column=2, row=2, pady=10)
        srcfilesframe.pack(fill=X)

        # TODO implement xsl file dialog
        # ***---*** xsl file dialog ***---***
        # xslfileframe = LabelFrame(self.__root, text="XSL-File")

        # ***---*** file format settings dialog ***---***
        # small help function
        def limit_character(entry_text):
            if len(entry_text.get()) > 0:
                # take only last input character and throw away the rest
                entry_text.set(entry_text.get()[-1])

        def make_radiobuttons(button_value, button_labels, c, r, command=lambda *_: None):
            if isinstance(button_labels, tuple) or isinstance(button_labels, list):
                for i, item in enumerate(button_labels):
                    Radiobutton(fileformatsettingsframe, text=item, variable=button_value,
                                value=item, command=command).grid(column=c + i, row=r, padx=10, sticky=W)

        fileformatsettingsframe = LabelFrame(self.__root, text="File Format Settings")
        Label(fileformatsettingsframe, text="Separator").grid(column=1, row=1, sticky=E)
        self.__settings["separator"] = StringVar()
        seperatorentry = Entry(fileformatsettingsframe, textvariable=self.__settings["separator"], width=1)
        self.__settings["separator"].trace("w", lambda *_: limit_character(self.__settings["separator"]))
        seperatorentry.bind("<Return>", self.update_settings)
        seperatorentry.bind("<FocusOut>", self.update_settings)
        seperatorentry.grid(column=2, row=1, sticky=W, padx=15)
        Label(fileformatsettingsframe, text="Field separator").grid(column=1, row=2, sticky=E)
        self.__settings["fieldseparator"] = StringVar()
        fieldseperatorentry = Entry(fileformatsettingsframe, textvariable=self.__settings["fieldseparator"], width=1)
        self.__settings["fieldseparator"].trace("w", lambda *_: limit_character(self.__settings["fieldseparator"]))
        fieldseperatorentry.bind("<Return>", self.update_settings)
        fieldseperatorentry.bind("<FocusOut>", self.update_settings)
        fieldseperatorentry.grid(column=2, row=2, sticky=W, padx=15)
        Label(fileformatsettingsframe, text="Marking of field separator in fields").grid(column=1, row=3, sticky=E)
        markingoptions = ("double", "mark")  # TODO eventually define this as global enum
        self.__settings["markingoption"] = StringVar()
        self.__settings["markingoption"].set(markingoptions[1])
        make_radiobuttons(self.__settings["markingoption"], markingoptions, 2, 3, self.update_settings)
        Label(fileformatsettingsframe, text="Marking sign").grid(column=1, row=4, sticky=E)
        self.__settings["markingsign"] = StringVar()
        markingsignentry = Entry(fileformatsettingsframe, textvariable=self.__settings["markingsign"], width=1)
        self.__settings["markingsign"].trace("w", lambda *_: limit_character(self.__settings["markingsign"]))
        markingsignentry.bind("<Return>", self.update_settings)
        markingsignentry.bind("<FocusOut>", self.update_settings)
        markingsignentry.grid(column=2, row=4, sticky=W, padx=15)
        Label(fileformatsettingsframe, text="Field marking mode").grid(column=1, row=5, sticky=E)
        markingmodes = ("all", "minimal", "non numeric", "none")  # TODO eventually define this as global enum
        self.__settings["markingmode"] = StringVar()
        self.__settings["markingmode"].set(markingmodes[1])
        make_radiobuttons(self.__settings["markingmode"], markingmodes, 2, 5, self.update_settings)
        Label(fileformatsettingsframe, text="Ignore spaces at beginning").grid(column=1, row=6, sticky=E)
        self.__settings["skipinitialspace"] = BooleanVar()
        self.__settings["skipinitialspace"].set(False)
        Checkbutton(fileformatsettingsframe, variable=self.__settings["skipinitialspace"],
                    command=self.update_settings).grid(column=2, row=6, sticky=W, padx=10)
        Label(fileformatsettingsframe, text="Headline present").grid(column=1, row=7, sticky=E)
        self.__settings["headlinepresent"] = BooleanVar()
        self.__settings["headlinepresent"].set(False)
        Checkbutton(fileformatsettingsframe, variable=self.__settings["headlinepresent"],
                    command=self.update_settings).grid(column=2, row=7, sticky=W, padx=10)
        fileformatsettingsframe.pack(fill=X)

        # TODO implement preview frame
        # ***---*** preview frame ***---***
        previewframe = LabelFrame(self.__root, text="Preview")
        self.__pdtable = Table(parent=previewframe, dataframe=self.__importer.dfx)  # TODO hand over dataframe
        self.__pdtable.show()
        previewframe.pack()

        # save settings to check for changes on update
        self.__prevsettings = self.__unpack_settings(self.__settings)

    def run(self):
        self.__root.mainloop()

    def exit_program(self):
        self.__root.destroy()

    def add_files(self):
        names = askopenfilenames()
        if names:
            try:
                self.__importer.set_files(names)
                self.__srcfileslistbox.insert(END, *names)
                self.__importer.set_files(self.__srcfileslistbox.get(0, END))
            except ValueError:
                showerror(title="Error", message="Could not open files")

            self.__update_table()
            self.__update_dialog()

    def remove_files(self):
        itemstodelete = self.__srcfileslistbox.curselection()
        if itemstodelete:
            for i in itemstodelete:
                self.__srcfileslistbox.delete(i)
            self.__importer.set_files(self.__srcfileslistbox.get(0, END))
            self.__update_table()

    def remove_all(self):
        self.__srcfileslistbox.delete(0, END)

    @staticmethod
    def __unpack_settings(settings):
        """__unpack_settings takes settings in form of dict with tkinter variables and unpacks them"""
        return dict((key, settings[key].get()) for key in settings)

    def __update_table(self):
        self.__pdtable.updateModel(TableModel(self.__importer.dfx))
        self.__pdtable.redraw()

    def __update_dialog(self):
        importersettings = self.__importer.get_settings()
        for key in self.__settings:
            if key in importersettings:
                self.__settings[key].set(importersettings[key])

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
