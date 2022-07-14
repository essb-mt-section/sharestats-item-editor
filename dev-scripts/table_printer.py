class TablePrinter(object):

    ROW_SEP_CHAR = "-"
    COL_SEP_CHAR = "|"
    CROSS_CHAR = "+"
    CUTTED_TEXT_SYMBOL = ".."

    def __init__(self, table_data, first_row_is_heading=False):

        self.data = []
        ncol = None
        for nrows, row in enumerate(table_data):
            # check data
            if isinstance(row, (tuple, list)):
                if nrows==0:
                    ncol = len(row)
                else:
                    if len(row) != ncol:
                        raise ValueError("Number of columns does not match in row {}".format(
                                        nrows))
            else:
                raise ValueError("Not well shaped table data. Table_data must " 
                                 "be a two dimensional array.")
            # make strings and copy data
            self.data.append([str(c) for c in row])

        if first_row_is_heading:
            self.heading = self.data.pop(0)
        else:
            self.heading = None

    def n_row(self):
        return len(self.data)

    def n_column(self):
        return len(self.data[0])

    def _get_max_length_in_columns(self):
        rtn = [0]*self.n_column()
        for r in self.data:
            for cnt, col in enumerate(r):
                l = len(col)
                if l>rtn[cnt]:
                    rtn[cnt] = l
        return rtn

    def text(self,
             column_width=None,
             column_sep = True,
             row_sep = False,
             wrap_text = True,
             max_wrap_text_lines = 4):

        if column_width is None:
            column_width = self._get_max_length_in_columns()

        if len(column_width) != self.n_column():
            ValueError("Column width array does not match number of columns.")

        if column_sep:
            col_sep_txt = " " + TablePrinter.COL_SEP_CHAR + " "
        else:
            col_sep_txt = ""

        row_sep_txt = ""
        rtn = ""
        for row in self.data:
            #make row
            wrap_row_cnt = 1
            while True:
                if wrap_text and (max_wrap_text_lines is None or
                        wrap_row_cnt<max_wrap_text_lines):
                    cut = "" # wrapping
                else:
                    # no wrapping
                    cut = TablePrinter.CUTTED_TEXT_SYMBOL

                txt_row, row = _formated_single_row(row,
                                                    column_width=column_width,
                                                    cutted_text_symbol=cut,
                                                    col_sep_txt=col_sep_txt)
                rtn += txt_row + "\n"
                wrap_row_cnt += 1

                if len(cut)>0 or sum([len(x) for x in row])==0:
                    # no wrapping or wrapping done
                    break

            if row_sep:
                if len(row_sep_txt)==0:
                    # make once the row_seperator
                    row_sep_txt = [TablePrinter.ROW_SEP_CHAR] * len(txt_row)
                    for x in _find_all_chars(txt_row, TablePrinter.COL_SEP_CHAR):
                        row_sep_txt[x] = TablePrinter.CROSS_CHAR
                    row_sep_txt = "".join(row_sep_txt) # string from array of char
                rtn += row_sep_txt + "\n"

        if row_sep:
            rtn = row_sep_txt + "\n" + rtn

        return rtn


def _formated_single_row(row_data, column_width, cutted_text_symbol,
                         col_sep_txt):

    c = len(cutted_text_symbol)
    txt_row = col_sep_txt
    not_printed = []
    for w, cell in zip(column_width, row_data):
        if len(cell) > w:
            # cut to long cells
            not_printed.append(cell[(w - c):])
            cell = cell[:(w - c)] + cutted_text_symbol
        else:
            not_printed.append("")
        txt_row += cell + " " * (w - len(cell)) + col_sep_txt

    if len(col_sep_txt):
        txt_row = txt_row[1:] # remove first space

    return txt_row.rstrip(), not_printed


def _find_all_chars(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

if __name__ == "__main__":

    a = [["sdfsdr", "hhjk", "Rsydgfasds",
         ["sd", "okin asdfl asdf asdjh sadölfhokin asdfl asdf asdjh "
                    "sadölfhokin asdfl asdf asdjh sadölfhokin asdfl asdf "
                   "asdjh sadölfhokin asdfl asdf asdjh sadölfh ", "fsda"],
         ["asdf", 4.7, "asd"]]

    fm = TablePrinter(a, first_row_is_heading=False)
    txt = fm.text(column_width=[8, 20, 9])
    print(txt)
