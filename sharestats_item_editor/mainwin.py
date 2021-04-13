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
        self.ig_nl = ItemGUI("nl")
        self.ig_en = ItemGUI("en")
        self.lb_items = sg.Listbox(values=[], enable_events=True,
                                   key="lb_files", size=(30, 37))

        fr_items = sg.Frame("Item list", [
            [self.lb_items],
            [sg.Button(button_text="<<", size=(11, 1), key="btn_previous"),
             sg.Button(button_text=">>", size=(11, 1), key="btn_next")]])

        fr_btns =sg.Frame("", [
            [sg.Button(button_text="New", size=(28, 2), key="new")],
            [sg.Button(button_text="Save", size=(28, 2), key="save")],
            [sg.CloseButton(button_text="Close", size=(28, 2))]])

        self.it_base_directory = sg.InputText(self.base_directory, size=(60, 1),
                                            key="it_base_dir",  disabled=True,
                                            enable_events=True)
        top_frame = sg.Frame("Directory",
                             [[self.it_base_directory,
                              sg.FolderBrowse(initial_folder=self.base_directory)]])

        self.it_name = sg.InputText("", size=(30, 1), disabled=False,
                                    key="it_name", enable_events=False)

        top_frame2 = sg.Frame("Item Name",
                             [[self.it_name,
                              sg.Button(button_text="Rename", size=(10, 1),
                                        key="rename")]])

        left_frame = sg.Frame("", [[fr_items], [fr_btns]],
                              border_width=0)

        self.layout = [[top_frame, top_frame2],
                  [left_frame,
                   self.ig_nl.get_frame("Dutch"),
                   self.ig_en.get_frame("English")]]

        self.fl_list_bilingual = files.FileListBilingual()
        self.unsaved_item = None

    @property
    def base_directory(self):
        if settings.base_directory is None:
            settings.base_directory = os.getcwd()
        return settings.base_directory

    @base_directory.setter
    def base_directory(self, v):
        if v != settings.base_directory:
            settings.base_directory = v

            self.update_item_list()

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

    def update_name(self):
        if self.idx_selected_item is not None:
            #update name
            names = self.fl_list_bilingual.get_shared_names(bilingual_tag=False)
            self.it_name.update(value=names[self.idx_selected_item])
        else:
            self.it_name.update(value="")

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

        self.resit_gui()
        self.idx_selected_item = 0
        self.load_selected_item()

        while True:
            win.refresh()
            event, values = win.read()
            if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event is None:
                self.save_items(ask=True)
                break

            if event=="it_base_dir":
                self.save_items(ask=True)
                self.base_directory = values[event]
                self.resit_gui()

            elif event== "save":
                self.save_items(ask=False)

            elif event=="new":
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

            elif event.startswith("nl_") or event.startswith("en_"):
                # ItemGUI events
                is_nl_event = event.startswith("nl_")
                if is_nl_event:
                    ig = self.ig_nl
                else:
                    ig = self.ig_en

                if event.endswith("dd_types"):
                    ig.ss_item.meta_info.type = values[event]
                    ig.update_gui()

                elif event.endswith("btn_change_meta"):
                    new_meta = dialogs.taxonomy(ig.ss_item.meta_info)
                    if new_meta is not None:
                        ig.ss_item.meta_info = new_meta
                        ig.ml_metainfo.update(value=new_meta.str_parameter +
                                                    new_meta.str_text)

                elif event.endswith("btn_add_answer_list"):
                    ig.ss_item.question.add_answer_list_section()
                    ig.update_gui()

                elif event.endswith("btn_add_feedback_list"):
                    ig.ss_item.solution.add_answer_list_section()
                    ig.update_gui()

                elif event.endswith("_answer"):
                    ig.update_answer_list_button()

                elif event.endswith("btn_update_exsolution"):
                    ig.ss_item.update_solution(solution_str= \
                            AnswerList.extract_solution(ig.ml_answer.get()))
                    ig.update_gui()

                elif event.endswith("btn_fix_meta_issues"):
                    needs_gui_reset = False
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

        # processing
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
                txt = self.ig_nl.as_markdown_file()
                self.ig_nl.ss_item.parse(txt)
                self.ig_nl.ss_item.save()
                self.ig_nl.update_gui()
            if self.ig_en.ss_item is not None:
                txt = self.ig_en.as_markdown_file()
                self.ig_en.ss_item.parse(txt)
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

#FIXME update solution (save, before refresh)