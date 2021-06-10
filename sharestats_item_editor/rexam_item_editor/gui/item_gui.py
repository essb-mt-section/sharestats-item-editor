from os import listdir, path
import PySimpleGUI as sg

from .. import misc
from ..rexam import extypes
from ..rexam.item import RExamItem, AnswerList
from . import consts

_EMPTY_ITEM = RExamItem(None)

class ItemGUI(object):

    def __init__(self, label, key_prefix, change_meta_info_button=False):
        # all events start with key_prefix

        if consts.TAB_LAYOUT:
            len_ml = consts.LEN_ML_LARGE
            len_answer = consts.LEN_ANSWER_LARGE
        else:
            len_ml = consts.LEN_ML_SMALL
            len_answer = consts.LEN_ANSWER_SMALL

        self.label =label
        self.key_prefix = key_prefix
        self._item = None

        self.ml_quest = sg.Multiline(default_text="",
                                     size=(consts.WIDTH_ML, len_ml),
                                     enable_events=True,
                                     key="{}_quest".format(key_prefix))
        self.ml_answer = sg.Multiline(default_text="", enable_events=True,
                                      size=(consts.WIDTH_ML, len_answer),
                                      key="{}_answer".format(key_prefix))

        self.txt_answer_list = sg.Text("Answer list", size=(10, 1),
                                       background_color=consts.COLOR_QUEST)

        self.ml_solution = sg.Multiline(default_text="", enable_events=True,
                                        size=(consts.WIDTH_ML, len_ml),
                                        key="{}_solution".format(key_prefix))
        self.ml_solution_answ_lst = sg.Multiline(default_text="", enable_events=True,
                                                 size=(
                                                     consts.WIDTH_ML, len_answer),
                                                 key="{}_solution_feedback".format(key_prefix))
        self.txt_solution_answ_lst = sg.Text("Answer list", size=(10, 1),
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
            self.main_frame = sg.Frame(self.label, [
                   [tab_group],
                   [sg.Frame("Meta-Information", layout_meta_info)],
                   [sg.Frame("Validation", [[self.ml_info_validation]]),
                    sg.Frame("Files", [[self.ml_files]])]
            ])
        else:
            self.main_frame = sg.Frame(self.label, [
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
        self._item = v
        self._enable_gui(v is not None)

    def is_enabled(self):
        return self._item is not None

    def _enable_gui(self, value):
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
        self.change_meta_info_extra.update(disabled=not value)
        if not value:
            self.btn_add_answer_list.update(visible=False)
            self.btn_update_exsolution.update(visible=False)
            self.btn_add_feedback_list.update(visible=False)
            self.btn_fix_meta_issues.update(visible=False)

    def set_enable_answer_list(self, enable):
        if enable:
            col =  consts.COLOR_BKG_ACTIVE
        else:
            col = consts.COLOR_BKG_INACTIVE
        self.ml_answer.update(disabled=not enable, background_color=col)

        if self.is_enabled():
            self.btn_add_answer_list.update(visible=not enable)

    def set_enable_feedback_list(self, enable):
        if enable:
            col =  consts.COLOR_BKG_ACTIVE
        else:
            col = consts.COLOR_BKG_INACTIVE
        self.ml_solution_answ_lst.update(disabled=not enable,
                                         background_color=col)
        if self.is_enabled():
            self.btn_add_feedback_list.update(visible=not enable)

    def set_issues(self, issues):
        txt = ""
        auto_fix = False
        for i in issues:
            txt += "* {}\n".format(i.description)
            if i.fix_fnc is not None:
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
        rtn = "".join(self.rexam_item.header)
        rtn += _EMPTY_ITEM.question.str_markdown_heading
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

    def update_answer_list_button(self):
        # extract solution and switch visibility

        if self.rexam_item is None or not self.rexam_item.question.has_answer_list_section():
            self.btn_update_exsolution.update(visible=False)
            return

        solution = AnswerList.extract_solution(self.ml_answer.get())
        self.btn_update_exsolution.update(visible=
                                          self.rexam_item.meta_info.solution != solution)

    def update_ss_item(self):
        # new content from gui to ss_item
        self.rexam_item.parse(self.as_markdown_file(),
                              reset_meta_information=True)

    def update_gui(self):
        # copy ss_items --> GUI elements and set active
        if self.rexam_item is None:
            item = _EMPTY_ITEM
        else:
            item = self.rexam_item

        fl_info = path.join(path.split(item.directory)[1],
                            item.filename)
        if len(fl_info):
            fl_info = ":  ..." + path.sep + fl_info
        self.main_frame.update(value=self.label + fl_info)

        self.ml_quest.update(value=item.question.str_text)
        self.ml_solution.update(value=item.solution.str_text)

        self.ml_metainfo.update(value=item.meta_info.str_parameter +
                                item.meta_info.str_text)

        if not item.meta_info.check_type():
            t = extypes.UNKNOWN_TYPE
        else:
            t = item.meta_info.type
        self.dd_types.update(value=t)

        if not item.question.has_answer_list_section():
            self.ml_answer.update(value="")
        else:
            self.ml_answer.update(value=
                        item.question.answer_list.get_str_answers_marked() +
                        item.question.answer_list.str_text)


        if not item.solution.has_answer_list_section():
            self.ml_solution_answ_lst.update(value="")
        else:
            self.ml_solution_answ_lst.update(value=
                        item.solution.answer_list.str_answers +
                        item.solution.answer_list.str_text)
        self.set_enable_answer_list(item.question.has_answer_list_section())
        self.set_enable_feedback_list(item.solution.has_answer_list_section())
        self.update_answer_list_button()

        # validation and file info
        if self.is_enabled():
            col = consts.COLOR_BKG_ACTIVE_INFO
            self.set_issues(item.validate())
        else:
            col = consts.COLOR_BKG_INACTIVE
            self.ml_info_validation(value="", background_color=col)

        #files
        self.ml_files.update(background_color=col)
        if self.is_enabled() and len(item.directory):
            x = misc.CaseInsensitiveStringList(listdir(item.directory))
            x.remove_all(item.filename)
            if len(x):
                self.ml_files(value="\n".join(x.get()))
            else:
                self.ml_files(value="")
        else:
            self.ml_files(value="")

    def save_item(self):
        if self.rexam_item is not None:
            self.update_ss_item()
            self.rexam_item.save()
            self.update_gui()
