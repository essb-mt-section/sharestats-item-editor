import PySimpleGUI as sg

from . import consts
from .taxonomy import Taxonomy
from .item_sections import ItemMetaInfo

def splitstrip(text, sep):
    return list(map(lambda x: x.strip(), text.split(sep)))


def taxonomy(meta_info):
    """default_taxonomy needs to be comma seperated as specified Rmd file
    """
    assert (isinstance(meta_info, ItemMetaInfo))

    tax = Taxonomy()
    default_taxonomy = "\n".join(splitstrip(meta_info.taxonomy, ","))
    default_type = "\n".join(splitstrip(meta_info.type, ","))

    # LAYOUT
    layout = []
    sg.theme('SystemDefault1')
    list_bg = '#E0E0D0'

    # taxomony
    list_box = [sg.Listbox(values=[], size=(22, 10), key="L1",
                           background_color=list_bg,
                           enable_events=True),
                sg.Listbox(values=[], size=(22, 10), key="L2",
                           background_color=list_bg,
                           enable_events=True),
                sg.Listbox(values=[], size=(22, 10), key="L3",
                           background_color=list_bg,
                           enable_events=True),
                sg.Listbox(values=[], size=(22, 10), key="L4",
                           background_color=list_bg,
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
        [sg.Listbox(values=tax.get_tags_type(), size=(26, 10),
                    background_color=list_bg, key="L_types"),
         sg.Button(">>", size=(2, 2), key="add_types"),
         ml_types]
    ])
    # tags
    fr_tags = sg.Frame("Tags", [
        [sg.Text("Language:", size=(13, 1), ),
         sg.DropDown(values=[""] + tax.get_tags_language(),
                     default_value=meta_info.language,
                     size=(20, 10),
                     key="dd_lang")],
        [sg.Text("Program:", size=(13, 1)),
         sg.DropDown(values=[""] + tax.get_tags_program(),
                     default_value=meta_info.program,
                     size=(20, 10), key="dd_progam")],
        [sg.Text("Level:", size=(13, 1)),
         sg.DropDown(values=[""] + tax.get_tags_level(),
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
            r += " / ".join(select) + "\n"
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
        meta_info.taxonomy = ", ".join(
            filter(len, tmp))  # remove empty lines and csv
        tmp = splitstrip(value["result_types"].strip(), "\n")
        meta_info.type = ", ".join(filter(len, tmp))
        meta_info.program = value["dd_progam"]
        meta_info.level = value["dd_level"]
        meta_info.language = value["dd_lang"]
        return meta_info

    else:
        return None

def new_item():
    sg.theme('SystemDefault1')

    txt_flname1 = sg.Text("", size=(43, 1))
    txt_flname2 = sg.Text("", size=(30, 1))
    fr_names = sg.Frame("", [[sg.Text("a:", size=(2,1)), txt_flname1],
                                  [sg.Text("b:" , size=(2,1)),txt_flname2]],
                        border_width=0)

    lb_type = sg.Listbox(values=["None"] + list(consts.EXTYPES.values()),
                            default_values=["None"],
                         select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                         size=(26, 6), no_scrollbar=True,
                         key="lb_type")

    fr_filename = sg.Frame("Item Name(s)",[
                           [sg.Text("Uni"+" "*11 + "Topic"+" "*24 +
                                    "Counter"+" "*7 + "Language")],
                            [sg.InputText(size=(5,1), key="fln0",
                                          enable_events=True), sg.Text("-"),
                            sg.InputText(size=(15,1), key="fln1",
                                          enable_events=True), sg.Text("-"),
                            sg.InputText(size=(4,1), key="fln2",
                                          enable_events=True), sg.Text("-"),
                            sg.DropDown(values=["Dutch", "English",
                                                "Bilingual"], key="fln3",
                                            enable_events=True),
                            ], [fr_names]
                        ])

    layout=[[fr_filename]]
    layout.append([sg.Frame("Template", [[lb_type]]),
                                    sg.Cancel(size=(10, 2)),
                                    sg.Button("Create", size=(10, 2),
                                              key="create")])
    window = sg.Window("New Item(s)", layout, finalize=True)

    fln_name1 = ""
    fln_name2 = ""
    selected = lb_type.get_indexes()

    while True:
        window.refresh()
        event, v = window.read()

        if event.startswith("fln"):
            tmp = tuple(map(lambda x:x.lower().strip(),
                                            (v["fln0"], v["fln1"]) ))

            fln_name1 = "-".join(filter(len, (tmp[:2])))
            fln_name2 = ""

            if len(fln_name1):
                try:
                    fln_name1 += "-" + str(int(v["fln2"])).zfill(3)
                except:
                    pass

            if len(fln_name1)>0:
                lang = v["fln3"]
                if lang == "Dutch":
                    fln_name1 = fln_name1 + "-nl"
                elif lang == "English":
                    fln_name1 = fln_name1 + "-en"
                elif lang == "Bilingual":
                    fln_name2 = fln_name1 + "-en"
                    fln_name1 = fln_name1 + "-nl"
            txt_flname1.update(value=fln_name1)
            txt_flname2.update(value=fln_name2)

        else:
            break

    rtn = None
    if event == "create" and len(fln_name1):
        s = lb_type.get_indexes()[0]
        if s > 0:
            selected = list(consts.EXTYPES.keys())[s - 1]
        else:
            selected = None
        rtn = (fln_name1, fln_name2, selected)

    window.close()
    return rtn

