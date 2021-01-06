from codecs import escape_decode
from io import StringIO
from tkinter import Menu, Listbox, Text, StringVar, BooleanVar, IntVar
from tkinter.constants import E, W, X, END
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
from tkinter.messagebox import showerror, showinfo
from tkinter.ttk import Combobox, Frame, LabelFrame, Button, Label, Radiobutton, Checkbutton, Entry, Scrollbar

from pandas import DataFrame
from pandastable import Table, TableModel
from ttkthemes import ThemedTk

from csvxmlimporter import CsvXmlImporter

# list of encodings that can be detected by chardet
encodings = (
    "Big5", "GB2312", "GB18030", "EUC-TW", "HZ-GB-2312", "ISO-2022-CN", "EUC-JP", "SHIFT_JIS", "ISO-2022-JP", "EUC-KR",
    "ISO-2022-KR", "KOI8-R", "MacCyrillic", "IBM855", "IBM866", "ISO-8859-5", "windows-1251", "ISO-8859-2",
    "windows-1250", "ISO-8859-5", "windows-1251", "ISO-8859-1", "windows-1252", "ISO-8859-7", "windows-1253",
    "ISO-8859-8", "windows-1255", "TIS-620", "UTF-32", "UTF-16", "UTF-8", "ascii")

theme = "equilux"


class Program:
    """Exampleprogram to show possible usage of the model csvxmlImporter"""
    __importer: CsvXmlImporter

    def __init__(self):
        self.__settings = {}
        self.__importer = CsvXmlImporter()

        self.__root = ThemedTk(theme=theme)
        self.__root.title("Csv/Xml Importer")
        self.__root.minsize(560, 1)
        menu = Menu(self.__root)
        self.__root.config(menu=menu)

        filemenu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=filemenu)
        menu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit)

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
        self.__srcfileslistbox = Listbox(srcfilesframe, selectmode="extended", width=100, height=5)
        self.__srcfileslistbox.grid(column=2, row=1)

        Label(srcfilesframe, text="Encoding").grid(column=1, row=2, sticky=E)
        self.__settings["encoding"] = StringVar()
        self.__settings["encoding"].trace_add("write", self.update_settings)
        encCombobox = Combobox(srcfilesframe, textvariable=self.__settings["encoding"], values=encodings,
                               state="readonly")
        encCombobox.bind("<FocusOut>", self.update_settings)
        encCombobox.grid(column=2, row=2, pady=10)
        srcfilesframe.pack(fill=X)

        # ***---*** xsl file dialog ***---***
        xslfileframe = LabelFrame(self.__root, text="XSL-File")
        Button(xslfileframe, text="Add .xsl", command=self.add_xslfile).grid(column=1, row=1)
        self.__xsllistbox = Listbox(xslfileframe, width=100, height=1)
        self.__xsllistbox.grid(column=2, row=1, sticky="w")
        buttonframe = Frame(xslfileframe)
        Button(buttonframe, text="Apply Parameter", command=self.apply_xslparameter).pack(fill=X)
        Button(buttonframe, text="Restore Default", command=self.reset_xslparameter).pack(fill=X)
        buttonframe.grid(column=1, row=2)
        box = Frame(xslfileframe)
        self.__xslparametertext = Text(box, height=3, width=75)
        self.__xslparametertext.grid(column=0, row=1, sticky="nsew")
        scrollbar = Scrollbar(box, command=self.__xslparametertext.yview)
        scrollbar.grid(column=0, row=1, sticky="nse")
        box.grid(column=2, row=2, sticky="we")
        self.__xslparametertext["yscrollcommand"] = scrollbar.set
        xslfileframe.pack(fill=X)

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
        self.__settings["delimiter"].trace_add("write", lambda *_: limit_character(self.__settings["delimiter"]))
        seperatorentry.bind("<Return>", self.update_settings)
        seperatorentry.bind("<FocusOut>", self.update_settings)
        seperatorentry.grid(column=2, row=1, sticky=W, padx=15)

        Label(fileformatsettingsframe, text="Quotechar").grid(column=1, row=2, sticky=E)
        self.__settings["quotechar"] = StringVar()
        quotecharentry = Entry(fileformatsettingsframe, textvariable=self.__settings["quotechar"], width=1)
        self.__settings["quotechar"].trace_add("write", lambda *_: limit_character(self.__settings["quotechar"]))
        quotecharentry.bind("<Return>", self.update_settings)
        quotecharentry.bind("<FocusOut>", self.update_settings)
        quotecharentry.grid(column=2, row=2, sticky=W, padx=15)

        Label(fileformatsettingsframe, text="Doublequote").grid(column=1, row=3, sticky=E)
        self.__settings["doublequote"] = BooleanVar()
        Checkbutton(fileformatsettingsframe, variable=self.__settings["doublequote"],
                    command=self.update_settings).grid(column=2, row=3, sticky=W, padx=10)

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
                        ).grid(column=2 + i,
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
        previewframe.pack(fill="both", expand=True)

        # ***---*** export button ***---***
        exportframe = LabelFrame(self.__root, text="Export")
        Button(exportframe, text="Export", command=self.create_exportdialog).pack()
        exportframe.pack(fill="both", expand=True)

        # save settings to check for changes on update
        self.__prevsettings = self.__unpack_settings(self.__settings)

    def run(self):
        self.__root.mainloop()

    def exit(self):
        self.__root.destroy()

    def add_files(self):
        names = askopenfilenames(
            title="Select .csv or .xml files",
            filetypes=(("any", "*.*"), ("Csv File", "*.csv"), ("Xml File", "*.xml"))
        )
        if names:
            try:
                self.__srcfileslistbox.insert(END, *names)
                self.__importer.update_files(*self.__srcfileslistbox.get(0, END))
            except AttributeError as e:
                showerror(title="Error", message="No .xsl file set")
                raise e
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

            x = self.__srcfileslistbox.get(0, END)
            if x:
                self.__importer.update_files(*x)
            else:
                self.__importer.reset()
            self.__update_table()

    def remove_all(self):
        self.__srcfileslistbox.delete(0, END)
        self.__importer.reset()
        self.__update_table()

    def add_xslfile(self):
        filename = askopenfilename(
            title="Select .xsl file",
            filetypes=(("Xsl File", "*.xsl"),)
        )
        if filename:
            self.__importer.set_xslfile(filename)
            self.__xsllistbox.insert(0, filename)
            self.reset_xslparameter()

    def apply_xslparameter(self):
        """apply_xslparameter reads userinput from textbox and parses input in dict"""
        param = self.__xslparametertext.get("1.0", END)
        with StringIO(param) as f:
            lines = [line[:-1] for line in f.readlines()]
            # escape_decode removes extra escapes added through reading the text
            d = {x.split("=")[0]: escape_decode(x.split("=")[1])[0] for x in lines if x}
            self.__importer.set_xslparameter(**d)
        if not self.__importer.dfx.empty:
            self.__importer.update_files()
            self.__update_table()

    def reset_xslparameter(self):
        self.__xslparametertext.delete("1.0", END)
        param = self.__importer.get_xslparameter(default=True)
        s = ""
        for key, item in param.items():
            s += repr(key + "=" + item)[1:-1] + '\n'
        self.__xslparametertext.insert("1.0", s)

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
                 message="""\
    To import files select Add Files
    For .xml import first add a .xsl file.
    To export select Export and set desired parameters\
    """
                 )

    def ask_about(self):
        showinfo(title="About",
                 message="Projektarbeit Python\nAuthor: Leo Schurrer\nDate: 19/12/20"
                 )

    def create_exportdialog(self):
        self.ExportDialog(self.__importer.dfx).run()

    class ExportDialog:
        def __init__(self, df: DataFrame):
            self.__root = ThemedTk(theme=theme)
            self.__root.title("Export")
            self.__df = df

            frame = Frame(self.__root)
            Label(frame, text="Seperator").grid(column=1, row=1)
            self.__separator = StringVar(self.__root, value=",")
            Entry(frame, textvariable=self.__separator).grid(column=2, row=1)

            Label(frame, text="Encoding").grid(column=1, row=2)
            self.__encoding = StringVar(self.__root, value="UTF-8")
            Combobox(frame, textvariable=self.__encoding, values=encodings, state="readonly").grid(column=2, row=2)
            frame.pack(fill="both", expand=True)

            frame = Frame(self.__root)
            Button(frame, text="Save", command=self.export_csv).pack()
            frame.pack(fill="both", expand=True)

        def run(self):
            self.__root.mainloop()

        def exit(self):
            self.__root.destroy()

        def export_csv(self):
            e = self.__encoding.get()
            s = self.__separator.get()
            destination = asksaveasfilename(defaultextension=".csv", filetypes=(("Csv File", "*.csv"),),
                                            initialfile="export.csv")
            if destination:
                try:
                    self.__df.to_csv(destination, sep=s, encoding=e)
                except ValueError:
                    showerror(text="Oops. Something went wrong. Please try again.")
                finally:
                    self.exit()


if __name__ == "__main__":
    Program().run()
