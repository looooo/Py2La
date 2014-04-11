# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import popplerqt4
from PyQt4.Qsci import QsciScintilla, QsciLexerPython
from sympy import latex, sympify, N
import tempfile
import os

class mywidget(QtGui.QWidget):
    def __init__(self):
        super(mywidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.splitter = QtGui.QSplitter(self)
        self.horizontal_layout = QtGui.QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.splitter)
        self.editor_widget = QtGui.QWidget(self)
        self.editor_widget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)

        self.verticalLayout = QtGui.QVBoxLayout(self.editor_widget)
        self.editor = PythonEditor(self.editor_widget)
        self.editor.setText(open("example.py").read())
        self.pdf_widget = pdf_widget(self)
        self.pdf_widget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.create_document_button = QtGui.QPushButton("create document", self.editor_widget)
        self.create_document_button.clicked.connect(self.create_document)
        QtGui.QShortcut(QtGui.QKeySequence("f1"), self.editor_widget, self.create_document)
        self.splitter.splitterMoved.connect(self.scale_pdf)
        self.splitter.addWidget(self.editor_widget)
        
        self.splitter.addWidget(self.pdf_widget)
        self.verticalLayout.addWidget(self.editor)
        self.verticalLayout.addWidget(self.create_document_button)
        self.create_document()

        self.splitter.setSizes([self.width() / 2, self.width() / 2])

    def create_document(self):
        tempfile.mktemp()
        text = self.editor.text()
        print(text)
        latex_code = py2la(str(text))
        tmp_dir = tempfile.tempdir
        tex_tmp = "example.tex"
        tex_tmp_file = open(tmp_dir + "/" + tex_tmp, "w")
        tex_tmp_file.write(prependtext)
        tex_tmp_file.write(latex_code.out)
        tex_tmp_file.write(appendtext)
        tex_tmp_file.close()
        os.system(
        	"pdflatex -interaction=batchmode -jobname=ausgabe" + 
        	" -output-directory=" + tmp_dir + " " + tmp_dir + "/" + tex_tmp
        	)
        self.pdf_widget.setpdf(tmp_dir + "/ausgabe.pdf")

    def scale_pdf(self):
        self.pdf_widget.resetsize()


class pdf_widget(QtGui.QWidget):
    def __init__(self, parent = None):
        super(pdf_widget, self).__init__()
        self.current_page = 0
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.pdf = PdfViewer(self)
        self.verticalLayout.addWidget(self.pdf)
        self.horizontal_widget = QtGui.QWidget(self)
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontal_widget)
        self.page_number = QtGui.QSpinBox(self.horizontal_widget)
        self.next_page_button = QtGui.QPushButton("next", self)
        self.next_page_button.clicked.connect(self.next_page)
        self.prev_page_button = QtGui.QPushButton("prev", self)
        self.prev_page_button.clicked.connect(self.prev_page)
        self.page_number.valueChanged.connect(self.set_page)
        self.horizontalLayout.addWidget(self.page_number)
        self.horizontalLayout.addWidget(self.prev_page_button)
        self.horizontalLayout.addWidget(self.next_page_button)
        self.verticalLayout.addWidget(self.horizontal_widget)

    def next_page(self):
        if self.current_page + 1 < self.pdf.doc.numPages():
            self.current_page += 1
            self.pdf.setpage(self.current_page)
            self.page_number.setValue(self.current_page)

    def prev_page(self):
        if self.current_page != 0:
            self.current_page -= 1
            self.pdf.setpage(self.current_page)
            self.page_number.setValue(self.current_page)

    def set_page(self, pagenumber):
        if pagenumber >= 0 and pagenumber <= self.pdf.doc.numPages():
            self.current_page = pagenumber
            self.pdf.setpage(self.current_page)

    def setpdf(self, path):
        self.pdf.loadpdf(path)
        self.set_page(self.existing_pagenumber())
        self.page_number.setMaximum(self.pdf.doc.numPages()-1)

    def existing_pagenumber(self):
        if self.pdf.doc.numPages()-1 < self.current_page:
            return(self.pdf.doc.numPages()-1)
        return(self.current_page)

    def resetsize(self):
        self.pdf.reset_pixmap()



class PdfViewer(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        super(PdfViewer, self).__init__()
        self.scene = QtGui.QGraphicsScene(self)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setScene(self.scene)
        self.loadpdf('ausgabe.pdf')
        self.setpage(0)

    def loadpdf(self, path):
        self.doc = popplerqt4.Poppler.Document.load(path)
        self.doc.setRenderHint(popplerqt4.Poppler.Document.Antialiasing and popplerqt4.Poppler.Document.TextAntialiasing)

    def setpage(self, pagenumber):
        self.page = self.doc.page(pagenumber)
        image = self.page.renderToImage(self.width()/8.27, self.width()/8.27)
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.scene.clear()
        self.setTransform(QtGui.QTransform())
        self.scene.addPixmap(self.pixmap)

    def reset_pixmap(self):
        self.page = self.doc.page(0)
        image = self.page.renderToImage(self.width()/8.27, self.width()/8.27)
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.scene.clear()
        self.setTransform(QtGui.QTransform())
        self.scene.addPixmap(self.pixmap)


# copied from:
##### -------------------------------------------------------------------------
# qsci_simple_pythoneditor.pyw

# QScintilla sample with PyQt

# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
##### -------------------------------------------------------------------------

class PythonEditor(QsciScintilla):
    ARROW_MARKER_NUM = 8

    def __init__(self, parent=None):
        super(PythonEditor, self).__init__(parent)
        # Set the default font
        self.setUtf8(False)
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QtGui.QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.connect(self,
            QtCore.SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'),
            self.on_margin_clicked)
        self.markerDefine(QsciScintilla.RightArrow,
            self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee1111"),
            self.ARROW_MARKER_NUM)

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))
        # Set Python lexer
        # Set style for Python comments (style number 1) to a fixed-width
        # courier.
        #
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 0, 'Courier')

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 1)

        # not too small
        self.setMinimumSize(100, 200)

    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)


prependtext = (
    r'\documentclass[nenglish,fleqn,a4paper]{article}'
    '\n'
    r'\usepackage[utf8]{inputenc}'
    '\n'
    r'\usepackage{babel}'
    '\n'
    r'\usepackage{amsmath}'
    '\n'
    r'\usepackage{graphicx}'
    '\n'
    r'\usepackage{titlesec}'
    '\n'
    r'\begin{document}')

testoperator = ["=", "<", ">", "=="]

appendtext = "\end{document}"


class py2la():

    def __init__(self, string):
        self.string = string
        self.latex = []
        self.out = ""
        self.unit = ""
        self.equstr = ""
        self.equunit = ""
        self.equationOn = False
        self.textOn = False
        self.dic = {}
        self.proceed = True
        self.run()
        self.stringopen = False
        if self.proceed:
            self.getLatex()

    def run(self):
        try:
            exec(self.string, {}, self.dic)
            self.proceed = True
        except:
            print(Exception)
            print("warning: the file is not execable")
            self.proceed = False

    def getLatex(self):
        self.string = self.string.rsplit("\n")
        for s in self.string:
            if s[0:3] == "# L":
                s = s[0] + s[2:]
            if s[0:2] == "#L":
                s = s[2:].rsplit("->")
                if len(s) == 2:
                    s[0] = s[0].replace(" ", "")
                    if s[0] == "text":
                        s[1] = s[1].replace(" ", "")
                        self.textOn = self.change(s[1])
                    elif s[0] == "equation":
                        s[1] = s[1].replace(" ", "")
                        self.equationOn = self.change(s[1])
                    else:
                        self.out += '\\' + s[0] + "{" + s[1] + "}\n"
                elif len(s) == 1:
                    self.out += s[0] + '\n'
            else:
                if self.equationOn:
                    self.equlatexform1(s)
                elif self.textOn:
                    self.txtlatexform(s)

    def change(self, onoff):
        if onoff == "on":
            out = True
        elif onoff == "off":
            out = False
        return out

    def equlatexform(self, string):
        if len(string) > 0:
            if string[0:3] in ('"""', "'''"):
                self.equstr += string.replace(string[0:3], "")
            elif string[0] in ('"', "'"):
                self.equunit += string.replace(string[0], "")
            else:
                string = string.replace(" ", "")
                string = string.rsplit("=")
                if len(string) == 2:
                    self. out += "\\begin{flalign} \n"
                    temp0 = latex(sympify(string[0]))
                    temp1 = latex(
                        sympify(string[1], convert_xor=True, strict=False, rational=False), mul_symbol="dot")
                    try:
                        temp2 = str(N(self.dic[string[0]], 6))
                    except:
                        print("warning warning")
                    if temp1 == temp2 or sympify(string[1]) == self.dic[string[0]]:
                        self.out += temp0 + "=" + temp1
                    else:
                        self.out += temp0 + "=" + temp1 + "=" + temp2
                    if len(self.equunit) > 0:
                        self.out += "\:" + latex(sympify(self.equunit))
                        self.equunit = ""
                    if len(self.equstr) > 0:
                        self.out += "& & \\text{" + self.equstr + "}\n"
                        self.equstr = ""
                    else:
                        self.out += "& & \\text{""}\n"
                    self.out += "\\end{flalign}\n"

    def equlatexform1(self, string):
        outlist = []
        if len(string) > 0:
            if string[0:3] in ('"""', "'''"):
                self.equstr += string.replace(string[0:3], "")
            elif string[0] in ('"', "'"):
                self.equunit += string.replace(string[0], "")
            else:
                string = string.replace(" ", "")
                string = equtoparts(string)
                self. out += "\\begin{flalign} \n"
                for equ in string:
                    if equ in testoperator:
                        outlist.append(equ)
                    else:
                        if equ[:9] == "integrate":
                            outlist.append(latex(sympify("Integral" + equ[9:])))
                            outlist.append("=")
                        outlist.append(latex(sympify(equ, convert_xor=True, strict=False, rational=False), mul_symbol="dot"))
                if isstringnumber(str(self.dic[string[0]])):
                    if isstringnumber(outlist[-1]) == False:
                        outlist.append("=" + str(N(self.dic[string[0]], 6)))
                elif isinstance(self.dic[string[0]], bool):
                    outlist.append("\Rightarrow " + str(self.dic[string[0]]))
                else:
                    pass
                for equ in outlist:
                    self.out += equ
                if len(self.equunit) > 0:
                        self.out += "\:" + latex(sympify(self.equunit))
                        self.equunit = ""
                if len(self.equstr) > 0:
                    self.out += "& & \\text{" + self.equstr + "}\n"
                    self.equstr = ""
                else:
                    self.out += "& & \\text{""}\n"
                self.out += "\\end{flalign}\n"

    def txtlatexform(self, string):
        if len(string) > 0:
            if self.stringopen:
                if string[-3:] == ('"""' or "'''"):
                    self.stringopen = False
                    self.out += string.replace(string[-3:],"")
                else:
                    self.out += string
            elif string[0:3] == ('"""' or "'''"):
                self.stringopen = True
                if string[-3:] == ('"""' or "'''") and string[-3:] != string[:3]:
                    self.stringopen = False
                self.out += string.replace(string[0:3],"")
            elif string[0:2] != ('""' or "''"):
                if string[0] == ('"' or "'"):
                    self.out += string.replace(string[0], "")


def equtoparts(string):
        equations = []
        inp = ""
        for i in string:
            if i in testoperator:
                if len(inp) > 0:
                    equations.append(inp)
                    inp = ""
                equations.append(i)
            else:
                inp += i
        equations.append(inp)
        return(equations)


def deleteduplicates(t):
    s = []
    for i in t:
        if i not in s:
            s.append(i)
    return(s)


def isstringnumber(string):
    try:
        float(string)
    except ValueError:
        return(False)
    else:
        if string in ("True", "False"):
            return(False)
        else:
            return(True)



class py2la_parser():
	def __init__(self, expr):
		pass

	def get_line(self):
		pass

	def store_keyword(self):
		pass

	def preparse(self):
		"""join strings, look for errors"""
		pass


class py2la_line_parser(object):
	def __init__(self, celltype):
		pass

	def parse_line(self):
		pass

	def has_keyword(self):
		pass


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        mw = mywidget()
        self.setCentralWidget(mw)
        shortcutFull = QtGui.QShortcut(self)
        shortcutFull.setKey(QtGui.QKeySequence('F11'))
        shortcutFull.setContext(QtCore.Qt.ApplicationShortcut)
        shortcutFull.activated.connect(self.toggle_fullscreen)
        self.showMaximized()

    def toggle_fullscreen(self):
        if self.windowState() & QtCore.Qt.WindowFullScreen:
            self.showMaximized()
        else:
            self.showFullScreen()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())