from ..gui.mainwin import MainWin
from ..gui import dialogs as base_dialogs

from .dialogs import edit_taxonomy,FrameMakeName
base_dialogs.FrameMakeName = FrameMakeName

class SSItemEditorMainWin(MainWin):

    def __init__(self, reset_settings):
        super().__init__(reset_settings=reset_settings,
                         change_meta_info_button=True)

    def process_item_gui_event(self, event, values):

        if event.endswith("btn_change_meta"):

            if event.startswith("nl_"):
                ig = self.ig_nl
            else:
                ig = self.ig_en

            ig.update_ss_item()
            new_meta = edit_taxonomy(ig.rexam_item.meta_info)
            if new_meta is not None:
                ig.rexam_item.meta_info = new_meta
                ig.ml_metainfo.update(value=new_meta.str_parameter +
                                            new_meta.str_text)
                ig.rexam_item.meta_info.sort_parameter()
                ig.update_gui()

        else:
            super().process_item_gui_event(event, values)