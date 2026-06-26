import wx
import json
languages = {}
language_display_names = {}
current_language = None
main_frame = None
notebook_control = None
tabs_menu = None
ID_SAVE = None
ID_IMPORT_TAB = None
ID_LANGUAGE = None
ID_NEW_TAB = None
ID_RENAME_TAB = None
ID_CLOSE_TAB = None
def load_languages():
    global languages, language_display_names
    try:
        with open("english.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
            languages["english"] = data
            language_display_names["english"] = data.get("language_name", "English")
    except:
        pass
    try:
        with open("persian.json", "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
            languages["persian"] = data
            language_display_names["persian"] = data.get("language_name", "Persian")
    except:
        pass
def get_text(key, default=""):
    if current_language in languages:
        return languages[current_language].get(key, default)
    return default
def show_language_dialog(parent):
    if not languages:
        return None
    display_list = [language_display_names[k] for k in languages.keys()]
    dialog = wx.Dialog(parent, title=get_text("select_language_title", "Select Language"))
    panel = wx.Panel(dialog)
    vertical_sizer = wx.BoxSizer(wx.VERTICAL)
    vertical_sizer.Add(wx.StaticText(panel, label=get_text("language_label", "Language:")), 0, wx.ALL, 5)
    combo_box = wx.ComboBox(panel, choices=display_list, style=wx.CB_READONLY)
    if current_language and current_language in language_display_names:
        combo_box.SetStringSelection(language_display_names[current_language])
    elif display_list:
        combo_box.SetSelection(0)
    vertical_sizer.Add(combo_box, 0, wx.EXPAND | wx.ALL, 5)
    button_sizer = wx.BoxSizer(wx.HORIZONTAL)
    ok_button = wx.Button(panel, wx.ID_OK, get_text("ok", "OK"))
    cancel_button = wx.Button(panel, wx.ID_CANCEL, get_text("cancel", "Cancel"))
    button_sizer.Add(ok_button, 0, wx.ALL, 5)
    button_sizer.Add(cancel_button, 0, wx.ALL, 5)
    vertical_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)
    panel.SetSizer(vertical_sizer)
    dialog.Fit()
    if dialog.ShowModal() == wx.ID_OK:
        selected_display = combo_box.GetValue()
        for key, display in language_display_names.items():
            if display == selected_display:
                dialog.Destroy()
                return key
    dialog.Destroy()
    return None
def create_accelerators():
    entries = [
        (wx.ACCEL_CTRL, ord('S'), ID_SAVE),
        (wx.ACCEL_CTRL, ord('N'), ID_NEW_TAB),
        (wx.ACCEL_CTRL, ord('I'), ID_IMPORT_TAB),
    ]
    main_frame.SetAcceleratorTable(wx.AcceleratorTable(entries))
def rebuild_tabs_menu():
    global tabs_menu
    menu_items = tabs_menu.GetMenuItems()
    for item in menu_items:
        tabs_menu.DestroyItem(item)
    tabs_menu.Append(ID_NEW_TAB, get_text("new_tab_menu", "&New Tab\tCtrl+N"))
    tabs_menu.Append(ID_IMPORT_TAB, get_text("import_tab_menu", "&Import Tab\tCtrl+I"))
    tabs_menu.Append(ID_SAVE, get_text("save_tab_menu", "&Save Tab\tCtrl+S"))
    tabs_menu.Append(ID_RENAME_TAB, get_text("rename_tab_menu", "&Rename Tab"))
    tabs_menu.Append(ID_CLOSE_TAB, get_text("close_tab_menu", "&Close Tab"))
    tabs_menu.AppendSeparator()
    for index in range(notebook_control.GetPageCount()):
        tab_name = notebook_control.GetPageText(index)
        menu_id = wx.NewIdRef()
        tabs_menu.Append(menu_id, tab_name)
        main_frame.Bind(wx.EVT_MENU, lambda event, idx=index: notebook_control.SetSelection(idx), id=menu_id)
def add_tab():
    dialog = wx.TextEntryDialog(
        main_frame,
        get_text("new_tab_dialog_message", "Enter tab name"),
        get_text("new_tab_dialog_title", "New Tab"),
        get_text("untitled_default", "Untitled")
    )
    if dialog.ShowModal() != wx.ID_OK:
        dialog.Destroy()
        return
    tab_name = dialog.GetValue().strip()
    if not tab_name:
        tab_name = get_text("untitled_default", "Untitled")
    dialog.Destroy()
    text_control = wx.TextCtrl(notebook_control, style=wx.TE_MULTILINE)
    text_control.SetName(get_text("note_taker_input", "Note"))
    notebook_control.AddPage(text_control, tab_name)
    rebuild_tabs_menu()
    notebook_control.SetSelection(notebook_control.GetPageCount() - 1)
def get_current_editor():
    page = notebook_control.GetCurrentPage()
    if isinstance(page, wx.TextCtrl):
        return page
    return None
def on_import_tab(event=None):
    with wx.FileDialog(
        main_frame,
        get_text("import_file_dialog_title", "Import Text File"),
        wildcard=get_text("import_wildcard", "Text files (*.txt)|*.txt|All files (*.*)|*.*"),
        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    ) as file_dialog:
        if file_dialog.ShowModal() == wx.ID_CANCEL:
            return
        file_path = file_dialog.GetPath()
        try:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                content = file_handle.read()
            import os
            tab_name = os.path.splitext(os.path.basename(file_path))[0]
            text_control = wx.TextCtrl(notebook_control, style=wx.TE_MULTILINE)
            text_control.SetName(get_text("note_taker_input", "Note"))
            text_control.SetValue(content)
            notebook_control.AddPage(text_control, tab_name)
            notebook_control.SetSelection(notebook_control.GetPageCount() - 1)
            rebuild_tabs_menu()
        except Exception as error:
            wx.MessageBox(str(error), get_text("error_title", "Error"))
def on_save(event=None):
    editor = get_current_editor()
    if not editor:
        return
    with wx.FileDialog(
        main_frame,
        get_text("save_file_dialog_title", "Save note"),
        wildcard=get_text("save_wildcard", "Text files (*.txt)|*.txt"),
        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
    ) as file_dialog:
        if file_dialog.ShowModal() == wx.ID_CANCEL:
            return
        file_path = file_dialog.GetPath()
        try:
            with open(file_path, "w", encoding="utf-8") as file_handle:
                file_handle.write(editor.GetValue())
            wx.MessageBox(get_text("save_success_message", "File saved successfully"))
        except Exception as error:
            wx.MessageBox(str(error), get_text("error_title", "Error"))
def on_language(event=None):
    global current_language
    if not languages:
        return
    display_list = [language_display_names[k] for k in languages.keys()]
    dialog = wx.Dialog(main_frame, title=get_text("select_language_title", "Select Language"))
    panel = wx.Panel(dialog)
    vertical_sizer = wx.BoxSizer(wx.VERTICAL)
    vertical_sizer.Add(wx.StaticText(panel, label=get_text("language_label", "Language:")), 0, wx.ALL, 5)
    combo_box = wx.ComboBox(panel, choices=display_list, style=wx.CB_READONLY)
    if current_language and current_language in language_display_names:
        combo_box.SetStringSelection(language_display_names[current_language])
    elif display_list:
        combo_box.SetSelection(0)
    vertical_sizer.Add(combo_box, 0, wx.EXPAND | wx.ALL, 5)
    button_sizer = wx.BoxSizer(wx.HORIZONTAL)
    ok_button = wx.Button(panel, wx.ID_OK, get_text("ok", "OK"))
    cancel_button = wx.Button(panel, wx.ID_CANCEL, get_text("cancel", "Cancel"))
    button_sizer.Add(ok_button, 0, wx.ALL, 5)
    button_sizer.Add(cancel_button, 0, wx.ALL, 5)
    vertical_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)
    panel.SetSizer(vertical_sizer)
    dialog.Fit()
    if dialog.ShowModal() == wx.ID_OK:
        selected_display = combo_box.GetValue()
        for key, display in language_display_names.items():
            if display == selected_display:
                current_language = key
                break
    dialog.Destroy()
def on_new_tab(event=None):
    add_tab()
def on_rename_tab(event=None):
    page_index = notebook_control.GetSelection()
    if page_index == wx.NOT_FOUND:
        return
    current_name = notebook_control.GetPageText(page_index)
    dialog = wx.TextEntryDialog(
        main_frame,
        get_text("rename_tab_dialog_message", "Enter new tab name"),
        get_text("rename_tab_dialog_title", "Rename Tab"),
        current_name
    )
    if dialog.ShowModal() == wx.ID_OK:
        new_name = dialog.GetValue().strip()
        if new_name:
            notebook_control.SetPageText(page_index, new_name)
            rebuild_tabs_menu()
    dialog.Destroy()
def on_close_tab(event=None):
    page_index = notebook_control.GetSelection()
    if page_index != wx.NOT_FOUND:
        notebook_control.DeletePage(page_index)
        rebuild_tabs_menu()
        if notebook_control.GetPageCount() == 0:
            add_tab()
def on_tab_context_menu(event):
    context_menu = wx.Menu()
    new_id = wx.NewIdRef()
    import_id = wx.NewIdRef()
    rename_id = wx.NewIdRef()
    save_id = wx.NewIdRef()
    close_id = wx.NewIdRef()
    context_menu.Append(new_id, get_text("context_new_tab", "New Tab"))
    context_menu.Append(import_id, get_text("context_import_tab", "Import Tab"))
    context_menu.Append(rename_id, get_text("context_rename_tab", "Rename Tab"))
    context_menu.Append(save_id, get_text("context_save_tab", "Save Tab"))
    context_menu.Append(close_id, get_text("context_close_tab", "Close Tab"))
    main_frame.Bind(wx.EVT_MENU, on_new_tab, id=new_id)
    main_frame.Bind(wx.EVT_MENU, on_import_tab, id=import_id)
    main_frame.Bind(wx.EVT_MENU, on_rename_tab, id=rename_id)
    main_frame.Bind(wx.EVT_MENU, on_save, id=save_id)
    main_frame.Bind(wx.EVT_MENU, on_close_tab, id=close_id)
    main_frame.PopupMenu(context_menu)
    context_menu.Destroy()
def create_menu():
    global ID_SAVE, ID_IMPORT_TAB, ID_LANGUAGE, ID_NEW_TAB, ID_RENAME_TAB, ID_CLOSE_TAB, tabs_menu
    menu_bar = wx.MenuBar()
    file_menu = wx.Menu()
    ID_SAVE = wx.NewIdRef()
    file_menu.Append(ID_SAVE, get_text("save_menu", "&Save\tCtrl+S"))
    ID_IMPORT_TAB = wx.NewIdRef()
    file_menu.Append(ID_IMPORT_TAB, get_text("import_menu", "&Import\tCtrl+I"))
    options_menu = wx.Menu()
    ID_LANGUAGE = wx.NewIdRef()
    options_menu.Append(ID_LANGUAGE, get_text("select_language_menu", "Select &Language"))
    tabs_menu = wx.Menu()
    ID_NEW_TAB = wx.NewIdRef()
    ID_RENAME_TAB = wx.NewIdRef()
    ID_CLOSE_TAB = wx.NewIdRef()
    menu_bar.Append(file_menu, get_text("file_menu", "&File"))
    menu_bar.Append(options_menu, get_text("options_menu", "&Options"))
    menu_bar.Append(tabs_menu, get_text("tabs_menu", "&Tabs"))
    main_frame.SetMenuBar(menu_bar)
    main_frame.Bind(wx.EVT_MENU, on_save, id=ID_SAVE)
    main_frame.Bind(wx.EVT_MENU, on_language, id=ID_LANGUAGE)
    main_frame.Bind(wx.EVT_MENU, on_new_tab, id=ID_NEW_TAB)
    main_frame.Bind(wx.EVT_MENU, on_import_tab, id=ID_IMPORT_TAB)
    main_frame.Bind(wx.EVT_MENU, on_rename_tab, id=ID_RENAME_TAB)
    main_frame.Bind(wx.EVT_MENU, on_close_tab, id=ID_CLOSE_TAB)
def create_main_frame(initial_language):
    global main_frame, notebook_control, current_language
    current_language = initial_language
    main_frame = wx.Frame(None, title=get_text("window_title", "note taker"), size=(800, 600))
    panel = wx.Panel(main_frame)
    main_sizer = wx.BoxSizer(wx.VERTICAL)
    notebook_control = wx.Notebook(panel)
    main_sizer.Add(notebook_control, 1, wx.EXPAND)
    panel.SetSizer(main_sizer)
    create_menu()
    create_accelerators()
    add_tab()
    notebook_control.Bind(wx.EVT_CONTEXT_MENU, on_tab_context_menu)
    main_frame.Show()
def main():
    global current_language
    application = wx.App()
    load_languages()
    if languages:
        chosen = show_language_dialog(None)
        if chosen is not None:
            current_language = chosen
        else:
            current_language = list(languages.keys())[0]
    else:
        current_language = None
    create_main_frame(current_language)
    application.MainLoop()
if __name__ == "__main__":
    main()