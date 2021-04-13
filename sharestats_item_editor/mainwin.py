import os
import PySimpleGUI as sg

from . import __version__, consts, files, settings, dialogs
from .sharestats_item import ShareStatsItem
from .item_sections import AnswerList
from .item_gui import ItemGUI

class MainWin(object):

    def __init__(self):
        sg.theme(consts.COLOR_THEME)

        # LAYOUT
        self.ig_nl = ItemGUI("Dutch", "nl")
        self.ig_en = ItemGUI("English", "en")

        self.lb_items = sg.Listbox(values=[], enable_events=True,
                                   key="lb_files", size=(30, 40))

        fr_items = sg.Frame("Item list", [
            [self.lb_items],
            [sg.Button(button_text="<<", size=(11, 1), key="btn_previous"),
             sg.Button(button_text=">>", size=(11, 1), key="btn_next")]])

        self.btn_save = sg.Button(button_text="Save", size=(28, 2),
                                  disabled=True, key="save")

        self.txt_base_directory = sg.Text(self.base_directory, size=(60, 1))
        fr_base_dir = sg.Frame("Base Directory",
                             [[self.txt_base_directory]])

        self.it_name = sg.InputText("", size=(30, 1), disabled=False,
                                    key="it_name", enable_events=False)
        fr_item_name = sg.Frame("Item",
                             [[sg.Text("Name:"),
                              self.it_name,
                              sg.Button(button_text="Rename", size=(10, 1),
                                        key="rename")]])

        fr_btns =sg.Frame("", [[self.btn_save]])
        left_frame = sg.Frame("", [[fr_items], [fr_btns]],
                              border_width=0)

        self.menu = sg.Menu(menu_definition=self.menu_definition(),
                            tearoff=False)
        self.layout = [
                  [self.menu],
                  [fr_base_dir, fr_item_name],
                  [left_frame,
                   self.ig_nl.main_frame,
                   self.ig_en.main_frame]]

        self.fl_list_bilingual = files.FileListBilingual()
        self._unsaved_item = None

    def menu_definition(self):
        recent_dirs =  list(reversed(settings.recent_dirs[:-1]))

        return ['&File', ['&New Item', '&Save Item', '---',
                                 'Open &Directory',
                                 'Recent', recent_dirs,
                                 '---',
                                 'C&lose']],   [
                       '&About', ['&About']]

    @property
    def base_directory(self):
        try:
            return settings.recent_dirs[-1]
        except:
            return ""

    @base_directory.setter
    def base_directory(self, v):
        # update recent_dir list
        if len(settings.recent_dirs)>0 and v == settings.recent_dirs[-1]:
            return # nothing changes

        while True:
            try:
                settings.recent_dirs.remove(v)
            except:
                break
        settings.recent_dirs.append(v)
        settings.recent_dirs = settings.recent_dirs[
                               -1*consts.MAX_RECENT_DIRS:] #limit n elements         self.update_item_list()

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
            names = self.fl_list_bilingual.get_shared_names(bilingual_tag=False)
            self.it_name.update(value=names[self.idx_selected_item])
        else:
            self.it_name.update(value="")

        # dir information
        self.txt_base_directory.update(value=self.base_directory)

    def update_item_list(self, select_item=None):
        if not os.path.isdir(self.base_directory):
            self.base_directory = sg.PopupGetFolder("Please select item directory:",
                title="{} ({})".format(consts.APPNAME, __version__))
            if not os.path.isdir(self.base_directory):
                sg.PopupError("No valid item directory selected.")
                exit()

        self.fl_list_bilingual = files.FileListBilingual(self.base_directory)
        list_display = self.fl_list_bilingual.get_shared_names()
        self.lb_items.update(values=list_display)
        try:
            self.idx_selected_item = list_display.index(select_item)
        except:
            pass

    def resit_gui(self):
        self.menu.update(menu_definition=self.menu_definition())
        self.update_item_list()
        self.ig_nl.ss_item = None
        self.ig_en.ss_item = None
        self.ig_en.update_gui()
        self.ig_nl.update_gui()
        self.update_name()
        self.unsaved_item = None

    def run(self):
        win = sg.Window("{} ({})".format(consts.APPNAME, __version__),
                        self.layout, finalize=True,
                        enable_close_attempted_event=True)

        if len(settings.recent_dirs) == 0: # very first launch
            self.base_directory = os.getcwd()

        self.resit_gui()
        self.idx_selected_item = 0
        self.load_selected_item()

        while True:
            win.refresh()
            event, values = win.read()
            if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or \
                    event =="Close" or event is None:
                self.save_items(ask=True)
                break

            if event.startswith("nl_") or event.startswith("en_"):
                # ItemGUI events
                is_nl_event = event.startswith("nl_")
                if is_nl_event:
                    ig = self.ig_nl
                else:
                    ig = self.ig_en

                if event.endswith("dd_types"):
                    ig.update_ss_item()
                    ig.ss_item.meta_info.type = values[event]
                    ig.ss_item.meta_info.sort_parameter()
                    ig.update_gui()

                elif event.endswith("btn_change_meta"):
                    ig.update_ss_item()
                    new_meta = dialogs.taxonomy(ig.ss_item.meta_info)
                    if new_meta is not None:
                        ig.ss_item.meta_info = new_meta
                        ig.ml_metainfo.update(value=new_meta.str_parameter +
                                                    new_meta.str_text)
                        ig.ss_item.meta_info.sort_parameter()


                elif event.endswith("btn_add_answer_list"):
                    ig.ss_item.question.add_answer_list_section()
                    ig.update_gui()

                elif event.endswith("btn_add_feedback_list"):
                    ig.ss_item.solution.add_answer_list_section()
                    ig.update_gui()

                elif event.endswith("_answer"):
                    ig.update_answer_list_button()

                elif event.endswith("btn_update_exsolution"):
                    ig.update_ss_item()
                    ig.ss_item.update_solution(solution_str= \
                            AnswerList.extract_solution(ig.ml_answer.get()))
                    ig.update_gui()

                elif event.endswith("btn_fix_meta_issues"):
                    needs_gui_reset = False
                    ig.update_ss_item()
                    for i in ig.ss_item.validate():
                        if str(i.fix_fnc).find("fix_directory_name")>=0:
                            needs_gui_reset = True
                        i.fix()
                    if needs_gui_reset:
                        self.resit_gui()
                    else:
                        ig.update_gui()

                if self.unsaved_item is None:
                    # if change in any text boxes
                    self.unsaved_item = self.idx_selected_item

            elif event in ("lb_files", "btn_next", "btn_previous"):
                self.save_items(ask=True)
                if event=="btn_next":
                    if self.idx_selected_item is None:
                        self.idx_selected_item = 0
                    else:
                        self.idx_selected_item +=1
                elif event=="btn_previous":
                    if self.idx_selected_item is None:
                        self.idx_selected_item = 0
                    else:
                        self.idx_selected_item -= 1
                self.load_selected_item()

            elif event=="Open Directory" or event in settings.recent_dirs:
                self.save_items(ask=True)
                if event=="Open Directory":
                    fld = sg.PopupGetFolder(message="", no_window=True)
                    if len(fld):
                        self.base_directory = fld
                else:
                    self.base_directory = event # from recent dir submenu
                self.resit_gui()

            elif event== "save" or event=="Save Item":
                self.save_items(ask=False)

            elif event=="New Item":
                self.new_item()

            elif event=="rename":
                n1, n2, fix_dir= dialogs.rename_item(self.lb_items.get()[0])
                if n1 is not None:
                    self.save_items(ask=True)

                for new_name, old in zip((n1, n2),
                                         self.fl_list_bilingual.files[self.idx_selected_item]):
                    if new_name is not None and old is not None:
                        new = old.copy()
                        new.name = new_name
                        os.rename(old.full_path, new.full_path)
                        if fix_dir:
                            new.fix_directory_name()
                            os.rename(old.directory, new.directory)
                self.resit_gui()

        win.close()
        settings.save()

    def load_selected_item(self):
        if self.idx_selected_item is None:
            return

        fls = self.fl_list_bilingual.files[self.idx_selected_item]
        if fls[0] is not None and fls[0].get_language() == "en":
            fls = (fls[1], fls[0]) # swap

        if fls[0] is not None:
            self.ig_nl.ss_item = ShareStatsItem(fls[0])
        else:
            self.ig_nl.ss_item = None
        if fls[1] is not None:
            self.ig_en.ss_item = ShareStatsItem(fls[1])
        else:
            self.ig_en.ss_item = None

        self.ig_en.update_gui()
        self.ig_nl.update_gui()
        self.update_name()

    def save_items(self, ask=False):
        if self.unsaved_item is not None:
            if ask:
                item_name = self.lb_items.get_list_values()[self.unsaved_item]
                if not dialogs.ask_save(item_name):
                    self.unsaved_item = None
                    return

            if self.ig_nl.ss_item is not None: # TODO can be simplified (move
                # to itemGUI
                self.ig_nl.update_ss_item()
                self.ig_nl.ss_item.save()
                self.ig_nl.update_gui()
            if self.ig_en.ss_item is not None:
                self.ig_en.update_ss_item()
                self.ig_en.ss_item.save()
                self.ig_en.update_gui()

            self.unsaved_item = None

    def new_item(self):
        new_items = dialogs.new_item(self.base_directory)
        if new_items[0] is not None:
            self.save_items()  # TODO allow canceling new at this point
            # TODO check existing file and overriding
            fl_name = new_items[0].filename.filename
            for n in new_items:
                if n is not None:
                    n.save()

            self.ig_nl.ss_item = new_items[0]
            self.ig_en.ss_item = new_items[1]
            if self.ig_nl.ss_item.filename.get_language() == "en":
                self.ig_nl.ss_item, self.ig_en.ss_item = \
                                    self.ig_en.ss_item, self.ig_nl.ss_item # swap
            self.update_item_list()

            idx = self.fl_list_bilingual.find_filename(fl_name)
            if idx is not None:
                self.idx_selected_item = idx

            self.ig_en.update_gui()
            self.ig_nl.update_gui()
            self.update_name()

#TODO update solution (save, before refresh)