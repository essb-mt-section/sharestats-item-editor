from os import getcwd
import PySimpleGUI as sg

from .. import __version__, APPNAME
from ..rexam.item_database import ItemDatabase
from ..rexam.exam import Exam
from . import consts
from .json_settings import JSONSettings
from .dialogs import top_label

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

        self.db = ItemDatabase(self.base_directory)
        self.exam = Exam()
        self.tab_db = None
        self.tab_exam = None
        self.short_hashes = True # TODO option in GUI
        self.tab_db = self._make_tab(n_row=3,key='tab_database',
                                     tooltip='Item Database' )
        self.tab_exam = self._make_tab(n_row=10, key='tab_exam',
                                       tooltip='Exam Items')
        self.layout = [
            [top_label([self.txt_base_directory,
                        sg.Button("change", size=(6, 1),
                                  key="change_directory")],
                       label="Database Directory",border_width=2),
             top_label([self.it_exam,
                        sg.Button("save", size=(12, 1),
                                  key="save_exam"),
                        sg.Button("load", size=(4, 1),
                                  key="load_exam"),
                        sg.Button("new", size=(4, 1),
                                  key="load_exam")
                        ],
                        label="Exam", border_width=2),
             ],

            [self.tab_db],
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
            [self.tab_exam]]

        self._unsaved_change = False


    def _make_tab(self, n_row, key, tooltip):
        headings = ["cnt", "Name", "Dutch", "English"]
        width = [2, 10, 50, 50]
        if ExamCompiler.SHOW_HASHES:
            headings.extend(["Hash Dutch", "Hash English"])
            width.extend([10]*2)

        return sg.Table(values=[[""] * len(headings)],
                               col_widths=width,
                               headings=headings,
                               max_col_width=500,
                               background_color='white',
                               auto_size_columns=False,
                               display_row_numbers=False,
                               select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                               justification='left',
                               num_rows=n_row,
                               #enable_events=True,
                               bind_return_key=True,
                               #alternating_row_color='lightyellow',
                               key=key,
                               row_height=40,
                               vertical_scroll_only = False,
                               tooltip=tooltip)


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
                                    -1 * consts.MAX_RECENT_DIRS:] #limit n elements         self.update_item_list()

    @property
    def exam_file(self):
        return self.it_exam.get()

    @exam_file.setter
    def exam_file(self, v):
        self.it_exam.update(value=v)
        self._unsaved_change = True


    def update_table(self, max_lines=2, exam_tab_select_row=None):
        """table with item_id, name, short question item,
           short question translation"""

        exam_question_ids = self.exam.get_database_ids(self.db)

        data = []
        for x in self.db.selected_entries:
            if x.id not in exam_question_ids:
                d = [x.id]
                d.extend(x.short_repr(max_lines,
                             add_versions=ExamCompiler.SHOW_HASHES,
                             short_version=self.short_hashes))
                data.append(d)
        self.tab_db.update(values=data)

        data = []
        for x in self.db.get_entries(exam_question_ids):
            d = [x.id]
            d.extend(x.short_repr(max_lines,
                            add_versions=ExamCompiler.SHOW_HASHES,
                            short_version=self.short_hashes))
            data.append(d)

        self.tab_exam.update(values=data)
        if exam_tab_select_row is not None:
            self.tab_exam.update(select_rows=[exam_tab_select_row])

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
        pass

    def run(self):

        win = sg.Window("{} ({})".format("Exam Compiler", __version__),
                        self.layout, finalize=True,
                        return_keyboard_events=True,
                        enable_close_attempted_event=True)

        if len(self.settings.recent_dirs) == 0: # very first launch
            self.base_directory = getcwd()

        self.update_table()
        self.reset_gui()

        self.load_exam("demo.json")

        while True:
            win.refresh()
            event, values = win.read(timeout=None)
            if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or \
                    event == "Close" or event is None:
                self.save_exam(ask=True)
                break

            elif event=="save_exam":
                self.save_exam(ask=False)

            elif event=="load_exam":
                pass # TODO

            elif event=="new_exam":
                pass # TODO

            elif event=="tab_database":
                selected_entry = self.tab_db.get()[values[event][0]]
                #TODO

            elif event=="tab_exam":
                selected_entry = self.tab_exam.get()[values[event][0]]
                #TODO

            elif event=="add_to_exam":
                try:
                    selected_entry = self.tab_db.get()[values["tab_database"][0]]
                except:
                    continue # nothing selected
                self.add_to_exam(selected_entry[0])
                self._unsaved_change = True


            elif event=="remove_from_exam":
                try:
                    selected_entry = self.tab_exam.get()[values["tab_exam"][0]]
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

