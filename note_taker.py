import wx
import json
import os
import glob

class LanguageDialog(wx.Dialog):
    def __init__(self, parent, languages, current_language):
        super().__init__(parent, title="Select Language")

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(wx.StaticText(panel, label="Language:"), 0, wx.ALL, 5)

        self.combo = wx.ComboBox(panel, choices=languages, style=wx.CB_READONLY)
        if current_language in languages:
            self.combo.SetStringSelection(current_language)
        elif languages:
            self.combo.SetSelection(0)

        sizer.Add(self.combo, 0, wx.EXPAND | wx.ALL, 5)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ok_btn = wx.Button(panel, wx.ID_OK, "OK")
        cancel_btn = wx.Button(panel, wx.ID_CANCEL, "Cancel")

        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)

        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)

        panel.SetSizer(sizer)
        self.Fit()

    def get_language(self):
        return self.combo.GetValue()

class NoteFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="note taker", size=(800, 600))

        self.languages = {}
        self.current_language = None

        self.load_languages()

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.notebook = wx.Notebook(panel)
        sizer.Add(self.notebook, 1, wx.EXPAND)

        panel.SetSizer(sizer)

        self.create_menu()
        self.create_accelerators()

        self.add_tab()

        if self.languages:
            self.current_language = list(self.languages.keys())[0]

        self.notebook.Bind(wx.EVT_CONTEXT_MENU, self.on_tab_context_menu)

        self.Show()

    def load_languages(self):
        for filename in glob.glob("*.json"):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    self.languages[os.path.splitext(filename)[0]] = json.load(f)
            except Exception:
                pass

    def get_text(self, key, default=""):
        if self.current_language in self.languages:
            return self.languages[self.current_language].get(key, default)
        return default

    def create_menu(self):
        menubar = wx.MenuBar()

        file_menu = wx.Menu()
        self.ID_SAVE = wx.NewIdRef()
        file_menu.Append(self.ID_SAVE, "&Save\tCtrl+S")
        self.ID_IMPORT_TAB = wx.NewIdRef()
        file_menu.Append(self.ID_IMPORT_TAB, "&Import\tCtrl+I")

        options_menu = wx.Menu()
        self.ID_LANGUAGE = wx.NewIdRef()
        options_menu.Append(self.ID_LANGUAGE, "Select &Language")

        tabs_menu = wx.Menu()
        self.tabs_menu = tabs_menu
        self.ID_NEW_TAB = wx.NewIdRef()
        tabs_menu.Append(self.ID_NEW_TAB, "&New Tab\tCtrl+N")

        tabs_menu.Append(self.ID_IMPORT_TAB, "&Import Tab\tCtrl+I")

        tabs_menu.Append(self.ID_SAVE, "&Save Tab\tCtrl+S")

        self.ID_RENAME_TAB = wx.NewIdRef()
        tabs_menu.Append(self.ID_RENAME_TAB, "&Rename Tab")

        self.ID_CLOSE_TAB = wx.NewIdRef()
        tabs_menu.Append(self.ID_CLOSE_TAB, "&Close Tab")

        menubar.Append(file_menu, "&File")
        menubar.Append(options_menu, "&Options")
        menubar.Append(tabs_menu, "&Tabs")

        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.on_save, id=self.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_language, id=self.ID_LANGUAGE)
        self.Bind(wx.EVT_MENU, self.on_new_tab, id=self.ID_NEW_TAB)
        self.Bind(wx.EVT_MENU, self.on_import_tab, id=self.ID_IMPORT_TAB)
        self.Bind(wx.EVT_MENU, self.on_rename_tab, id=self.ID_RENAME_TAB)
        self.Bind(wx.EVT_MENU, self.on_close_tab, id=self.ID_CLOSE_TAB)

    def create_accelerators(self):
        entries = [
            (wx.ACCEL_CTRL, ord('S'), self.ID_SAVE),
            (wx.ACCEL_CTRL, ord('N'), self.ID_NEW_TAB),
            (wx.ACCEL_CTRL, ord('I'), self.ID_IMPORT_TAB),
        ]
        self.SetAcceleratorTable(wx.AcceleratorTable(entries))

    def rebuild_tabs_menu(self):
        menu_items = self.tabs_menu.GetMenuItems()
        for item in menu_items:
            self.tabs_menu.DestroyItem(item)

        self.tabs_menu.Append(
            self.ID_NEW_TAB,
            "&New Tab\tCtrl+N"
        )

        self.tabs_menu.Append(
            self.ID_IMPORT_TAB,
            "&Import Tab\tCtrl+I"
        )

        self.tabs_menu.Append(
            self.ID_SAVE,
            "&Save Tab\tCtrl+S"
        )

        self.tabs_menu.Append(
            self.ID_RENAME_TAB,
            "&Rename Tab"
        )

        self.tabs_menu.Append(
            self.ID_CLOSE_TAB,
            "&Close Tab"
        )

        self.tabs_menu.AppendSeparator()

        for i in range(self.notebook.GetPageCount()):
            tab_name = self.notebook.GetPageText(i)

            menu_id = wx.NewIdRef()

            self.tabs_menu.Append(
                menu_id,
                tab_name
            )

            self.Bind(
                wx.EVT_MENU,
                lambda event, index=i:
                    self.notebook.SetSelection(index),
                id=menu_id
            )

    def add_tab(self):
        dlg = wx.TextEntryDialog(
            self,
            "Enter tab name",
            "New Tab",
            "Untitled"
        )

        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        tab_name = dlg.GetValue().strip()

        if not tab_name:
            tab_name = "Untitled"

        dlg.Destroy()

        text = wx.TextCtrl(
            self.notebook,
            style=wx.TE_MULTILINE
        )

        text.SetName("Note")

        self.notebook.AddPage(text, tab_name)
        self.rebuild_tabs_menu()
        self.notebook.SetSelection(
            self.notebook.GetPageCount() - 1
        )

    def get_current_editor(self):
        page = self.notebook.GetCurrentPage()
        if isinstance(page, wx.TextCtrl):
            return page
        return None

    def on_import_tab(self, event=None):

        with wx.FileDialog(
            self,
            self.get_text("import text file", "Import Text File"),
            wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as dlg:

            if dlg.ShowModal() == wx.ID_CANCEL:
                return

            path = dlg.GetPath()

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                tab_name = os.path.splitext(
                    os.path.basename(path)
                )[0]

                text = wx.TextCtrl(
                    self.notebook,
                    style=wx.TE_MULTILINE
                )

                text.SetName(
                    self.get_text("note taker input", "Note")
                )

                text.SetValue(content)

                self.notebook.AddPage(
                    text,
                    tab_name
                )

                self.notebook.SetSelection(
                    self.notebook.GetPageCount() - 1
                )

                self.rebuild_tabs_menu()

            except Exception as e:
                wx.MessageBox(str(e), "Error")

    def on_save(self, event):
        editor = self.get_current_editor()
        if not editor:
            return

        with wx.FileDialog(
            self,
            "Save note",
            wildcard="Text files (*.txt)|*.txt",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as dlg:

            if dlg.ShowModal() == wx.ID_CANCEL:
                return

            path = dlg.GetPath()

            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(editor.GetValue())

                msg = self.get_text("save success", "File saved successfully")
                wx.MessageBox(msg)

            except Exception as e:
                wx.MessageBox(str(e), "Error")

    def on_language(self, event):
        langs = list(self.languages.keys())

        dlg = LanguageDialog(self, langs, self.current_language)

        if dlg.ShowModal() == wx.ID_OK:
            self.current_language = dlg.get_language()

        dlg.Destroy()

    def on_new_tab(self, event=None):
        self.add_tab()

    def on_rename_tab(self, event=None):
        page = self.notebook.GetSelection()

        if page == wx.NOT_FOUND:
            return

        current_name = self.notebook.GetPageText(page)

        dlg = wx.TextEntryDialog(
            self,
            "Enter new tab name",
            "Rename Tab",
            current_name
        )

        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg.GetValue().strip()

            if new_name:
                self.notebook.SetPageText(page, new_name)
                self.rebuild_tabs_menu()

        dlg.Destroy()

    def on_close_tab(self, event=None):
        page = self.notebook.GetSelection()

        if page != wx.NOT_FOUND:
            self.notebook.DeletePage(page)
            self.rebuild_tabs_menu()

            if self.notebook.GetPageCount() == 0:
                self.add_tab()

    def on_tab_context_menu(self, event):
        menu = wx.Menu()

        new_id = wx.NewIdRef()
        import_id = wx.NewIdRef()
        rename_id = wx.NewIdRef()
        save_id = wx.NewIdRef()
        close_id = wx.NewIdRef()

        menu.Append(new_id, "New Tab")
        menu.Append(import_id, "Import Tab")
        menu.Append(rename_id, "Rename Tab")
        menu.Append(save_id, "Save Tab")
        menu.Append(close_id, "Close Tab")

        self.Bind(wx.EVT_MENU, self.on_new_tab, id=new_id)
        self.Bind(wx.EVT_MENU, self.on_import_tab, id=import_id)
        self.Bind(wx.EVT_MENU, self.on_rename_tab, id=rename_id)
        self.Bind(wx.EVT_MENU, self.on_save, id=save_id)
        self.Bind(wx.EVT_MENU, self.on_close_tab, id=close_id)

        self.PopupMenu(menu)
        menu.Destroy()

app = wx.App()
frame = NoteFrame()
app.MainLoop()
