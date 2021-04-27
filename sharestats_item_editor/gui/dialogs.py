from os import path
import PySimpleGUI as sg

from .. import consts, __version__, __author__, info
from ..rexam.files import RmdFile
from ..rexam import r_render


def ask_save(item_name):
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
    win_titel = "View Files"
    content = [None, None]
    files = []
    for i, fl in enumerate((file, file2)):
        if isinstance(fl, RmdFile):
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
    sg.theme(old_theme)