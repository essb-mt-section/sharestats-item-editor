from os import listdir, path
import PySimpleGUI as sg

from .. import misc, consts
from ..rexam import extypes
from ..rexam.item import RExamItem, AnswerList
from ..rexam.git_info import GitInfo

_EMPTY_ITEM = RExamItem(None)

sg.theme_add_new("mytheme", consts.SG_COLOR_THEME)
sg.theme("mytheme")


class GUIBaseDirectory(object):

    def __init__(self, database_folder, label="Base Directory",
                 size=(60, 1), key="change_directory"):

        self.label = label
        self.text = sg.Text(database_folder, size=size,
                                background_color=consts.COLOR_BKG_ACTIVE_INFO)
        self.frame = sg.Frame(title=label, layout=[[self.text,
                      sg.Button("change", size=(6, 1), key=key)]], border_width=2)

    def update_folder(self, folder):
        self.text.update(value=folder)
        txt = self.label
        head = GitInfo(folder).head
        if len(head):
            txt += ": git head {}".format(head[:7])
        self.frame.update(value=txt)


def labeled_frame(elem, label="", border_width=0):
    if not isinstance(elem, list):
        elem = [elem]
    return sg.Frame(label,[elem], border_width=border_width)


def set_font(font, font_size):
    if font is not None:
        if font_size is None:
            font_size = ""
        sg.set_options(font='{} {}'.format(font, font_size))

class GUIItem(object):

    def __init__(self, label, key_prefix,
                 show_hash = True,
                 change_meta_info_button=False,
                 disabled = False):
        # all events start with key_prefix

        if consts.TAB_LAYOUT:
            len_ml = consts.LEN_ML_LARGE
            len_answer = consts.LEN_ANSWER_LARGE
        else:
            len_ml = consts.LEN_ML_SMALL
            len_answer = consts.LEN_ANSWER_SMALL

        self.disabled = disabled
        self.label = label
        self.show_hash = show_hash
        self.key_prefix = key_prefix
        self._item = None

        self.ml_quest = sg.Multiline(default_text="",
                                     size=(consts.WIDTH_ML, len_ml),
                                     enable_events=True,
                                     key="{}_quest".format(key_prefix))
        self.ml_answer = sg.Multiline(default_text="", enable_events=True,
                                      size=(consts.WIDTH_ML, len_answer),
                                      key="{}_answer".format(key_prefix))

        self.txt_answer_list = sg.Text("Answer-list", size=(10, 1),
                                       background_color=consts.COLOR_QUEST)

        self.ml_solution = sg.Multiline(default_text="", enable_events=True,
                                        size=(consts.WIDTH_ML, len_ml),
                                        key="{}_solution".format(key_prefix))
        self.ml_solution_answ_lst = sg.Multiline(default_text="", enable_events=True,
                                                 size=(
                                                     consts.WIDTH_ML, len_answer),
                                                 key="{}_solution_feedback".format(key_prefix))
        self.txt_solution_answ_lst = sg.Text("Answer-list", size=(10, 1),
                                             background_color=consts.COLOR_SOLUTION)

        self.ml_metainfo = sg.Multiline(default_text="",
                                        size=(consts.WIDTH_ML, 10), enable_events=True,
                                        key="{}_meta".format(key_prefix))

        self.change_meta_info_extra = sg.Button("Edit Meta Information",
                                                enable_events=True,
                                                visible=change_meta_info_button,
                                                key="{}_btn_change_meta".format(key_prefix))

        self.ml_info_validation =sg.Multiline(default_text="",
                                              size=(consts.WIDTH_ML - 26, 4),
                                              background_color=consts.COLOR_BKG_INACTIVE,
                                              disabled=True)

        self.ml_files = sg.Multiline(default_text="",
                                     size=(20, 4),
                                     background_color=consts.COLOR_BKG_INACTIVE,
                                     disabled=True,
                                     write_only=False)

        self.dd_types = sg.DropDown(values=[extypes.UNKNOWN_TYPE] +
                                           list(extypes.EXTYPES.keys()),
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
                                               button_color=consts.COLOR_RED_BTN,
                                               size=(15,1),
                                               key="{}_btn_update_exsolution".format(key_prefix))

        self.btn_fix_meta_issues = sg.Button("Auto-fix issues",
                                             enable_events=True,
                                             button_color=consts.COLOR_RED_BTN,
                                             size=(15,1),
                                             key="{}_btn_fix_meta_issues".format(key_prefix))

        # make main frame
        layout_question =[[self.ml_quest],
                        [self.txt_answer_list, self.btn_add_answer_list,
                         self.btn_update_exsolution],
                        [self.ml_answer]]

        layout_solution = [[self.ml_solution],
                        [self.txt_solution_answ_lst, self.btn_add_feedback_list],
                        [self.ml_solution_answ_lst]]

        layout_meta_info =  [[self.ml_metainfo],
                             [self.dd_types, self.btn_fix_meta_issues,
                              self.change_meta_info_extra]]

        if consts.TAB_LAYOUT:
            tab_group = sg.TabGroup([[sg.Tab("Question", layout_question,
                                             background_color=consts.COLOR_QUEST,
                                             key="{}_tab_quest".format(
                                                 self.key_prefix)),
                                      sg.Tab("Solution", layout_solution,
                                             background_color=consts.COLOR_SOLUTION,
                                             key="{}_tab_sol".format(
                                                 self.key_prefix))
                                      ]])
            self.gui_element = sg.Frame(self.label, [
                   [tab_group],
                   [sg.Frame("Meta-Information", layout_meta_info)],
                   [sg.Frame("Validation", [[self.ml_info_validation]]),
                    sg.Frame("Files", [[self.ml_files]])]
            ])
        else:
            self.gui_element = sg.Frame(self.label, [
                   [sg.Frame("Question", layout_question,
                             background_color=consts.COLOR_QUEST)],
                   [sg.Frame("Solution (feedback)", layout_solution,
                             background_color=consts.COLOR_SOLUTION)],
                    [sg.Frame("Meta-Information", layout_meta_info)],
                    [sg.Frame("", [[self.ml_info_validation]])]
            ])

    @property
    def rexam_item(self):
        return self._item

    @rexam_item.setter
    def rexam_item(self, v):
        assert isinstance(v, (RExamItem)) or v is None
        if self.disabled:
            self._item = None
        else:
            self._item = v
            self._activate_gui(v is not None)

    def is_activated(self):
        return self._item is not None

    def _activate_gui(self, value):
        if self.disabled:
            return
        if value:
            col = consts.COLOR_BKG_ACTIVE
        else:
            col = consts.COLOR_BKG_INACTIVE

        self.ml_quest.update(disabled=not value, background_color=col)
        self.ml_answer.update(disabled=not value, background_color=col)
        self.ml_solution.update(disabled=not value, background_color=col)
        self.ml_solution_answ_lst.update(disabled=not value,
                                         background_color=col)
        self.ml_metainfo.update(disabled=not value, background_color=col)
        self.dd_types.update(disabled=not value)
        self.change_meta_info_extra.update(disabled=not value)
        if not value:
            self.btn_add_answer_list.update(visible=False)
            self.btn_update_exsolution.update(visible=False)
            self.btn_add_feedback_list.update(visible=False)
            self.btn_fix_meta_issues.update(visible=False)

    def set_enable_answer_list(self, enable):
        if self.disabled:
            return

        if enable:
            col =  consts.COLOR_BKG_ACTIVE
        else:
            col = consts.COLOR_BKG_INACTIVE
        self.ml_answer.update(disabled=not enable, background_color=col)

        if self.is_activated():
            self.btn_add_answer_list.update(visible=not enable)

    def set_enable_feedback_list(self, enable):
        if self.disabled:
            return
        if enable:
            col =  consts.COLOR_BKG_ACTIVE
        else:
            col = consts.COLOR_BKG_INACTIVE
        self.ml_solution_answ_lst.update(disabled=not enable,
                                         background_color=col)
        if self.is_activated():
            self.btn_add_feedback_list.update(visible=not enable)

    def set_issues(self, issues):
        if self.disabled:
            return
        txt = ""
        auto_fix = False
        for i in issues:
            txt += "* {}\n".format(i.description)
            if i.has_fix_function:
                auto_fix = True

        self.ml_info_validation(value=txt)
        self.btn_fix_meta_issues.update(visible=auto_fix)
        if len(issues):
            self.ml_info_validation(background_color="darkred",
                                    text_color="white")
        else:
            self.ml_info_validation(background_color=consts.COLOR_BKG_ACTIVE_INFO,
                                    text_color="black")

    def as_markdown_file(self):
        if self.disabled:
            return ""

        rtn = "".join(self.rexam_item.header)
        rtn += _EMPTY_ITEM.question.str_markdown_heading()
        rtn += self.ml_quest.get().strip() + "\n\n"

        if len(self.ml_answer.get().strip())>0:
            rtn += AnswerList(_EMPTY_ITEM).str_markdown_heading()
            rtn += self.ml_answer.get().strip() + "\n\n"

        rtn += _EMPTY_ITEM.solution.str_markdown_heading()
        rtn += self.ml_solution.get().strip() + "\n\n"
        if len(self.ml_solution_answ_lst.get().strip())>0:
            rtn += AnswerList(_EMPTY_ITEM).str_markdown_heading()
            rtn += self.ml_solution_answ_lst.get().strip() + "\n\n"

        rtn += _EMPTY_ITEM.meta_info.str_markdown_heading()
        rtn += self.ml_metainfo.get().strip() + "\n"
        return rtn

    def update_answer_list_button(self):
        # extract solution and switch visibility
        if self.disabled:
            return

        if self.rexam_item is None or not self.rexam_item.question.has_answer_list_section():
            self.btn_update_exsolution.update(visible=False)
            return

        solution = AnswerList.extract_solution(self.ml_answer.get())
        self.btn_update_exsolution.update(visible=
                                          self.rexam_item.meta_info.solution != solution)

    def update_item(self):
        # new content from gui to ss_item
        self.rexam_item.parse(self.as_markdown_file(),
                              reset_meta_information=True)

    def update_gui(self):
        # copy items --> GUI elements and set active

        if self.disabled:
            return

        if self.rexam_item is None:
            item = _EMPTY_ITEM
        else:
            item = self.rexam_item


        fl_info = self.label + ": "
        tmp = path.join(item.sub_directory, item.filename)
        if len(tmp):
            if self.show_hash:
                fl_info += "[{}] ".format(item.hash_short())
            fl_info += "..." + path.sep + tmp
        self.gui_element.update(value=fl_info)

        self.ml_quest.update(value=item.question.str_text())
        self.ml_solution.update(value=item.solution.str_text())

        self.ml_metainfo.update(value=item.meta_info.str_parameter() +
                                item.meta_info.str_text())

        if not item.meta_info.check_type():
            t = extypes.UNKNOWN_TYPE
        else:
            t = item.meta_info.type
        self.dd_types.update(value=t)

        if not item.question.has_answer_list_section():
            self.ml_answer.update(value="")
        else:
            self.ml_answer.update(value=
                                  item.question.answer_list.str_answers(tag_mark_correct=True) +
                                  item.question.answer_list.str_text())


        if not item.solution.has_answer_list_section():
            self.ml_solution_answ_lst.update(value="")
        else:
            self.ml_solution_answ_lst.update(value=
                        item.solution.answer_list.str_answers() +
                        item.solution.answer_list.str_text())
        self.set_enable_answer_list(item.question.has_answer_list_section())
        self.set_enable_feedback_list(item.solution.has_answer_list_section())
        self.update_answer_list_button()

        # validation and file info
        if self.is_activated():
            col = consts.COLOR_BKG_ACTIVE_INFO
            self.set_issues(item.validate())
        else:
            col = consts.COLOR_BKG_INACTIVE
            self.ml_info_validation(value="", background_color=col)

        #files
        try:
            is_in_subfolder = len(self.rexam_item.sub_directory)>0
        except:
            is_in_subfolder = False

        if self.is_activated() and is_in_subfolder:
            self.ml_files.update(background_color=consts.COLOR_BKG_ACTIVE_INFO)
            x = misc.CaseInsensitiveStringList(listdir(item.directory))
            x.remove_all(item.filename)
            if len(x):
                self.ml_files(value="\n".join(x.get()))
            else:
                self.ml_files(value="")

        else:
            self.ml_files.update(background_color=consts.COLOR_BKG_INACTIVE)
            self.ml_files(value="")

    def save_item(self):
        if self.rexam_item is not None:
            self.update_item()
            self.rexam_item.save()
            self.update_gui()
