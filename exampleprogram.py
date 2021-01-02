from pandastable import Table, TableModel
from tkinter import Menu, Listbox, StringVar, BooleanVar, IntVar
from tkinter.constants import E, W, X, END
from tkinter.filedialog import askopenfilenames
from tkinter.messagebox import showerror, showinfo
from tkinter.ttk import Combobox, Frame, LabelFrame, Button, Label, Radiobutton, Checkbutton, Entry
from ttkthemes import ThemedTk

from csvxmlimporter import CsvXmlImporter

# list of encodings that can be detected by chardet
encodings = (
    "Big5", "GB2312", "GB18030", "EUC-TW", "HZ-GB-2312", "ISO-2022-CN", "EUC-JP", "SHIFT_JIS", "ISO-2022-JP", "EUC-KR",
    "ISO-2022-KR", "KOI8-R", "MacCyrillic", "IBM855", "IBM866", "ISO-8859-5", "windows-1251", "ISO-8859-2",
    "windows-1250", "ISO-8859-5", "windows-1251", "ISO-8859-1", "windows-1252", "ISO-8859-7", "windows-1253",
    "ISO-8859-8", "windows-1255", "TIS-620", "UTF-32", "UTF-16", "UTF-8", "ascii")


class Program:
    """Exampleprogram to show possible usage of the model csvxmlImporter"""
    __importer: CsvXmlImporter

    def __init__(self):
        self.__settings = {}
        self.__importer = CsvXmlImporter()

        self.__root = ThemedTk(theme="equilux")
        self.__root.title("Csv/Xml Importer")
        self.__root.minsize(560, 1)
        menu = Menu(self.__root)
        self.__root.config(menu=menu)

        filemenu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=filemenu)
        menu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit_program)

        helpmenu = Menu(menu, tearoff=0)
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

        fileformatsettingsframe = LabelFrame(self.__root, text="File Format Settings")

        Label(fileformatsettingsframe, text="Delimiter").grid(column=1, row=1, sticky=E)
        self.__settings["delimiter"] = StringVar()
        seperatorentry = Entry(fileformatsettingsframe, textvariable=self.__settings["delimiter"], width=1)
        self.__settings["delimiter"].trace("w", lambda *_: limit_character(self.__settings["delimiter"]))
        seperatorentry.bind("<Return>", self.update_settings)
        seperatorentry.bind("<FocusOut>", self.update_settings)
        seperatorentry.grid(column=2, row=1, sticky=W, padx=15)

        Label(fileformatsettingsframe, text="Quotechar").grid(column=1, row=2, sticky=E)
        self.__settings["quotechar"] = StringVar()
        quotecharentry = Entry(fileformatsettingsframe, textvariable=self.__settings["quotechar"], width=1)
        self.__settings["quotechar"].trace("w", lambda *_: limit_character(self.__settings["quotechar"]))
        quotecharentry.bind("<Return>", self.update_settings)
        quotecharentry.bind("<FocusOut>", self.update_settings)
        quotecharentry.grid(column=2, row=2, sticky=W, padx=15)

        Label(fileformatsettingsframe, text="Doublequote").grid(column=1, row=3, sticky=E)
        self.__settings["doublequote"] = BooleanVar()
        Checkbutton(fileformatsettingsframe, variable=self.__settings["doublequote"],
                    command=self.update_settings).grid(column=2, row=3, sticky=W, padx=10)
        #make_radiobuttons(self.__settings["doublequote"], markingoptions, 2, 3, self.update_settings)


        Label(fileformatsettingsframe, text="Quoting").grid(column=1, row=5, sticky=E)
        quotingopt = {
            "minimal": 0,
            "all": 1,
            "non numeric": 2,
            "none": 3
        }
        self.__settings["quoting"] = IntVar()
        for i, (key, value) in enumerate(quotingopt.items()):
            Radiobutton(fileformatsettingsframe,
                        text=key,
                        value=value,
                        variable=self.__settings["quoting"],
                        command=self.update_settings,
                        ).grid(column=2+i,
                               row=5,
                               padx=10,
                               sticky=W,
                               )

        Label(fileformatsettingsframe, text="Ignore spaces at beginning").grid(column=1, row=6, sticky=E)
        self.__settings["skipinitialspace"] = BooleanVar()
        self.__settings["skipinitialspace"].set(False)
        Checkbutton(fileformatsettingsframe, variable=self.__settings["skipinitialspace"],
                    command=self.update_settings).grid(column=2, row=6, sticky=W, padx=10)

        fileformatsettingsframe.pack(fill=X)


        # ***---*** preview frame ***---***
        previewframe = LabelFrame(self.__root, text="Preview")
        self.__pdtable = Table(parent=previewframe, dataframe=self.__importer.dfx)
        self.__pdtable.show()
        previewframe.pack(fill='both', expand=True)

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
                self.__srcfileslistbox.insert(END, *names)
                self.__importer.update_files(*self.__srcfileslistbox.get(0, END))
            except AttributeError as _:
                showerror(title="Error", message="No .xsl file set")
            except ValueError as _:
                showerror(title="Error", message="Could not open files")
                self.__srcfileslistbox.delete(0, END)

            self.__update_table()
            self.__update_dialog()

    def remove_files(self):
        itemstodelete = self.__srcfileslistbox.curselection()
        if itemstodelete:
            for i in itemstodelete:
                self.__srcfileslistbox.delete(i)

            x = self.__srcfileslistbox.get(0,END)
            if x:
                self.__importer.update_files(*x)
            else:
                self.__importer.reset()
            self.__update_table()

    def remove_all(self):
        self.__srcfileslistbox.delete(0, END)
        self.__importer.reset()
        self.__update_table()

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

            self.__importer.set_settings(**changedsettings)
            self.__prevsettings = newsettings
            if not self.__importer.dfx.empty:
                self.__update_table()

    def ask_help(self):
        showinfo(title="Help",
                 message="To import files select Add Files\nTo export select Export and choose the desired format"
                 )

    def ask_about(self):
        showinfo(title="About",
                 message="Projektarbeit Python\nAuthor: Leo Schurrer\nDate: 19/12/20"
                 )


if __name__ == "__main__":
    Program().run()
