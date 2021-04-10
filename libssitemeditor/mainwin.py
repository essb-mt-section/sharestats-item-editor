import os
from . import __version__, consts, files, settings
from .sharestats_item import ShareStatsItem
from .item_sections import AnswerList
from .dialogs import sg
from . import dialogs

WIDTH_ML = 80 # multi line field for text input
LEN_ML = 6
LEN_ANSWER_ML = 5

_EMPTY_ITEM = ShareStatsItem(None)


class MainWin(object):


    def __init__(self):
        sg.theme('SystemDefault1')

        # LAYOUT
        self.ig_nl = _ItemGUI("nl")
        self.ig_en = _ItemGUI("en")
        self.lb_files = sg.Listbox(values=[], enable_events=True,
                                   key="lb_files", size=(30, 37))

        fr_files = sg.Frame("Files", [
            [self.lb_files],
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

        left_frame = sg.Frame("", [[fr_files], [fr_btns]],
                              border_width=0)

        self.layout = [[top_frame, top_frame2],
                  [left_frame,
                   self.ig_nl.get_frame("Dutch"),
                   self.ig_en.get_frame("English")]]

        self.ss_item_nl = None
        self.ss_item_en = None
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

    def update_item_gui(self, en):

        if en:
            ig = self.ig_en
            item = self.ss_item_en
        else:
            ig = self.ig_nl
            item = self.ss_item_nl

        ig.enable=item is not None
        if item is None:
            item = _EMPTY_ITEM
        else:
            names = self.fl_list_bilingual.get_shared_names(bilingual_tag=False)
            self.it_name.update(value=names[self.idx_selected_item])


        ig.ml_quest.update(value=item.question.str_text)
        ig.ml_solution.update(value=item.solution.str_text)

        ig.ml_metainfo.update(value=item.meta_info.str_parameter +
                                item.meta_info.str_text)

        if not item.meta_info.check_type():
            t = consts.UNKNOWN_TYPE
        else:
            t = item.meta_info.type
        ig.dd_types.update(value=t)

        if not item.question.has_answer_list_section():
            ig.ml_answer.update(value="")
        else:
            ig.ml_answer.update(value=
                        item.question.answer_list.get_str_answers_marked() +
                        item.question.answer_list.str_text)


        if not item.solution.has_answer_list_section():
            ig.ml_solution_answ_lst.update(value="")
        else:
            ig.ml_solution_answ_lst.update(value=
                        item.solution.answer_list.str_answers +
                        item.solution.answer_list.str_text)
        ig.set_enable_answer_list(item.question.has_answer_list_section())
        ig.set_enable_feedback_list(item.solution.has_answer_list_section())
        self.update_answer_list_button(en)

        # info window
        txt = ""
        if len(item.filename.directory):
            x = os.listdir(item.filename.directory)
            x.remove(item.filename.filename)
            if len(x):
                txt += "Files: {}\n\n".format(", ".join(x))

        txt += item.validate_meta_info()
        ig.ml_info_validation(value=txt)



    def update_item_list(self, select_item=None):
        if not os.path.isdir(self.base_directory):
            self.base_directory = sg.PopupGetFolder("Please select item directory:",
                title="{} ({})".format(consts.APPNAME, __version__))
            if not os.path.isdir(self.base_directory):
                sg.PopupError("No valid item directory selected.")
                exit()

        self.fl_list_bilingual = files.FileListBilingual(self.base_directory)
        list_display = self.fl_list_bilingual.get_shared_names()
        self.lb_files.update(values=list_display)
        try:
            self.idx_selected_item = list_display.index(select_item)
        except:
            pass

    @property
    def idx_selected_item(self):
        try:
            return self.lb_files.get_indexes()[0]
        except:
            return None

    @idx_selected_item.setter
    def idx_selected_item(self, index):
        n = len(self.lb_files.get_list_values())
        if n<=0:
            return
        elif index<0:
           index = 0
        elif index > n-1:
            index = n-1
        self.lb_files.update(set_to_index=index)

    def resit_gui(self):
        self.update_item_list()
        self.ss_item_nl = None
        self.ss_item_en = None
        self.update_item_gui(en=False)
        self.update_item_gui(en=True)
        self.it_name.update(value="")
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

            if self.unsaved_item is None and \
                    (event.startswith("nl_") or event.startswith("en_")):
                # if change in any text boxes
                self.unsaved_item = self.idx_selected_item

            is_nl_event = event.startswith("nl_")

            if event=="it_base_dir":
                self.save_items(ask=True)
                self.base_directory = values[event]
                self.resit_gui()

            elif event== "save":
                self.save_items(ask=False)

            elif event=="new":
                self.new_item()

            elif event=="rename":
                n1, n2, fix_dir= dialogs.rename_item(self.lb_files.get()[0])
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

            elif event.endswith("dd_types"):
                if is_nl_event:
                    self.ss_item_nl.meta_info.type = values[event]
                    self.update_item_gui(en=False)

                else:
                    self.ss_item_en.meta_info.type = values[event]
                    self.update_item_gui(en=True)

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

            elif event.endswith("btn_change_meta"):
                if is_nl_event:
                    item = self.ss_item_nl
                    ig = self.ig_nl
                else:
                    item = self.ss_item_en
                    ig = self.ig_en

                if item is not None:
                    new_meta = dialogs.taxonomy(item.meta_info)
                    if new_meta is not None:
                        item.meta_info = new_meta
                        ig.ml_metainfo.update(value= new_meta.str_parameter +
                                          new_meta.str_text)

            elif event.endswith("btn_add_answer_list"):
                if is_nl_event:
                    self.ss_item_nl.question.add_answer_list_section()
                    self.update_item_gui(en=False)
                else:
                    self.ss_item_en.question.add_answer_list_section()
                    self.update_item_gui(en=True)

            elif event.endswith("btn_add_feedback_list"):
                if is_nl_event:
                    self.ss_item_nl.solution.add_answer_list_section()
                    self.update_item_gui(en=False)
                else:
                    self.ss_item_en.solution.add_answer_list_section()
                    self.update_item_gui(en=True)

            elif event.endswith("_answer"):
                self.update_answer_list_button(en=not is_nl_event)

            elif event.endswith("btn_update_exsolution"):
                if is_nl_event:
                    self.ss_item_nl.update_solution(solution_str=\
                        AnswerList.extract_solution(self.ig_nl.ml_answer.get()))
                else:
                    self.ss_item_en.update_solution(solution_str=\
                        AnswerList.extract_solution(self.ig_en.ml_answer.get()))
                self.update_item_gui(en = not is_nl_event)

        # processing
        win.close()
        settings.save()

    def update_answer_list_button(self, en):
        # extract solution and switch visibility

        if en:
            item = self.ss_item_en
            ig = self.ig_en
        else:
            item = self.ss_item_nl
            ig = self.ig_nl

        if item is None or not item.question.has_answer_list_section():
            ig.btn_update_exsolution.update(visible=False)
            return

        solution = AnswerList.extract_solution(ig.ml_answer.get())
        ig.btn_update_exsolution.update(visible=
                                        item.meta_info.solution != solution)

    def load_selected_item(self):
        if self.idx_selected_item is None:
            return

        self.ss_item_nl = None
        self.ss_item_en = None
        fls = self.fl_list_bilingual.files[self.idx_selected_item]
        if fls[0] is not None and fls[0].get_language() == "en":
            fls = (fls[1], fls[0]) # swap

        if fls[0] is not None:
            self.ss_item_nl = ShareStatsItem(fls[0])
        if fls[1] is not None:
            self.ss_item_en = ShareStatsItem(fls[1])

        self.update_item_gui(en=True)
        self.update_item_gui(en=False)

    def save_items(self, ask=False):
        if self.unsaved_item is not None:

            if ask:
                item_name = self.lb_files.get_list_values()[self.unsaved_item]
                if not dialogs.ask_save(item_name):
                    self.unsaved_item = None
                    return

            if self.ss_item_nl is not None:
                txt = self.ig_nl.as_markdown_file()
                self.ss_item_nl.parse(txt)
                self.ss_item_nl.save()
                self.update_item_gui(en=False)
            if self.ss_item_en is not None:
                txt = self.ig_en.as_markdown_file()
                self.ss_item_en.parse(txt)
                self.ss_item_en.save()
                self.update_item_gui(en=True)

            self.unsaved_item = None

    def new_item(self):
        new_items = dialogs.new_item(self.base_directory)
        if new_items[0] is not None:
            self.save_items()  # TODO allow canceling new at this point
            # TODO check existing file and overriding
            self.ss_item_nl, self.ss_item_en = new_items
            fl_name = self.ss_item_nl.filename.filename
            if self.ss_item_nl.filename.get_language() == "en":
                self.ss_item_nl, self.ss_item_en = \
                                    self.ss_item_en, self.ss_item_nl # swap
            self.unsaved_item = -1 # any to force saving
            self.save_items(ask=False)  # create folder and file
            self.update_item_gui(en=True)
            self.update_item_gui(en=False)
            self.update_item_list()

            idx = self.fl_list_bilingual.find_filename(fl_name)
            if idx is not None:
                self.idx_selected_item = idx


class _ItemGUI(object):

    def __init__(self, key_prefix):
        self.ml_quest = sg.Multiline(default_text="",
                                     size=(WIDTH_ML, LEN_ML), enable_events=True,
                                     key="{}_quest".format(key_prefix))
        self.ml_answer = sg.Multiline(default_text="", enable_events=True,
                                      size=(WIDTH_ML, LEN_ANSWER_ML),
                                      key="{}_answer".format(key_prefix))

        self.txt_answer_list = sg.Text("Answer list", size=(10, 1),
                                       background_color=consts.COLOR_QUEST)

        self.ml_solution = sg.Multiline(default_text="", enable_events=True,
                                        size=(WIDTH_ML, LEN_ML),
                                        key="{}_solution".format(key_prefix))
        self.ml_solution_answ_lst = sg.Multiline(default_text="", enable_events=True,
                                                 size=(WIDTH_ML, LEN_ANSWER_ML),
                                                 key="{}_solution_feedback".format(key_prefix))
        self.txt_solution_answ_lst = sg.Text("Answer list", size=(10, 1),
                                             background_color=consts.COLOR_SOLUTION)

        self.ml_metainfo = sg.Multiline(default_text="",
                                        size=(WIDTH_ML, 10),  enable_events=True,
                                        key="{}_meta".format(key_prefix))

        self.btn_change_meta = sg.Button("Edit Meta Information",  enable_events=True,
                                         key="{}_btn_change_meta".format(key_prefix))

        self.ml_info_validation =sg.Multiline(default_text="",
                                              size=(WIDTH_ML, 5),
                                              background_color="#DADADA",
                                              disabled=True)

        self.dd_types = sg.DropDown(values=[consts.UNKNOWN_TYPE] +
                                           list(consts.EXTYPES.keys()),
                                    size=(10,1),  enable_events=True,
                                    key="{}_dd_types".format(key_prefix))

        self.btn_add_answer_list = sg.Button("+", enable_events=True,
                                             size=(2, 1),
                      key="{}_btn_add_answer_list".format(key_prefix))
        self.btn_add_feedback_list = sg.Button("+", enable_events=True,
                                            size=(2,1),
                    key="{}_btn_add_feedback_list".format(key_prefix))

        self.btn_update_exsolution = sg.Button("update 'exsolution'",
                                            enable_events=True,
                                            size=(15,1),
                    key="{}_btn_update_exsolution".format(key_prefix))

        self._enable = False

    @property
    def enable(self):
        return self._enable

    @enable.setter
    def enable(self, value):
        self._enable = value
        if value:
            col =  consts.COLOR_BKG_ACTIVE
        else:
            col = consts.COLOR_BKG_INACTIVE
        self.ml_quest.update(disabled=not value, background_color=col)
        self.ml_answer.update(disabled=not value, background_color=col)
        self.ml_solution.update(disabled=not value, background_color=col)
        self.ml_solution_answ_lst.update(disabled=not value,
                                         background_color=col)
        self.ml_metainfo.update(disabled=not value, background_color=col)
        self.dd_types.update(disabled=not value)
        self.btn_change_meta.update(disabled=not value)
        if not value:
            self.btn_add_answer_list.update(visible=False)
            self.btn_update_exsolution.update(visible=False)
            self.btn_add_feedback_list.update(visible=False)

    def set_enable_answer_list(self, enable):
        if enable:
            col =  consts.COLOR_BKG_ACTIVE
        else:
            col = consts.COLOR_BKG_INACTIVE
        self.ml_answer.update(disabled=not enable, background_color=col)

        if self._enable:
            self.btn_add_answer_list.update(visible=not enable)

    def set_enable_feedback_list(self, enable):
        if enable:
            col =  consts.COLOR_BKG_ACTIVE
        else:
            col = consts.COLOR_BKG_INACTIVE
        self.ml_solution_answ_lst.update(disabled=not enable,
                                         background_color=col)
        if self._enable:
            self.btn_add_feedback_list.update(visible=not enable)


    def get_frame(self, heading):
        layout_question =[[self.ml_quest],
                        [self.txt_answer_list, self.btn_add_answer_list,
                         self.btn_update_exsolution],
                        [self.ml_answer]]

        layout_solution = [[self.ml_solution],
                        [self.txt_solution_answ_lst, self.btn_add_feedback_list],
                        [self.ml_solution_answ_lst]]

        layout_meta_info =  [[self.ml_metainfo],
                        [self.dd_types, self.btn_change_meta]]

        return sg.Frame(heading, [
                    [sg.Frame("Question", layout_question ,
                              background_color=consts.COLOR_QUEST)],
                    [sg.Frame("Solution (feedback)", layout_solution,
                              background_color=consts.COLOR_SOLUTION)],
                    [sg.Frame("Meta-Information", layout_meta_info,
                              background_color=consts.COLOR_MATA_INFO)],
                    [sg.Frame("", [[self.ml_info_validation]])]
        ])

    def as_markdown_file(self):
        rtn = _EMPTY_ITEM.question.str_markdown_heading
        rtn += self.ml_quest.get().strip() + "\n\n"

        if len(self.ml_answer.get().strip())>0:
            rtn += AnswerList(_EMPTY_ITEM).str_markdown_heading
            rtn += self.ml_answer.get().strip() + "\n\n"

        rtn += _EMPTY_ITEM.solution.str_markdown_heading
        rtn += self.ml_solution.get().strip() + "\n\n"
        if len(self.ml_solution_answ_lst.get().strip())>0:
            rtn += AnswerList(_EMPTY_ITEM).str_markdown_heading
            rtn += self.ml_solution_answ_lst.get().strip() + "\n\n"

        rtn += _EMPTY_ITEM.meta_info.str_markdown_heading
        rtn += self.ml_metainfo.get().strip() + "\n"
        return rtn




