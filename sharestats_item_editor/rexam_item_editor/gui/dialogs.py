from os import path
import PySimpleGUI as sg

from .. import sysinfo, __version__, __author__, APPNAME, templates
from ..consts import FILE_ENCODING
from ..rexam import r_render, extypes
from ..rexam.rmd_file import RmdFile, SEP, TAG_L1, TAG_L2, TAG_BILINGUAL
from ..rexam.item import RExamItem


def ask_save(item_name, txt=None):
    if txt is None:
        layout = []
    else:
        layout = [[sg.Text(txt)], [sg.Text("")]]
    layout.extend([[sg.Text("There are unsaved changes in '{}'.".format(
        item_name))],
              [sg.Save("Save", key="save"),
               sg.Cancel("Dismiss changes")]])
    window = sg.Window("{}".format(item_name), layout, finalize=True,
                       modal=True, keep_on_top=True)
    while True:
        window.refresh()
        event, v = window.read()
        break

    window.close()
    return event == "save"


def show_text_file(file, file2=None):
    win_titel = "View Files"
    content = [None, None]
    files = []
    for i, fl in enumerate((file, file2)):
        if isinstance(fl, RmdFile):
            win_titel = "View Files: {}".format(fl.name)
            fl = fl.full_path
        try:
            with open(fl, "r", encoding=FILE_ENCODING) as fl_hdl:
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
    if isinstance(file, RmdFile):
        file = file.full_path
    r = r_render.RRender()
    if r.r_init_error is not None:
        sg.Print(r.r_init_error)
        return

    error = r.rmd_to_html(file)
    if error is None:
        r.open_html(new=0)
    else:
        sg.Print(error)


def about():
    old_theme = sg.theme()
    sg.theme("DarkBlack")
    width = 40

    layout = [[sg.Text(APPNAME, size=(width , 1), font='bold',
                       justification='center')],
              [sg.Text("Version {}".format(__version__), font='bold',
                       size=(width , 1),
                       justification='center')],
              [sg.Text(" " * 22), sg.Image(path.join(path.dirname(__file__),
                                                     "essb.png"))],
              [sg.Text("")] ]

    info_array = ["(c) {}".format(__author__), ""] + sysinfo.info()

    layout.append([sg.Multiline(default_text="\n".join(info_array),
                                size=(55, len(info_array)),
                                border_width=0,
                                background_color='black',
                                auto_size_text=True,
                                no_scrollbar=True,
                                text_color='white')])

    window = sg.Window("About", layout, finalize=True,
                       modal=True, keep_on_top=True)
    window.refresh()
    while True:
        window.refresh()
        event, v = window.read()
        break
    window.close()
    sg.theme(old_theme)


class FrameMakeName(object):

    def __init__(self, default_name=""):

        default_name = path.splitext(default_name)[0] # remove possible extension
        defaults = [""] * 3
        if default_name.endswith(TAG_BILINGUAL):
            defaults[-1] = "Bilingual"
            default_name = default_name[:-1*len(TAG_BILINGUAL)]
        elif default_name.endswith(TAG_L1):
            defaults[-1] = "Dutch"
            default_name = default_name[:-1*len(TAG_L1)]
        elif default_name.endswith(TAG_L2):
            defaults[-1] = "English"
            default_name = default_name[:-1*len(TAG_L2)]
        else:
            defaults[-1] = ""

        for c, txt in enumerate(default_name.split(SEP, maxsplit=2)):
            if c == len(defaults)-2: # cast number
                try:
                    defaults[c] = str(int(txt))
                except:
                    defaults[c-1] += SEP + txt
            else:
                defaults[c] = txt

        self.txt_name1 = sg.Text("", size=(43, 1), key="txt_name1")
        self.txt_name2 = sg.Text("", size=(43, 1), key="txt_name2")
        self.fr_names = sg.Frame("", [[sg.Text("a:", size=(2,1)),
                                  self.txt_name1],
                                 [sg.Text("b:" , size=(2,1)),
                                  self.txt_name2]],
                                  border_width=0)

        self.fln = [sg.InputText(default_text=defaults[0], size=(25,1),
                                 enable_events=True)] # could have potentiall
                                                     # multiple parts
        self.fln_cnt = sg.InputText(default_text=str(defaults[-1]), size=(4, 1),
                                    enable_events=True)

        self.fln_lang = sg.DropDown(default_value=defaults[-1],
                                    values=["Dutch", "English", "Bilingual"],
                                    enable_events=True)

        self.frame = sg.Frame("Item Name(s)",[
            [top_label([self.fln[0], sg.Text(SEP)], label="Topic"),
             top_label([self.fln_cnt, sg.Text(SEP)], label="Counter"),
             top_label(self.fln_lang, label="Language")],
             [self.fr_names]
             ])

    def update_names(self):
        # call me once after window created
        name_parts = map(lambda x: x.get().strip().lower(), self.fln)
        fln_cnt = self.fln_cnt.get().strip()

        name1 = SEP.join(filter(lambda x:len(x), name_parts))
        name2 = ""

        if len(name1):
            try:
                name1 += SEP + str(int(fln_cnt)).zfill(3)
            except:
                pass

        if len(name1) > 0:
            lang = self.fln_lang.get()
            if lang == "Dutch":
                name1 = name1 + TAG_L1
            elif lang == "English":
                name1 = name1 + TAG_L2
            elif lang == "Bilingual":
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


def new_item(base_directory):
    fr_make_name = FrameMakeName()
    lb_type = sg.Listbox(values=["None"] + list(extypes.EXTYPES.values()),
                         default_values=["None"],
                         select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                         size=(26, 6), no_scrollbar=True,
                         key="lb_type")

    layout = [[fr_make_name.frame]]
    layout.append([sg.Frame("Template", [[lb_type]]),
                   sg.Cancel(size=(10, 2)),
                   sg.Button("Create", size=(10, 2), key="create")])
    window = sg.Window("New Item(s)", layout, finalize=True,
                       modal=True, keep_on_top=True)
    fr_make_name.update_names()
    while True:
        window.refresh()
        event, v = window.read()
        if event in ("Cancel", "create", None):
            break
        else:
            fr_make_name.update_names()

    item1, item2 = (None, None)
    if event == "create":
        # template
        sel = lb_type.get_indexes()[0]
        if sel > 0:
            template_key = list(extypes.EXTYPES.keys())[sel - 1]
        else:
            template_key = None

        if len(fr_make_name.name1):
            rel_path = path.join(fr_make_name.name1,
                            "{}{}".format(fr_make_name.name1,RmdFile.SUFFIX))
            item1 = RExamItem(RmdFile(file_path=rel_path,
                                    base_directory = base_directory))
            if template_key is not None:
                item1.import_file(templates.FILES[template_key])
        if len(fr_make_name.name2):
            rel_path = path.join(fr_make_name.name2,
                        "{}{}".format(fr_make_name.name2, RmdFile.SUFFIX))
            item2 = RExamItem(RmdFile(file_path=rel_path,
                                    base_directory = base_directory))
            if template_key is not None:
                item2.import_file(templates.FILES[template_key])

    window.close()

    return item1, item2

def rename_item(item_name):
    fr_make_name = FrameMakeName(item_name)
    fix_dir = sg.Checkbox(text="Adapt directory name", default=True)
    layout = [[fr_make_name.frame]]
    layout.append([sg.Frame("", [[fix_dir]]),
                   sg.Text(" "*10),
                   sg.Cancel(size=(10, 2)),
                   sg.Button("Rename", size=(10, 2), key="rename")])
    window = sg.Window("Rename", layout, finalize=True,
                       modal=True, keep_on_top=True)
    fr_make_name.update_names()

    while True:
        window.refresh()
        event, _ = window.read()
        if event in ("Cancel", "rename", None):
            break
        else:
            fr_make_name.update_names()

    window.close()
    if event=="rename":
        return fr_make_name.name1, fr_make_name.name2, bool(fix_dir.get())
    else:
        return None, None, None

#TODO rendering picture
#TODO rename no language