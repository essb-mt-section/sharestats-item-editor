from os import path
from copy import deepcopy
import PySimpleGUI as sg

from . import taxonomy
from .rexam_item_editor import consts
from .rexam_item_editor.gui.gui_misc import labeled_frame
from .rexam_item_editor.misc import splitstrip
from .rexam_item_editor.rexam.item import ItemMetaInfo
from .rexam_item_editor.rexam.rmd_file import SEP, TAG_L1, TAG_L2, TAG_BILINGUAL

BILINGUAL = "Bilingual"


class FrameMakeName(object):

    def __init__(self, default_name=""):

        default_name = path.splitext(default_name)[0] # remove possible extension
        defaults = [""] * 4
        if default_name.endswith(TAG_BILINGUAL):
            defaults[3] = BILINGUAL
            default_name = default_name[:-1*len(TAG_BILINGUAL)]
        elif default_name.endswith(TAG_L1):
            defaults[3] = consts.LANGUAGE1
            default_name = default_name[:-1*len(TAG_L1)]
        elif default_name.endswith(TAG_L2):
            defaults[3] = consts.LANGUAGE2
            default_name = default_name[:-1*len(TAG_L2)]
        else:
            defaults[3] = ""

        for c, txt in enumerate(default_name.split(SEP, maxsplit=2)):
            if c == 2: # cast number
                try:
                    defaults[c] = str(int(txt))
                except:
                    defaults[c-1] += SEP + txt
            else:
                defaults[c] = txt

        if len(defaults[1])==0 and len(defaults[0])>0:
            defaults[1], defaults[0] = defaults[0], defaults[1]

        self.txt_name1 = sg.Text("", size=(43, 1), key="txt_name1")
        self.txt_name2 = sg.Text("", size=(43, 1), key="txt_name2")
        fr_names = sg.Frame("", [[sg.Text("a:", size=(2,1)),
                                  self.txt_name1],
                                 [sg.Text("b:" , size=(2,1)),
                                  self.txt_name2]],
                            border_width=0)

        self.fln0 = sg.InputText(default_text=defaults[0], size=(5,1),
                                 key="fln0", enable_events=True)
        self.fln1 = sg.InputText(default_text=defaults[1], size=(25,1),
                                 key="fln1",enable_events=True)
        self.fln2 = sg.InputText(default_text=str(defaults[2]), size=(4,1),
                                 key="fln2",enable_events=True)
        self.fln3 = sg.DropDown(default_value=defaults[3],
                                values=[consts.LANGUAGE1, consts.LANGUAGE2, BILINGUAL],
                                key="fln3", enable_events=True)

        self.frame = sg.Frame("Item Name(s)",[
            [labeled_frame([self.fln0, sg.Text(SEP)], "Uni"),
             labeled_frame([self.fln1, sg.Text(SEP)], "Topic"),
             labeled_frame([self.fln2, sg.Text(SEP)], "Counter"),
             labeled_frame(self.fln3, "Language")], [fr_names]
        ])

    def update_names(self):
        # call me once after window created
        fln0 = self.fln0.get().strip().lower()
        fln1 = self.fln1.get().strip().lower()
        fln2 = self.fln2.get().strip()

        name1 = SEP.join(filter(len, (fln0, fln1)))
        name2 = ""

        if len(name1):
            try:
                name1 += SEP + str(int(fln2)).zfill(3)
            except:
                pass

        if len(name1) > 0:
            lang = self.fln3.get()
            if lang == consts.LANGUAGE1:
                name1 = name1 + TAG_L1
            elif lang == consts.LANGUAGE2:
                name1 = name1 + TAG_L2
            elif lang == BILINGUAL:
                name2 = name1 + TAG_L2
                name1 = name1 + TAG_L1

        self.txt_name1.update(value=name1)
        self.txt_name2.update(value=name2)

    @property
    def name1(self):
        return self.txt_name1.get()

    @property
    def name2(self):
        return self.txt_name2.get()


def edit_taxonomy(current_meta_info):
    """default_taxonomy needs to be comma separated as specified Rmd file
    """
    assert (isinstance(current_meta_info, ItemMetaInfo))

    meta_info = deepcopy(current_meta_info)
    tax = taxonomy.Taxonomy()
    default_taxonomy = "\n".join(splitstrip(meta_info.taxonomy, ","))
    default_type = "\n".join(splitstrip(meta_info.type_tag, ","))

    # LAYOUT
    layout = []

    # taxomony
    list_box = [sg.Listbox(values=[], size=(22, 10), key="L1",
                           background_color=consts.COLOR_BKG_TAX_LIST,
                           enable_events=True),
                sg.Listbox(values=[], size=(22, 10), key="L2",
                           background_color=consts.COLOR_BKG_TAX_LIST,
                           enable_events=True),
                sg.Listbox(values=[], size=(22, 10), key="L3",
                           background_color=consts.COLOR_BKG_TAX_LIST,
                           enable_events=True),
                sg.Listbox(values=[], size=(22, 10), key="L4",
                           background_color=consts.COLOR_BKG_TAX_LIST,
                           enable_events=True)]

    ml_result_tax = sg.Multiline(default_text=default_taxonomy, size=(80, 6),
                                 key="result_tax")

    fr_taxonomy = sg.Frame("Taxonomy", [[sg.Frame("1", [[list_box[0]]]),
                                         sg.Frame("2", [[list_box[1]]]),
                                         sg.Frame("3", [[list_box[2]]]),
                                         sg.Frame("4", [[list_box[3]]])],
                                        [sg.Button(">>", size=(6, 5),
                                                   key="add_tax"),
                                         ml_result_tax]])
    layout.append([fr_taxonomy])

    # type
    ml_types = sg.Multiline(default_text=default_type, size=(20, 4),
                            key="result_types")
    fr_types = sg.Frame("Types", [
        [sg.Listbox(values=tax.get_tag_types(), size=(26, 10),
                    background_color=consts.COLOR_BKG_TAX_LIST, key="L_types"),
         sg.Button(">>", size=(2, 2), key="add_types"),
         ml_types]
    ])
    # tags
    fr_tags = sg.Frame("Tags", [
        [sg.Text("Language:", size=(13, 1), ),
         sg.DropDown(values=[""] + tax.get_tag_languages(),
                     default_value=meta_info.language,
                     size=(20, 10),
                     key="dd_lang")],
        [sg.Text("Program:", size=(13, 1)),
         sg.DropDown(values=[""] + tax.get_tag_programs(),
                     default_value=meta_info.program,
                     size=(20, 10), key="dd_progam")],
        [sg.Text("Level:", size=(13, 1)),
         sg.DropDown(values=[""] + tax.get_tag_levels(),
                     default_value=meta_info.level,
                     size=(20, 10), key="dd_level")],
    ])
    layout.append([fr_types,
                   sg.Frame("", [[fr_tags],
                                 [sg.Text()],
                                 [sg.Text(" " * 15),
                                  sg.Button("Cancel", key="cancel",
                                            size=(12, 2)),
                                  sg.Button("OK", key="ok", size=(12, 2))]
                                 ], border_width=0)
                   ])

    window = sg.Window("Taxonomy", layout, finalize=True)
    list_box[0].update(values=tax.get_taxonomy_level())

    select = []

    while True:
        window.refresh()
        event, value = window.read()
        # check selection
        if event in ("L1", "L2", "L3", "L4"):
            select = []
            for x in ("L1", "L2", "L3", "L4"):
                try:
                    select.append(value[x][0])
                except:
                    break
                if x == event:
                    break
            if event == "L1":
                list_box[1].update(values=tax.get_taxonomy_level(select[:1]))
                list_box[2].update(values=[])
                list_box[3].update(values=[])
            elif event == "L2":
                list_box[2].update(values=tax.get_taxonomy_level(select[:2]))
                list_box[3].update(values=[])
            elif event == "L3":
                list_box[3].update(values=tax.get_taxonomy_level(select[:3]))

        elif event == "add_tax":
            r = value["result_tax"]
            r += "/".join(select) + "\n"
            ml_result_tax.update(value=r.strip())

        elif event == "add_types":
            r = value["result_types"]
            r += "\n".join(value["L_types"]) + "\n"
            ml_types.update(value=r.strip())
        else:
            break

    window.close()

    if event == "ok":
        tmp = splitstrip(value["result_tax"].strip(), "\n")
        meta_info.taxonomy = ", ".join(filter(len, tmp))  # remove empty lines and csv
        tmp = splitstrip(value["result_types"].strip(), "\n")
        meta_info.type_tag = ", ".join(filter(len, tmp))
        meta_info.program = value["dd_progam"]
        meta_info.level = value["dd_level"]
        meta_info.language = value["dd_lang"]
        return meta_info

    else:
        return None
