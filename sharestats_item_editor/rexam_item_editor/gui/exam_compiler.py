from os import getcwd
import PySimpleGUI as sg

from .. import __version__, APPNAME, consts
from ..rexam.item_database import ItemDatabase
from .json_settings import JSONSettings
from .dialogs import top_label
from ..rexam import exam

sg.theme_add_new("mytheme", consts.SG_COLOR_THEME)
sg.theme("mytheme")


class ExamCompiler(object):
    SHOW_HASHES = True

    def __init__(self, settings=None):

        if not isinstance(settings, JSONSettings):
            self.settings = JSONSettings(
                         appname=APPNAME.replace(" ", "_").lower(),
                         settings_file_name="settings.json",
                         defaults= {"recent_dirs": []},
                         reset=False)
        else:
            self.settings = settings

        self.txt_base_directory = sg.Text(self.base_directory, size=(60, 1),
                                          background_color=consts.COLOR_BKG_ACTIVE_INFO)
        self.it_exam = sg.InputText("", size=(20, 1),
                                    enable_events=True,
                                    background_color=consts.COLOR_BKG_ACTIVE_INFO,
                                    key="change_name")

        self.db = ItemDatabase(self.base_directory,
                       files_first_level=consts.FILELIST_FIRST_LEVEL_FILES,
                       files_second_level=consts.FILELIST_SECOND_LEVEL_FILES,
                       check_for_bilingual_files=True) # FIXME set check_for_bilingual_files

        self.exam = exam.Exam()
        self.tab_db = GUIItemTable(show_l2=True,  # TODO option in GUI
                                   n_row=3,
                                   show_hash=ExamCompiler.SHOW_HASHES,
                                   short_hashes=True,  # TODO option in GUI
                                   key='tab_database',
                                   tooltip='Item Database')
        self.tab_exam = GUIItemTable(show_l2=self.tab_db.show_l2,
                                     n_row=10,
                                     show_hash=ExamCompiler.SHOW_HASHES,
                                     short_hashes=self.tab_db.short_hashes,
                                     key='tab_exam',
                                     tooltip='Exam Items')

        self.txt_exam = sg.Multiline(size=(80, 30))

        self.layout = [
            [top_label([self.txt_base_directory,
                        sg.Button("change", size=(6, 1),
                                  key="change_directory")],
                       label="Database Directory",border_width=2),
             top_label([self.it_exam,
                        sg.Button("save", size=(12, 1), key="save_exam"),
                        sg.Button("load", size=(4, 1), key="load_exam"),
                        sg.Button("new", size=(4, 1), key="load_exam")
                        ],
                        label="Exam", border_width=2),
             ],

            [self.tab_db.gui_element],
            [
             sg.Button("add", size=(30, 2),
                       button_color= consts.COLOR_GREEN_BTN,
                       key="add_to_exam"),
            sg.Button("remove", size=(30, 2),
                      button_color=consts.COLOR_RED_BTN,
                      key="remove_from_exam"),
            sg.Button("up", size=(10, 2), key="move_up"),
            sg.Button("down", size=(10, 2), key="move_down")
            ],
            [self.tab_exam.gui_element, self.txt_exam]]

        self._unsaved_change = False


    @property
    def base_directory(self):
        try:
            return self.settings.recent_dirs[-1]
        except:
            return ""

    @base_directory.setter
    def base_directory(self, v):
        # update recent_dir list
        if len(self.settings.recent_dirs)>0 and v == self.settings.recent_dirs[-1]:
            return # nothing changes

        while True:
            try:
                self.settings.recent_dirs.remove(v)
            except:
                break
        self.settings.recent_dirs.append(v)
        self.settings.recent_dirs = self.settings.recent_dirs[
                                    -1 * consts.MAX_RECENT_DIRS:] #limit n elements
        #update db
        self.db = ItemDatabase(base_directory=v,
                   files_first_level=self.db.files_first_level,
                   files_second_level=self.db.files_second_level,
                   check_for_bilingual_files=self.db.check_for_bilingual_files)

    @property
    def exam_file(self):
        return self.it_exam.get()

    @exam_file.setter
    def exam_file(self, v):
        self.it_exam.update(value=v)
        self._unsaved_change = True


    def update_table(self, exam_tab_select_row=None):
        """table with item_id, name, short question l1 ,
           short question l2"""
        self.exam.item_database = self.db

        # exam
        db_ids = self.exam.get_database_ids(rm_nones=False)
        tmp = []
        for quest, idx in zip(self.exam.questions, db_ids):

            if idx is None:
                tmp.append(exam.EntryNotFound(quest, use_l2=True)) #FIXME set l2 bool
            else:
                tmp.append(self.db.entries[idx])

        self.tab_exam.set_items(items=tmp)
        # not in exam --> show in database
        tmp = [x for x in self.db.selected_entries \
                                if x.id not in db_ids]
        self.tab_db.set_items(items=tmp)

        if exam_tab_select_row is not None:
            self.tab_exam.set_selected(exam_tab_select_row)

        md = self.exam.markdown()
        self.txt_exam.update(value=md)


    def load_exam(self, json_filename):
        self.save_exam(ask=True)
        try:
            self.exam.load(json_filename)
        except Exception as e:
            return e

        self.exam_file = json_filename
        self.update_table()
        self._unsaved_change = False
        return True

    def save_exam(self, ask=True):
        if self._unsaved_change:
            self.exam.save(self.exam_file) # FIXME ASK
            self._unsaved_change = False

    def reset_gui(self):
        self.update_table(exam_tab_select_row=None)

    def run(self):

        win = sg.Window("{} ({})".format("Exam Compiler", __version__),
                        self.layout, finalize=True,
                        return_keyboard_events=True,
                        enable_close_attempted_event=True)

        if len(self.settings.recent_dirs) == 0: # very first launch
            self.base_directory = getcwd()

        self.reset_gui()
        self.load_exam("demo.json") #FIXME

        while True:
            win.refresh()
            event, values = win.read()
            if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or \
                    event == "Close" or event is None:
                self.save_exam(ask=True)
                break

            elif event == "change_directory":
                fld = sg.PopupGetFolder(message="", no_window=True)
                if len(fld):
                    self.base_directory = fld
                self.reset_gui()

            elif event=="save_exam":
                self.save_exam(ask=False)

            elif event=="load_exam":
                pass # TODO

            elif event=="new_exam":
                pass # TODO

            elif event=="tab_database":
                selected_entry = self.tab_db.get_row(values[event][0])
                #TODO

            elif event=="tab_exam":
                selected_entry = self.tab_exam.get_row(values[event][0])
                #TODO

            elif event=="add_to_exam":
                try:
                    selected_entry = self.tab_db.get_row(values["tab_database"][0])
                except:
                    continue # nothing selected
                self.add_to_exam(selected_entry[0])
                self._unsaved_change = True

            elif event=="remove_from_exam":
                try:
                    selected_entry = self.tab_exam.get_row(values["tab_exam"][0])
                except:
                    continue # nothing selected
                self.remove_from_exam(selected_entry[0])
                self._unsaved_change = True

            elif event=="move_up":
                try:
                    selected_entry = values["tab_exam"][0]
                except:
                    continue # nothing selected
                self.exam.replace(selected_entry, selected_entry-1)
                self.update_table(exam_tab_select_row=selected_entry-1)
                self._unsaved_change = True

            elif event=="move_down":
                try:
                    selected_entry = values["tab_exam"][0]
                except:
                    continue # nothing selected
                self.exam.replace(selected_entry, selected_entry+1)
                self.update_table(exam_tab_select_row=selected_entry+1)
                self._unsaved_change = True

            elif event=="change_name":
                self._unsaved_change = True

            else:
                pass #print(event)

        win.close()
        self.save_exam(ask=True)
        self.settings.save()

    def add_to_exam(self, selected_entry):
        item = self.db.entries[selected_entry]
        self.exam.add_database_item(item)
        self.update_table()

    def remove_from_exam(self, selected_entry):
        item = self.db.entries[selected_entry]
        self.exam.remove_item(item)
        self.update_table()


class GUIItemTable(object):
    LANGUAGES = ("Dutch", "English")

    def __init__(self, n_row, key, tooltip, max_lines = 3,
                 show_l2 = False, show_hash=True, short_hashes=True):
        self.max_lines = max_lines
        self.show_hash = show_hash
        self.short_hashes = short_hashes
        self.show_l2 = show_l2
        headings, width = self.get_headings()
        self.gui_element = sg.Table(values=[[""] * len(headings)],
                                    col_widths=width,
                                    headings=[str(x) for x in range(len(headings))],
                                    max_col_width=500,
                                    background_color='white',
                                    auto_size_columns=False,
                                    display_row_numbers=False,
                                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                                    justification='left',
                                    num_rows=n_row,
                                    # enable_events=True,
                                    bind_return_key=True,
                                    # alternating_row_color='lightyellow',
                                    key=key,
                                    row_height=40,
                                    vertical_scroll_only=False,
                                    tooltip=tooltip)

    def update_headings(self):
        w = self.gui_element.Widget
        if w is not None:
            for idx, txt in zip(self.gui_element.ColumnHeadings, self.get_headings()[0]):
                w.heading(idx, text=txt)

    def get_headings(self):
        headings = ["Cnt", "Name",
                    GUIItemTable.LANGUAGES[int(self.show_l2)]]
        width = [5, 10, 50]
        if self.show_hash:
            headings.append("Hash")
            width.append(10)
        return headings, width

    def get_row(self, row_num):
        return self.gui_element.get()[row_num]

    def set_items(self, items):
        values = []
        for x in items:
            d = [x.id]
            d.extend(x.short_repr(self.max_lines,
                                  use_l2=self.show_l2,
                                  add_versions=self.show_hash,
                                  short_version=self.short_hashes)) # TODO short hashes
            values.append(d)
        self.gui_element.update(values=values)
        self.update_headings()

    def set_selected(self, selected):
        if not isinstance(selected, (list, tuple)):
            selected = [selected]
        self.gui_element.update(select_rows=selected)