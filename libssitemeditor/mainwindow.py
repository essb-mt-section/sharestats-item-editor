import PySimpleGUI as sg

from os import path, getcwd
from . import __version__, consts, files, settings
from .sharestats_item import ShareStatsItem
from . import windows

BGK_COLOR_INACTIVE = "#8A8A8A"
BGK_COLOR_ACTIVE = "#FFFFFF"


class MainWindow(object):

    _EMPTY_ITEM = ShareStatsItem(None)

    def __init__(self):
        sg.theme('SystemDefault1')

        # LAYOUT
        self.ig_nl = _ItemGUI("nl")
        self.ig_en = _ItemGUI("en")
        self.lb_files = sg.Listbox(values=['File 1', 'File 2',
                                            'File 3'],
                                   enable_events=True, key="lb_files",
                                   size=(30, 37))

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
            item = MainWindow._EMPTY_ITEM

        ig.ml_metainfo.update(value=item.meta_info.str_parameter +
                                item.meta_info.str_text)

        ig.ml_folder_info(value="") #TODO
        ig.ml_quest.update(value=item.question.str_text)
        ig.ml_solution.update(value=item.solution.str_text)

        if item.question.answer_list is None:
            ig.ml_answer.update(value="")
            ig.set_answer_list(False)
        else:
            ig.set_answer_list(True)
            ig.ml_answer.update(value=
                        item.question.answer_list.str_answers +
                        item.question.answer_list.str_text, disabled=True)
        if item.solution.answer_list is None:
            ig.ml_solution_feedback.update(value="")
        else:
            ig.ml_solution_feedback.update(value=
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
                self.unsaved_changes = True

            if event == "close":
                break

            elif event == "nl_btn_change_meta":
                if self.ss_item_nl is not None:
                    new_tax = windows.taxonomy(self.ss_item_nl.meta_info)
                    if new_tax is not None:
                        self.ss_item_nl.meta_info = new_tax
                        self.update_item_gui(en=False)

            elif event == "en_btn_change_meta":
                if self.ss_item_en is not None:
                    new_tax = windows.taxonomy(self.ss_item_en.meta_info)
                    if new_tax is not None:
                        self.ss_item_en.meta_info = new_tax
                        self.update_item_gui(en=True)

            elif event=="it_base_dir":
                self.base_directory = values[event]

            elif event== "save":
                self.save_items(ask=False)

            elif event=="new":
                new_items = windows.new_item(self.base_directory)
                if new_items[0] is not None:
                    self.save_items()  # TODO allow canceling new at this point
                    # TODO check existing file and  overriding
                    self.ss_item_nl, self.ss_item_en = new_items
                    self.unsaved_changes = True
                    fl_name = self.ss_item_nl.filename.filename
                    if self.ss_item_nl.filename.get_language()== "en":
                        #swap
                        self.ss_item_nl, self.ss_item_en = \
                                        self.ss_item_en, self.ss_item_nl
                    self.save_items(ask=False) # create folder and file
                    self.update_item_gui(en=True)
                    self.update_item_gui(en=False)
                    self.update_files_list()

                    #find filename in new bilingual file list
                    tmp = list(map(lambda x:x[0].filename==fl_name,
                                   self.file_list_bilingual))
                    try:
                        self.selected_file_index = tmp.index(True)
                    except:
                        pass


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

                if self.selected_file_index is None:
                    continue

                self.save_items()
                self.ss_item_nl = None
                self.ss_item_en = None
                fls = self.file_list_bilingual[self.selected_file_index]
                if fls[0] is not None:
                    if  fls[0].get_language()=="en":
                        self.ss_item_en = ShareStatsItem(fls[0])
                        self.ss_item_nl = ShareStatsItem(fls[1])
                    else:
                        self.ss_item_en = ShareStatsItem(fls[1])
                        self.ss_item_nl = ShareStatsItem(fls[0])
                    self.update_item_gui(en=True)
                    self.update_item_gui(en=False)

        # processing
        self.save_items()
        self.window.close()
        settings.save()

    def save_items(self, ask=False):
        # FIXME import gui content to self.ss_item
        if ask:
            # resp = windows.ask_save()
            #if resp == False:
            #    return
            pass # TODO
        if self.unsaved_changes:
            if self.ss_item_en is not None:
                self.ss_item_en.save()
            if self.ss_item_nl is not None:
                self.ss_item_nl.save()
            self.unsaved_changes = False


class _ItemGUI(object):

    def __init__(self, key_prefix):
        answer_length = 5
        solution_length = 3
        self.ml_quest = sg.Multiline(default_text="",
                                     size=(80, 8), enable_events=True,
                                     key="{}_quest".format(key_prefix))
        self.ml_answer = sg.Multiline(default_text="", enable_events=True,
                                      size=(80, answer_length),
                                      background_color=BGK_COLOR_INACTIVE,
                                      disabled=True,
                                      key="{}_answer".format(key_prefix))
        self.ml_solution = sg.Multiline(default_text="", enable_events=True,
                                        size=(80, solution_length),
                                        key="{}_solution".format(key_prefix))

        self.ml_solution_feedback = sg.Multiline(default_text="",  enable_events=True,
                                                 size=(80, answer_length),
                                                 background_color=BGK_COLOR_INACTIVE,
                                                 disabled=True,
                                                 key="{}_solution_feedback".format(key_prefix))
        self.ml_metainfo = sg.Multiline(default_text="",
                                        size=(80, 10),  enable_events=True,
                                        key="{}_meta".format(key_prefix))

        self.btn_change_meta = sg.Button("Edit Meta Information",  enable_events=True,
                                         key="{}_btn_change_meta".format(key_prefix))

        self.ml_folder_info =sg.Multiline(default_text="",
                         size=(80, 5),
                         background_color="#DADADA",
                         disabled=True,
                         key="{}_folder_info".format(key_prefix))

    def set_answer_list(self, enable):
        if enable:
            bkg_color = BGK_COLOR_ACTIVE
        else:
            bkg_color = BGK_COLOR_INACTIVE

        self.ml_answer.update(disabled=enable, background_color=bkg_color)
        self.ml_solution_feedback.update(disabled=enable, background_color=bkg_color)

    def get_frame(self, heading):
        q_colour = "#BBBBDD"
        s_colour = "#BBDDBB"
        m_colour = "#DDBBBB"
        return sg.Frame(heading, [
                    [sg.Frame("Question", [
                        [self.ml_quest],
                        [sg.Text("Answers", size=(10, 1),
                                 background_color=q_colour)],
                        [self.ml_answer]], background_color=q_colour)],

                    [sg.Frame("Solution", [
                        [self.ml_solution],
                        [sg.Text("Answer feedback", size=(30, 1),
                                 background_color=s_colour)],
                        [self.ml_solution_feedback]],
                              background_color=s_colour)],
                    [sg.Frame("Meta-Information", [
                        [self.ml_metainfo], [self.btn_change_meta]
                        ], background_color=m_colour)],
                    [sg.Frame("", [[self.ml_folder_info] ])]
        ])


