from os import path, getcwd
import PySimpleGUI as sg

from .. import __version__, APPNAME
from ..rexam.rmd_file import RmdFile, CODE_L1, CODE_L2
from ..rexam.item_database import ItemFileList
from ..rexam.r_render import RPY2INSTALLED
from ..rexam.item import RExamItem, AnswerList
from . import dialogs, consts
from .json_settings import JSONSettings
from .item_gui import ItemGUI
from .log import log

sg.theme_add_new("mytheme", consts.SG_COLOR_THEME)
sg.theme("mytheme")

LANG1_EVENT_PREFIX = "Lang1"
LANG2_EVENT_PREFIX = "Lang2"

class MainWin(object):

    def __init__(self, reset_settings=False, change_meta_info_button=False,
                 two_languages=None): # FIXME languiages to settings and GUI

        """languages is none or a list of two strings indicating the
        respective languages languages"""

        self.settings = JSONSettings(
                         appname=APPNAME.replace(" ", "_").lower(),
                         settings_file_name="settings.json",
                         defaults= {"recent_dirs": []},
                         reset=reset_settings)

        if isinstance(two_languages, (tuple, list)) and len(two_languages) == 2:
            self.is_bilingual = True
        elif two_languages is None:
            self.is_bilingual = False
            two_languages = ("File", "")
        else:
            raise RuntimeError("The parameter languages ha to be a tuple of "
                               "two string or None.")

        # remove not existing recent dirs
        existing_dirs =  list(filter(path.isdir, self.settings.recent_dirs))
        if len(existing_dirs) != len(self.settings.recent_dirs):
            self.settings.recent_dirs = existing_dirs
            self.settings.save()

        # LAYOUT

        self.ig_l1 = ItemGUI(two_languages[0], LANG1_EVENT_PREFIX, change_meta_info_button)
        self.ig_l2 = ItemGUI(two_languages[1], LANG2_EVENT_PREFIX, change_meta_info_button,
                             disabled=not self.is_bilingual)

        self.lb_items = sg.Listbox(values=[], enable_events=True,
                                   key="lb_files", size=(30, 39))

        self.txt_item_cnt = sg.Text("...", size=(28, 1))
        self.fr_items = sg.Frame("Items", [
            [self.txt_item_cnt],
            [self.lb_items],
            [sg.Button(button_text="<<", size=(11, 1), key="btn_previous"),
             sg.Button(button_text=">>", size=(11, 1), key="btn_next")]])

        self.btn_save = sg.Button(button_text="Save", size=(28, 2),
                                  disabled=True,
                                  key="save")

        self.txt_base_directory = sg.Text(self.base_directory, size=(60, 1),
                                          background_color=consts.COLOR_BKG_ACTIVE_INFO)
        fr_base_dir = sg.Frame("Database Directory",
                             [[self.txt_base_directory]])

        self.txt_name = sg.Text("", size=(30, 1),
                                background_color=consts.COLOR_BKG_ACTIVE_INFO)
        self.btn_rename = sg.Button(button_text="Rename", size=(10, 1),
                                    key="rename")
        self.btn_second_lang = sg.Button(button_text="Add Language",
                                         size=(10, 1), disabled=True,
                                    key="second_lang")
        fr_item_name = sg.Frame("Item Name",
                             [[self.txt_name,
                              self.btn_rename,
                               self.btn_second_lang]])

        fr_btns =sg.Frame("", [[self.btn_save]])
        left_frame = sg.Frame("", [[self.fr_items], [fr_btns]],
                              border_width=0)

        self.menu = sg.Menu(menu_definition=self.menu_definition(),
                            tearoff=False)

        if self.is_bilingual:
            right_frames = [self.ig_l1.main_frame, self.ig_l2.main_frame]
        else:
            right_frames = [self.ig_l1.main_frame]

        self.layout = [
                  [self.menu],
                  [fr_base_dir, fr_item_name],
                  [left_frame]+ right_frames]

        self.fl_list = ItemFileList(files_first_level=consts.FILELIST_FIRST_LEVEL_FILES,
                                    files_second_level=consts.FILELIST_SECOND_LEVEL_FILES,
                                    check_for_bilingual_files=self.is_bilingual)
        self._unsaved_item = None

    def menu_definition(self):
        file = ['&New Item', '&Save Item', '---',
                'Open &Directory',
                'Recent', list(reversed(self.settings.recent_dirs[:-1])),
                '---', '&Reload Item List',
                '---', 'C&lose']
        view = ["&Raw files", "---", '&About']
        menu = [['&File', file], ["&View", view]]

        if  RPY2INSTALLED:
            d_inactive, e_inactive = "", ""
            if not self.ig_l1.is_activated():
                d_inactive="!"
            if not self.ig_l2.is_activated():
                e_inactive = "!"
            rmenu = ["&Render", ["{}&Dutch Version::render".format(d_inactive),
                            "{}&English Version::render".format(e_inactive)]]
            menu = menu[0], rmenu, menu[1]

        return menu

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
    def idx_selected_item(self):
        try:
            return self.lb_items.get_indexes()[0]
        except:
            return None

    @idx_selected_item.setter
    def idx_selected_item(self, index):
        n = len(self.lb_items.get_list_values())
        if n<=0:
            return
        elif index<0:
           index = 0
        elif index > n-1:
            index = n-1
        self.lb_items.update(set_to_index=index)
        self.load_selected_item()

    def select_item_by_filename(self, item_name):
        """select by file name"""

        idx = self.fl_list.find_filename(item_name)
        if idx is not None:
            self.idx_selected_item = idx

        return idx

    @property
    def unsaved_item(self):
        return self._unsaved_item

    @unsaved_item.setter
    def unsaved_item(self, v):
        self._unsaved_item = v
        self.btn_save.update(disabled=v is None)

    def update_name(self):
        if self.idx_selected_item is not None:
            #update name
            names = self.fl_list.get_shared_names(bilingual_tag=False)
            self.txt_name.update(value=names[self.idx_selected_item])
            self.btn_rename.update(disabled=False)
            if self.fl_list.files[self.idx_selected_item].is_bilingual():
                self.btn_second_lang.update(disabled=True)
            else:
                self.btn_second_lang.update(disabled=False)
        else:
            self.txt_name.update(value="")
            self.btn_rename.update(disabled=True)
            self.btn_second_lang.update(disabled=True)

        # dir information
        self.txt_base_directory.update(value=self.base_directory)

    def update_item_list(self):
        if not path.isdir(self.base_directory):
            self.base_directory = sg.PopupGetFolder("Please select item directory:",
                title="{} ({})".format(APPNAME, __version__))
            if not path.isdir(self.base_directory):
                sg.PopupError("No valid item directory selected.")
                exit()

        self.fl_list = ItemFileList(folder=self.base_directory,
                        files_first_level=consts.FILELIST_FIRST_LEVEL_FILES,
                        files_second_level=consts.FILELIST_SECOND_LEVEL_FILES,
                        check_for_bilingual_files=self.is_bilingual)

        cnt = self.fl_list.get_count()
        self.fr_items.update(value="{} items".format(cnt["total"]))

        >>>   HIER WEITER, counter in biligual is incorrect and en file are
        not displaed <<<<

        cnt_txt = "{} {}, {} {}, {} {}/{}".format(
             cnt[CODE_L1], CODE_L1,
             cnt[CODE_L2], CODE_L2,
             cnt["bilingual"], CODE_L1, CODE_L2)
        if cnt["undef"] > 0:
            cnt_txt += ", {} undef".format(cnt["undef"])
        self.txt_item_cnt.update(value=cnt_txt)

        list_display = self.fl_list.get_shared_names()
        self.lb_items.update(values=list_display)

    def reset_gui(self, select_by_filename=None):

        if select_by_filename:
            selected_file = select_by_filename
        else:
            try:
                selected_file = self.fl_list.files[
                                    self.idx_selected_item].rmd_item.filename
            except:
                selected_file = None

        self.update_item_list()
        self.ig_l1.rexam_item = None
        self.ig_l2.rexam_item = None
        self.ig_l2.update_gui()
        self.ig_l1.update_gui()
        self.menu.update(menu_definition=self.menu_definition())
        self.update_name()
        self.unsaved_item = None

        if selected_file is not None:
            self.select_item_by_filename(selected_file)


    def run(self):
        win = sg.Window("{} ({})".format(APPNAME, __version__),
                        self.layout, finalize=True, return_keyboard_events=True,
                        enable_close_attempted_event=True)

        if len(self.settings.recent_dirs) == 0: # very first launch
            self.base_directory = getcwd()

        self.reset_gui()
        self.idx_selected_item = 0

        while True:
            win.refresh()
            event, values = win.read(timeout=5000)
            if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or \
                    event == "Close" or event is None:
                self.save_items(ask=True)
                break

            elif event.startswith(LANG1_EVENT_PREFIX) or event.startswith(LANG2_EVENT_PREFIX):
                #ItemGUI event
                self.process_item_gui_event(event, values)

                if self.unsaved_item is None: # if change in any text boxes
                    self.unsaved_item = self.idx_selected_item

            self.process_event(event, values)

        win.close()
        self.settings.save()

    def process_item_gui_event(self, event, values):
        # ItemGUI events have to start with LANG1_PREFIX or LANG2_PREFIX
        is_l1_event = event.startswith(LANG1_EVENT_PREFIX)
        if not self.is_bilingual or is_l1_event:
            ig = self.ig_l1
        else:
            ig = self.ig_l2

        if event.endswith("dd_types"):
            ig.update_item()
            ig.rexam_item.meta_info.type = values[event]
            ig.rexam_item.meta_info.sort_parameter()
            ig.update_gui()

        elif event.endswith("btn_add_answer_list"):
            ig.rexam_item.question.add_answer_list_section()
            ig.update_gui()

        elif event.endswith("btn_add_feedback_list"):
            ig.rexam_item.solution.add_answer_list_section()
            ig.update_gui()

        elif event.endswith("_answer"):
            ig.update_answer_list_button()

        elif event.endswith("btn_update_exsolution"):
            ig.update_item()
            ig.rexam_item.update_solution(solution_str= \
                AnswerList.extract_solution(
                    ig.ml_answer.get()))
            ig.update_gui()

        elif event.endswith("btn_fix_meta_issues"):
            ig.update_item()
            for i in ig.rexam_item.validate():
                i.fix()
                if i.fix_requires_gui_reset:
                    if isinstance(i.fix_requires_gui_reset, str):
                        self.reset_gui(select_by_filename=i.fix_requires_gui_reset)
                    else:
                        self.reset_gui()
                    return
            ig.update_gui()


    def process_event(self, event, values):

        if event == "__TIMEOUT__":
            if self.fl_list.is_file_list_changed():
                self.save_items(ask=True, info_text=
                        "Changes in base directory detected.")
                self.reset_gui()

        elif event in ("lb_files", "btn_next", "btn_previous"):
            self.save_items(ask=True)
            if event == "btn_next":
                if self.idx_selected_item is None:
                    self.idx_selected_item = 0
                else:
                    self.idx_selected_item += 1
            elif event == "btn_previous":
                if self.idx_selected_item is None:
                    self.idx_selected_item = 0
                else:
                    self.idx_selected_item -= 1

            else: # selected
                self.load_selected_item()

        elif event == "Open Directory" or event in self.settings.recent_dirs:
            self.save_items(ask=True)
            if event == "Open Directory":
                fld = sg.PopupGetFolder(message="", no_window=True)
                if len(fld):
                    self.base_directory = fld
            else:
                self.base_directory = event  # from recent dir submenu
            self.reset_gui()

        elif event == "save" or event == "Save Item":
            self.save_items(ask=False)

        elif event == "New Item":
            self.new_item()

        elif event == "About":
            dialogs.about()

        elif event == "Reload Item List":
            self.reset_gui()

        elif event == "rename":
            self.rename()

        elif event == "second_lang":
            self.save_items()
            self.add_second_language()

        elif event == "Raw files":
            try:
                flns = self.fl_list.files[self.idx_selected_item]
            except:
                return
            self.save_items(ask=True)
            dialogs.show_text_file(flns.rmd_item, flns.rmd_translation)

        elif event.endswith("render"):
            try:
                flns = self.fl_list.files[self.idx_selected_item]
            except:
                return
            if event.startswith("Dutch"):
                fl = flns.rmd_item
            else:
                fl = flns.rmd_translation
            if fl is not None:
                self.save_items(ask=True)
                dialogs.render(fl)

    def load_selected_item(self):
        if self.idx_selected_item is None:
            return

        try:
            fls = self.fl_list.files[self.idx_selected_item]
        except:
            fls = None

        if fls is not None:
            if not fls.is_bilingual() and fls.rmd_item.language_code == CODE_L2:
                self.ig_l2.rexam_item = RExamItem.load(fls.rmd_item.full_path,
                                                       base_directory = self.base_directory)
                self.ig_l1.rexam_item = None
            else:
                self.ig_l1.rexam_item = RExamItem.load(fls.rmd_item.full_path,
                                                       base_directory = self.base_directory)

                if fls.rmd_translation is not None:
                    self.ig_l2.rexam_item = RExamItem.load(
                                    fls.rmd_translation.full_path,
                                    base_directory=self.base_directory)
                else:
                    self.ig_l2.rexam_item = None

        self.ig_l2.update_gui()
        self.ig_l1.update_gui()
        self.update_name()
        self.menu.update(menu_definition=self.menu_definition())

    def save_items(self, ask=False, info_text=None):
        if self.unsaved_item is not None:
            if ask:
                item_name = self.lb_items.get_list_values()[self.unsaved_item]
                if not dialogs.ask_save(item_name, txt = info_text):
                    self.unsaved_item = None
                    return
            self.ig_l1.save_item()
            self.ig_l2.save_item()
            self.unsaved_item = None

    def new_item(self, new_rmd_file_name = None):
        if new_rmd_file_name is None:
            new_items = dialogs.new_item(self.base_directory)
        else:
            assert (isinstance(new_rmd_file_name, str))
            new_items = [RExamItem(RmdFile(new_rmd_file_name,
                                base_directory=self.base_directory)), None]
            if self.ig_l2.rexam_item is not None:
                new_items[1] = self.ig_l2.rexam_item
            elif self.ig_l1.rexam_item is not None:
                new_items[1] = self.ig_l1.rexam_item

        if new_items[0] is not None:
            self.save_items()
            fl_name = new_items[0].filename
            for n in new_items:
                if n is not None:
                    n.save()

            self.ig_l1.rexam_item = new_items[0]
            self.ig_l2.rexam_item = new_items[1] # FIXME no biligual new items
            if self.ig_l1.rexam_item.language_code == CODE_L2:
                self.ig_l1.rexam_item, self.ig_l2.rexam_item = \
                    self.ig_l2.rexam_item, self.ig_l1.rexam_item # swap
            self.update_item_list()

            self.select_item_by_filename(fl_name)
            self.ig_l2.update_gui()
            self.ig_l1.update_gui()
            self.update_name()
            self.menu.update(menu_definition=self.menu_definition())

    def add_second_language(self):
            ifln = self.fl_list.files[self.idx_selected_item].rmd_item
            fl_path = ifln.get_other_language_rmdfile()
            copy_content = sg.popup_yes_no("Copy content of {}?".format(
                        ifln.name))
            if copy_content == "Yes":
                new_name = RmdFile(fl_path).name
                new = ifln.copy_subdir_files(new_name)
                if not isinstance(new, RmdFile):
                    # io error
                    log(new)
                    self.reset_gui()
                    return
                self.reset_gui()
            else:
                self.new_item(fl_path)

    def rename(self):
        n1, n2, fix_dir = dialogs.rename_item(self.lb_items.get()[0])
        if n1 is not None:
            self.save_items(ask=False)

            flns = self.fl_list.files[self.idx_selected_item]
            add_language = len(n2) and not flns.is_bilingual()
            # rename
            for new_name, old in zip((n1, n2),
                                     (flns.rmd_item,
                                      flns.rmd_translation)):
                if new_name is not None and old is not None:
                    log(old.rename(new_name,
                                   new_sub_dir=new_name,
                                   rename_on_disk=True))
                    # TODO optional sub_dir renaming

            self.reset_gui()
            self.select_item_by_filename(n1 + RmdFile.SUFFIX)
            if add_language:
                self.add_second_language()
                self.reset_gui()
                self.select_item_by_filename(n1 + RmdFile.SUFFIX)
