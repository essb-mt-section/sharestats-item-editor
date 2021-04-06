from os import path, getcwd
from . import __version__, consts, files, settings
from .sharestats_item import ShareStatsItem
from .item_sections import AnswerList
from .windows import sg
from . import windows

_EMPTY_ITEM = ShareStatsItem(None)
_EMPTY_ANSWERLIST = AnswerList(_EMPTY_ITEM)

class MainWindow(object):


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

        self.it_base_directory = sg.InputText(self.base_directory, size=(80, 1),
                                            key="it_base_dir",  disabled=True,
                                            enable_events=True)
        top_frame = sg.Frame("Item Directory",
                             [[self.it_base_directory,
                              sg.FolderBrowse(initial_folder=self.base_directory)]])

        left_frame = sg.Frame("", [[fr_files], [fr_btns]],
                              border_width=0)

        layout = [[top_frame],
                  [left_frame,
                   self.ig_nl.get_frame("Dutch"),
                   self.ig_en.get_frame("English")]]

        self.ss_item_nl = None
        self.ss_item_en = None
        self.file_list_bilingual = []
        self.unsaved_changes = False

        self.window = sg.Window("{} ({})".format(consts.APPNAME, __version__),
                                layout, finalize=True)

    @property
    def base_directory(self):
        if settings.base_directory is None:
            settings.base_directory = getcwd()
        return settings.base_directory

    @base_directory.setter
    def base_directory(self, v):
        if v != settings.base_directory:
            settings.base_directory = v
            self.update_files_list()

    def update_item_gui(self, en):

        if en:
            ig = self.ig_en
            item = self.ss_item_en
        else:
            ig = self.ig_nl
            item = self.ss_item_nl

        if item is None:
            item = _EMPTY_ITEM

        ig.ml_quest.update(value=item.question.str_text)
        ig.ml_solution.update(value=item.solution.str_text)

        ig.ml_metainfo.update(value=item.meta_info.str_parameter +
                                item.meta_info.str_text)
        ig.ml_info_validation(value="") # TODO VALIDATION SOMEWHEN LATER

        if not item.meta_info.check_type():
            t = consts.UNKNOWN_TYPE
        else:
            t = item.meta_info.type
        ig.dd_types.update(value=t)

        if not item.question.has_answer_list():
            ig.ml_answer.update(value="")
            ig.set_answer_list(False)
        else:
            ig.set_answer_list(True)
            ig.ml_answer.update(value=
                        item.question.answer_list.str_answers +
                        item.question.answer_list.str_text, disabled=True)
        if not item.solution.has_answer_list():
            ig.ml_solution_answ_lst.update(value="")
        else:
            ig.ml_solution_answ_lst.update(value=
                        item.solution.answer_list.str_answers +
                        item.solution.answer_list.str_text, disabled=False)

    def update_files_list(self, select_item=None):
        if not path.isdir(self.base_directory):
            self.base_directory = sg.PopupGetFolder("Please select item directory:",
                title="{} ({})".format(consts.APPNAME, __version__))
            if not path.isdir(self.base_directory):
                sg.PopupError("No valid item directory selected.")
                exit()

        self.file_list_bilingual = files.rmd_file_list_bilingual(self.base_directory)
        list_display = list(map(files.bilinguar_list_name, self.file_list_bilingual))
        self.lb_files.update(values=list_display)
        try:
            self.selected_file_index = list_display.index(select_item)
        except:
            pass

    @property
    def selected_file_index(self):
        try:
            return self.lb_files.get_indexes()[0]
        except:
            return None

    @selected_file_index.setter
    def selected_file_index(self, index):
        n = len(self.lb_files.get_list_values())
        if n<=0:
            return
        elif index<0:
           index = 0
        elif index > n-1:
            index = n-1
        self.lb_files.update(set_to_index=index)

    def run(self):
        self.update_files_list()
        self.update_item_gui(en=False)
        self.update_item_gui(en=True)
        self.unsaved_changes = False

        while True:
            self.window.refresh()
            event, values = self.window.read()
            if event is None:
                break

            if not self.unsaved_changes and (event.startswith("nl_") or
                                          event.startswith("en_")):
                # if change in any text boxes
                self.unsaved_changes = True

            if event == "close":
                break

            elif event == "nl_btn_change_meta":
                if self.ss_item_nl is not None:
                    new_tax = windows.taxonomy(self.ss_item_nl.meta_info)
                    if new_tax is not None:
                        self.ss_item_nl.meta_info = new_tax
                        self.ig_nl.ml_metainfo.update(value=
                                          new_tax.str_parameter +
                                          new_tax.str_text)

            elif event == "en_btn_change_meta":
                if self.ss_item_en is not None:
                    new_tax = windows.taxonomy(self.ss_item_en.meta_info)
                    if new_tax is not None:
                        self.ss_item_en.meta_info = new_tax
                        self.ig_en.ml_metainfo.update(value=
                                        new_tax.str_parameter +
                                        new_tax.str_text)

            elif event=="it_base_dir":
                self.base_directory = values[event]

            elif event== "save":
                self.save_items(ask=False)

            elif event=="new":
                self.new_item()

            elif event.endswith("dd_types"):
                if event.startswith("nl"):
                    self.ss_item_nl.meta_info.type = values[event]
                    self.ig_nl.ml_metainfo.update(value=
                                self.ss_item_nl.meta_info.str_parameter +
                                self.ss_item_nl.meta_info.str_text)

                if event.startswith("en"):
                    self.ss_item_en.meta_info.type = values[event]
                    self.ig_en.ml_metainfo.update(value=
                                      self.ss_item_en.meta_info.str_parameter +
                                      self.ss_item_en.meta_info.str_text)

            elif event in ("lb_files", "btn_next", "btn_previous"):
                if event=="btn_next":
                    if self.selected_file_index is None:
                        self.selected_file_index = 0
                    else:
                        self.selected_file_index +=1
                elif event=="btn_previous":
                    if self.selected_file_index is None:
                        self.selected_file_index = 0
                    else:
                        self.selected_file_index -= 1
                self.load_selected_item()

        # processing
        self.save_items()
        self.window.close()
        settings.save()

    def load_selected_item(self):
        if self.selected_file_index is None:
            return

        self.save_items()
        self.ss_item_nl = None
        self.ss_item_en = None
        fls = self.file_list_bilingual[self.selected_file_index]
        if fls[0] is not None:
            if fls[0].get_language() == "en":
                self.ss_item_en = ShareStatsItem(fls[0])
                self.ss_item_nl = ShareStatsItem(fls[1])
            else:
                self.ss_item_en = ShareStatsItem(fls[1])
                self.ss_item_nl = ShareStatsItem(fls[0])
            self.update_item_gui(en=True)
            self.update_item_gui(en=False)

    def save_items(self, ask=False):
        if self.unsaved_changes:
            if ask:
                # resp = windows.ask_save()
                #if resp == False:
                #    return
                pass # TODO

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
            self.unsaved_changes = False

    def new_item(self):
        new_items = windows.new_item(self.base_directory)
        if new_items[0] is not None:
            self.save_items()  # TODO allow canceling new at this point
            # TODO check existing file and overriding
            self.ss_item_nl, self.ss_item_en = new_items
            self.unsaved_changes = True
            fl_name = self.ss_item_nl.filename.filename
            if self.ss_item_nl.filename.get_language() == "en":
                self.ss_item_nl, self.ss_item_en = \
                                    self.ss_item_en, self.ss_item_nl # swap
            self.save_items(ask=False)  # create folder and file
            self.update_item_gui(en=True)
            self.update_item_gui(en=False)
            self.update_files_list()

            # find filename in first item of bilingual file list
            tmp = list(map(lambda x: x[0].filename == fl_name,
                           self.file_list_bilingual))
            try:
                self.selected_file_index = tmp.index(True)
            except:
                pass

LEN_LARGE_ML = 12
LEN_SMALL_ML = 6
LEN_ANSWER_ML = 5
WIDTH_ML = 80 # multi line field for text input

class _ItemGUI(object):

    def __init__(self, key_prefix):
        self.ml_quest = sg.Multiline(default_text="",
                                     size=(WIDTH_ML, LEN_SMALL_ML), enable_events=True,
                                     key="{}_quest".format(key_prefix))
        self.ml_answer = sg.Multiline(default_text="", enable_events=True,
                                      size=(WIDTH_ML, LEN_ANSWER_ML),
                                      key="{}_answer".format(key_prefix))

        self.txt_answer_list = sg.Text("Answer list", size=(10, 1),
                                       background_color=consts.COLOR_QUEST)

        self.ml_solution = sg.Multiline(default_text="", enable_events=True,
                                        size=(WIDTH_ML, LEN_SMALL_ML),
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

    def set_answer_list(self, enable):
        if enable:
            bkg_color = consts.COLOR_BKG_ACTIVE
        else:
            bkg_color = consts.COLOR_BKG_INACTIVE

        self.ml_answer.update(disabled=enable,
                              background_color=bkg_color,
                              visible=enable)
        self.ml_solution_answ_lst.update(disabled=enable,
                                         background_color=bkg_color,
                                         visible=enable)
        self.txt_solution_answ_lst.update(visible=enable)
        self.txt_answer_list.update(visible=enable)

    def get_frame(self, heading):
        return sg.Frame(heading, [
                    [sg.Frame("Question", [
                        [self.ml_quest],
                        [self.txt_answer_list],
                        [self.ml_answer]], background_color=consts.COLOR_QUEST)],

                    [sg.Frame("Solution (feedback)", [
                        [self.ml_solution],
                        [self.txt_solution_answ_lst],
                        [self.ml_solution_answ_lst]],
                              background_color=consts.COLOR_SOLUTION)],
                    [sg.Frame("Meta-Information", [
                        [self.ml_metainfo],
                        [self.dd_types, self.btn_change_meta]
                        ], background_color=consts.COLOR_MATA_INFO)],
                    [sg.Frame("", [[self.ml_info_validation]])]
        ])

    def as_markdown_file(self):
        rtn = _EMPTY_ITEM.question.str_markdown_heading
        rtn += self.ml_quest.get().strip() + "\n\n"

        if len(self.ml_answer.get().strip())>0:
            rtn += _EMPTY_ANSWERLIST.str_markdown_heading
            rtn += self.ml_answer.get().strip() + "\n\n"

        rtn += _EMPTY_ITEM.solution.str_markdown_heading
        rtn += self.ml_solution.get().strip() + "\n\n"
        if len(self.ml_solution_answ_lst.get().strip())>0:
            rtn += _EMPTY_ANSWERLIST.str_markdown_heading
            rtn += self.ml_solution_answ_lst.get().strip() + "\n\n"

        rtn += _EMPTY_ITEM.meta_info.str_markdown_heading
        rtn += self.ml_metainfo.get().strip() + "\n"
        return rtn






