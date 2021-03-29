import PySimpleGUI as sg

from . import __version__, consts, files
from . statsshare_item import StatsShareItem
from .windows import taxonomy_win


def run():
    _MainWin().run()

class _MainWin(object):

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
            [sg.Button(button_text="<<", size=(11, 1)),
             sg.Button(button_text=">>", size=(11, 1))]])

        fr_btns =sg.Frame("", [
            [sg.Button(button_text="New", size=(28, 2), key="new")],
            [sg.Button(button_text="Save", size=(28, 2), key="save")],
            [sg.CloseButton(button_text="Close", size=(28, 2))]])

        left_frame = sg.Frame("", [[fr_files], [fr_btns]],
                              border_width=0)

        layout = [[left_frame,
                   self.ig_nl.get_frame("Dutch"),
                   self.ig_en.get_frame("English")]]

        self.window = sg.Window("{} ({})".format(consts.APPNAME, __version__),
                                layout, finalize=True)

        self.ss_item_nl = None
        self.ss_item_en = None
        self.base_folder = "demo" # todo settings & window
        self.file_list_bilingual = []

    def update_item_gui(self, en):

        if en:
            ig = self.ig_en
            item = self.ss_item_en
        else:
            ig = self.ig_nl
            item = self.ss_item_nl

        ig.ml_metainfo.update(value=
                                item.meta_info.str_parameter +
                                item.meta_info.str_text)

        ig.ml_folder_info(value="") #TODO
        ig.ml_quest.update(value=item.question.str_text)
        ig.ml_solution.update(value=item.solution.str_text)
        if item.question.answer_list is None:
            ig.ml_answer.update(value="")
        else:
            ig.ml_answer.update(value=
                        item.question.answer_list.str_answers +
                        item.question.answer_list.str_text)
        if item.solution.answer_list is None:
            ig.ml_solution_feedback.update(value="")
        else:
            ig.ml_solution_feedback.update(value=
                        item.solution.answer_list.str_answers +
                        item.solution.answer_list.str_text)

    def update_files_list(self):
        self.file_list_bilingual = files.rmd_file_list_bilingual(self.base_folder)
        list_display = list(map(files.bilinguar_list_name, self.file_list_bilingual))
        self.lb_files.update(values=list_display)

    def run(self):
        self.ss_item_nl = StatsShareItem("templates/TemplateMultipleChoice.Rmd")
        self.ss_item_en = StatsShareItem("templates/TemplateMultipleChoice.Rmd")

        self.update_files_list()
        self.update_item_gui(en=False)
        self.update_item_gui(en=True)
        unsaved_changes = False
        while True:
            self.window.refresh()
            event, values = self.window.read()
            if event is None:
                break

            if not unsaved_changes and (event.startswith("nl_") or
                                        event.startswith("en_")):
                unsaved_changes = True

            if event == "close":
                break
            elif event == "nl_btn_change_meta":
                new_tax = taxonomy_win(self.ss_item_nl.meta_info)
                if new_tax is not None:
                    self.ss_item_nl.meta_info = new_tax
                    self.update_item_gui(en=False)

            elif event == "en_btn_change_meta":
                new_tax = taxonomy_win(self.ss_item_en.meta_info)
                if new_tax is not None:
                    self.ss_item_en.meta_info = new_tax
                    self.update_item_gui(en=True)

            elif event== "save":
                # save TODO
                unsaved_changes=False

            elif event=="new":
                if unsaved_changes:
                    pass

            elif event=="lb_files":
                sel = self.lb_files.get_indexes()
                if unsaved_changes:
                    pass
                fls = self.file_list_bilingual[sel[0]]
                if fls[0] is not None:
                    if  fls[0].get_language()=="en":
                        self.ss_item_en = StatsShareItem(fls[0])
                        self.ss_item_nl = StatsShareItem(fls[1])
                    else:
                        self.ss_item_en = StatsShareItem(fls[1])
                        self.ss_item_nl = StatsShareItem(fls[0])
                    self.update_item_gui(en=True)
                    self.update_item_gui(en=False)

        # processing
        if unsaved_changes:
            pass # ToDo warning

        self.window.close()




class _ItemGUI(object):

    def __init__(self, key_prefix):
        answer_length = 5
        solution_length = 3
        self.ml_quest = sg.Multiline(default_text="",
                                     size=(80, 8), enable_events=True,
                                     key="{}_quest".format(key_prefix))
        self.ml_answer = sg.Multiline(default_text="", enable_events=True,
                                      size=(80, answer_length),
                                      key="{}_answer".format(key_prefix))
        self.ml_solution = sg.Multiline(default_text="", enable_events=True,
                                        size=(80, solution_length),
                                        key="{}_solution".format(key_prefix))

        self.ml_solution_feedback = sg.Multiline(default_text="",  enable_events=True,
                                                 size=(80, answer_length),
                                                 key="{}_solution_feedback".format(key_prefix))
        self.ml_metainfo = sg.Multiline(default_text="",
                                        size=(80, 10),  enable_events=True,
                                        key="{}_meta".format(key_prefix))

        self.btn_change_meta = sg.Button("Edit Meta Information",  enable_events=True,
                                         key="{}_btn_change_meta".format(key_prefix))

        self.ml_folder_info =sg.Multiline(default_text="",
                         size=(80, 5),
                         background_color="#DADADA",
                         key="{}_folder_info".format(key_prefix))


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


