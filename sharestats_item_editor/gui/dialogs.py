from os import path
import PySimpleGUI as sg

from .. import consts, templates, __version__, __author__, info
from ..misc import yesno, splitstrip
from ..taxonomy import Taxonomy
from ..item_sections import ItemMetaInfo
from ..rmd_exam_item import RmdExamItem
from ..files import ShareStatsFile
from .. import r_exams


def taxonomy(meta_info):
    """default_taxonomy needs to be comma separated as specified Rmd file
    """
    assert (isinstance(meta_info, ItemMetaInfo))

    tax = Taxonomy()
    default_taxonomy = "\n".join(splitstrip(meta_info.taxonomy, ","))
    default_type = "\n".join(splitstrip(meta_info.type_tag, ","))

    # LAYOUT
    layout = []
    sg.theme(consts.COLOR_THEME)

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
        [sg.Listbox(values=tax.get_tags_type(), size=(26, 10),
                    background_color=consts.COLOR_BKG_TAX_LIST, key="L_types"),
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

class _FrameMakeSSName(object):

    def __init__(self, default_name=""):

        default_name = path.splitext(default_name)[0] # remove possible extension
        defaults = [""] * 4
        if default_name.endswith(consts.TAG_BILINGUAL):
            defaults[3] = "Bilingual"
            default_name = default_name[:-1*len(consts.TAG_BILINGUAL)]
        elif default_name.endswith(consts.TAG_NL):
            defaults[3] = "Dutch"
            default_name = default_name[:-1*len(consts.TAG_NL)]
        elif default_name.endswith(consts.TAG_ENG):
            defaults[3] = "English"
            default_name = default_name[:-1*len(consts.TAG_ENG)]
        else:
            defaults[3] = ""

        for c, txt in enumerate(default_name.split("-", maxsplit=2)):
            if c == 2: # cast number
                try:
                    defaults[c] = str(int(txt))
                except:
                    defaults[c-1] += "-" + txt
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

        self.fln0 = sg.InputText(default_text=defaults[0],size=(5,1),
                                        key="fln0", enable_events=True)
        self.fln1 = sg.InputText(default_text=defaults[1], size=(25,1),
                                 key="fln1",enable_events=True)
        self.fln2 = sg.InputText(default_text=str(defaults[2]), size=(4,1),
                                 key="fln2",enable_events=True)
        self.fln3 = sg.DropDown(default_value=defaults[3],
                                values=["Dutch", "English", "Bilingual"],
                                key="fln3", enable_events=True)

        self.frame = sg.Frame("Item Name(s)",[
                               [sg.Text("Uni"+" "*11 + "Topic"+" "*24 +
                                        "Counter"+" "*7 + "Language")],
                                [self.fln0, sg.Text("-"),
                                self.fln1, sg.Text("-"),
                                self.fln2, sg.Text("-"),
                                self.fln3], [fr_names]
                            ])

    def update_names(self):
        # call me once after window created
        fln0 = self.fln0.get().strip().lower()
        fln1 = self.fln1.get().strip().lower()
        fln2 = self.fln2.get().strip()

        name1 = "-".join(filter(len, (fln0, fln1)))
        name2 = ""

        if len(name1):
            try:
                name1 += "-" + str(int(fln2)).zfill(3)
            except:
                pass

        if len(name1) > 0:
            lang = self.fln3.get()
            if lang == "Dutch":
                name1 = name1 + consts.TAG_NL
            elif lang == "English":
                name1 = name1 + consts.TAG_ENG
            elif lang == "Bilingual":
                name2 = name1 + consts.TAG_ENG
                name1 = name1 + consts.TAG_NL

        self.txt_name1.update(value=name1)
        self.txt_name2.update(value=name2)

    @property
    def name1(self):
        return self.txt_name1.get()

    @property
    def name2(self):
        return self.txt_name2.get()


def new_item(base_directory):
    sg.theme(consts.COLOR_THEME)

    lb_type = sg.Listbox(values=["None"] + list(consts.EXTYPES.values()),
                            default_values=["None"],
                         select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                         size=(26, 6), no_scrollbar=True,
                         key="lb_type")

    fr_make_name = _FrameMakeSSName()
    layout = [[fr_make_name.frame]]
    layout.append([sg.Frame("Template", [[lb_type]]),
                            sg.Cancel(size=(10, 2)),
                            sg.Button("Create", size=(10, 2), key="create")])
    window = sg.Window("New Item(s)", layout, finalize=True)
    fr_make_name.update_names()
    while True:
        window.refresh()
        event, v = window.read()

        if event is not None and event.startswith("fln"):
            fr_make_name.update_names()
        else:
            break

    item1, item2 = (None, None)
    if event == "create":
        # template
        sel = lb_type.get_indexes()[0]
        if sel > 0:
            template_key = list(consts.EXTYPES.keys())[sel - 1]
        else:
            template_key = None

        if len(fr_make_name.name1):
            item1 = RmdExamItem(path.join(base_directory, fr_make_name.name1,
                                        "{}.Rmd".format(fr_make_name.name1)))
            if template_key is not None:
                item1.import_file(templates.FILES[template_key])
        if len(fr_make_name.name2):
            item2 = RmdExamItem(path.join(base_directory, fr_make_name.name2,
                                        "{}.Rmd".format(fr_make_name.name2)))
            if template_key is not None:
                item2.import_file(templates.FILES[template_key])

    window.close()

    return item1, item2

def rename_item(item_name):
    sg.theme(consts.COLOR_THEME)

    fr_make_name = _FrameMakeSSName(item_name)
    fix_dir = sg.Checkbox(text="Adapt directory name", default=True)
    layout = [[fr_make_name.frame]]
    layout.append([sg.Frame("", [[fix_dir]]),
                  sg.Text(" "*10),
                  sg.Cancel(size=(10, 2)),
                  sg.Button("Rename", size=(10, 2), key="rename")])
    window = sg.Window("Rename", layout, finalize=True)
    fr_make_name.update_names()

    while True:
        window.refresh()
        event, _ = window.read()
        if event is not None and event.startswith("fln"):
            fr_make_name.update_names()
        else:
            break

    window.close()
    if event=="rename":
        return fr_make_name.name1, fr_make_name.name2, bool(fix_dir.get())
    else:
        return None, None, None



def ask_save(item_name):
    sg.theme(consts.COLOR_THEME)

    layout = [[sg.Text("Unsave changes in '{}'".format(item_name))]]
    layout.append([sg.Save("Save item", key="save"),
                   sg.Cancel("Dismiss changes")])
    window = sg.Window("Save?", layout, finalize=True)
    while True:
        window.refresh()
        event, v = window.read()
        break

    window.close()

    return event == "save"

def show_text_file(file, file2=None):
    sg.theme(consts.COLOR_THEME)
    win_titel = "View Files"
    content = [None, None]
    files = []
    for i, fl in enumerate((file, file2)):
        if isinstance(fl, ShareStatsFile):
            win_titel = "View Files: {}".format(fl.name)
            fl = fl.full_path
        try:
            with open(fl, "r") as fl_hdl:
                content[i] = fl_hdl.readlines()
            files.append(fl)
        except:
            pass

    if len(files)==0:
        return

    tabs = []
    for c, f in zip(content, files):
        if c is not None:
            tabs.append(sg.Tab("{}".format(path.split(f)[1]),
                    [[sg.Text("File: {}".format(f))],
                    [sg.Multiline(default_text="".join(c),
                        disabled=True, size=(80, 40))]]))

    layout = [[sg.TabGroup([tabs])],
              [sg.CloseButton("Close")]]
    window = sg.Window(win_titel, layout, finalize=True)
    window.refresh()
    while True:
        window.refresh()
        event, v = window.read()
        break
    window.close()


def render(file):
    if isinstance(file, ShareStatsFile):
        file = file.full_path
    r = r_exams.RExams()
    if r.r_init_error is not None:
        sg.Print(r.r_init_error)
        return

    error = r.rmd_to_html(file)
    if error is None:
        r.open_html(new=0)
    else:
        sg.Print(error)

def about():
    sg.theme("DarkBlack")
    width = 40

    layout = [[sg.Text(consts.APPNAME, size=(width , 1), font='bold',
                       justification='center')],
              [sg.Text("Version {}".format(__version__), font='bold',
                       size=(width , 1),
                       justification='center')],
              [sg.Text(" " * 22), sg.Image(path.join(path.dirname(__file__),
                                                     "essb.png"))],
              [sg.Text("")] ]


    info_array = ["(c) {}".format(__author__), ""] + info() +\
            ["", "website: https://github.com/essb-mt-section/sharestats-item" \
                                        "-editor"]

    layout.append([sg.Multiline(default_text="\n".join(info_array),
                                size=(55, len(info_array)),
                                border_width=0,
                                background_color='black',
                                auto_size_text=True,
                                no_scrollbar=True,
                                text_color='white')])

    window = sg.Window("About", layout, finalize=True)
    window.refresh()
    while True:
        window.refresh()
        event, v = window.read()
        break
    window.close()