import re
import sys
from PyPDF4 import PdfFileReader, PdfFileWriter
from PyQt5.QtWidgets import (
    QRadioButton, QApplication, QMainWindow, QStatusBar, QToolBar, QLineEdit,
    QFileDialog, QDialog, QLabel, QSpinBox, QDialogButtonBox, QVBoxLayout
)
from PyQt5.QtCore import Qt

PreventContextMenu = Qt.ContextMenuPolicy.PreventContextMenu


class MainWindow(QMainWindow):
    def __init__(self, parent=None, dropfile=None):
        super().__init__(parent)

        self.setWindowTitle("Separar PDF")
        self.resize(800, 600)
        self.setAcceptDrops(True)
        self._createMenu()
        self._addWidgets()
        self._createStatusBar()
        self._createToolbar()
        self.show()
        if dropfile:
            self._filepath.setText(dropfile)
            
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            path = e.mimeData().urls()[0].path()[1:]
            if path.endswith('.pdf'):
                e.accept()
            else:
                e.ignore()
        else:
            e.ignore()

    def dropEvent(self, e):
        path = e.mimeData().urls()[0].path()[1:]
        self._filepath.setText(path)
        
    def _createMenu(self):
        self.menu = self.menuBar()
        self.menu.addAction('&Abrir', self.fileSelect)
        self.menu.addAction('&Separar', self.split)
        self.menu.addAction('&Fechar', self.close)
        
    def _addWidgets(self):
        self._filepath = QLineEdit(self)
        self._npages = QSpinBox(self)
        self._npages.setMinimum(1)
        self._npages.setMinimumWidth(150)

    def _createStatusBar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _createToolbar(self):
        pathToolBar = QToolBar()
        pathToolBar.setMovable(False)
        pathToolBar.setContextMenuPolicy(PreventContextMenu)
        pathToolBar.addWidget(self._filepath)
        self.addToolBar(pathToolBar)
        self.addToolBarBreak()

        choiceToolBar = QToolBar()
        choiceToolBar.setMovable(False)
        choiceToolBar.setContextMenuPolicy(PreventContextMenu)
        self.addToolBar(choiceToolBar)
        self.n_choice = QRadioButton("Separar a cada 'n' páginas")
        self.n_choice.setChecked(True)
        self.n_choice.toggled.connect(self.changeShownWidgets)
        group_choice = QRadioButton("Separar páginas específicas")
        choiceToolBar.addWidget(self.n_choice)
        choiceToolBar.addWidget(group_choice)
        self.addToolBarBreak()
        
        self.ntoolbar = QToolBar()
        self.ntoolbar.setVisible(True)
        self.ntoolbar.setMovable(False)
        self.ntoolbar.setContextMenuPolicy(PreventContextMenu)
        self.addToolBar(self.ntoolbar)
        self.ntoolbar.addWidget(self._npages)
        
        self._paths = []
        self._pagegroups = []
        self.grouptoolbars = [QToolBar()]
        self.grouptoolbars[0].setVisible(False)
        self.grouptoolbars[0].setMovable(False)
        self.grouptoolbars[0].setContextMenuPolicy(PreventContextMenu)
        self.addGroupWidget(self.grouptoolbars[0])
        self.addToolBar(self.grouptoolbars[0])
        
    def addGroupWidget(self, toolbar):
        path = QLineEdit(toolbar)
        pagegroup = QLineEdit(toolbar)
        self._paths.append(path)
        self._pagegroups.append(pagegroup)
        nome = QLabel("Nome:")
        nome.setMinimumWidth(80)
        pag = QLabel("Páginas:")
        pag.setMinimumWidth(80)
        toolbar.addWidget(nome)
        toolbar.addWidget(path)
        toolbar.addSeparator()
        toolbar.addWidget(pag)
        toolbar.addWidget(pagegroup)
        toolbar.addSeparator()
        toolbar.addAction("Adicionar", self.addGroupToolBar)
        if len(self.grouptoolbars) > 1:
            toolbar.addAction("Remover", self.removeGroupToolBar)
        
    def addGroupToolBar(self):
        self.addToolBarBreak()
        self.grouptoolbars.append(QToolBar())
        tool = self.grouptoolbars[-1]
        tool.setVisible(True)
        tool.setMovable(False)
        tool.setContextMenuPolicy(PreventContextMenu)
        self.addGroupWidget(tool)
        self.addToolBar(tool)
        
    def removeGroupToolBar(self):
        tool = self.sender().parentWidget()
        n = self.grouptoolbars.index(tool)
        self.grouptoolbars.pop(n)
        self._paths.pop(n)
        self._pagegroups.pop(n)
        self.removeToolBar(tool)

    def changeShownWidgets(self):
        if self.sender().isChecked():
            self.ntoolbar.setVisible(True)
            for toolbar in self.grouptoolbars:
                toolbar.setVisible(False)
        else:
            self.ntoolbar.setVisible(False)
            for toolbar in self.grouptoolbars:
                toolbar.setVisible(True)
        
    def fileSelect(self):
        dlg = QFileDialog()
        dlg.ExistingFile
        dlg.setAcceptMode(QFileDialog.AcceptOpen)
        filepath = dlg.getOpenFileName(
            self, self.tr("Selecione o arquivo que deseja separar"), "",
            self.tr("Arquivos PDF (*.pdf)")
        )
        if filepath[0]:
            self._filepath.setText(filepath[0])
            
    def split(self):
        
        def getPages(pagegroup):
            pages = []
            page = re.split(",|;", pagegroup.text())
            for x in page:
                if "-" in x:
                    r = x.split("-")
                    pages.extend(range(int(r[0]), int(r[1])+1))
                else:
                    pages.append(int(x))
            return pages
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        path = self._filepath.text()
        try:
            pdffile = PdfFileReader(path)
        except Exception as e:
            QApplication.restoreOverrideCursor()
            MsgBox(self, "Arquivo inválido!",
                   f"Não foi possível ler o arquivo selecionado\nErro: {e}")
            return
        numpages = pdffile.getNumPages()
        pages = pdffile.pages
        if self.n_choice.isChecked():
            savepath = path.split(".pdf")[0]
            n = self._npages.value()
            if n > numpages:
                QApplication.restoreOverrideCursor()
                MsgBox(self, "Valor Inválido!",
                       "Valor informado maior que a quantidade de páginas!")
                return
            for i in range(0, numpages, n):
                writer = PdfFileWriter()
                for page in pages[i:n+i]:
                    writer.addPage(page)
                with open(f"{savepath} {i+1} - {n+i}.pdf", "wb") as f:
                    writer.write(f)
        else:
            savepath = "/".join(path.split("/")[0:-1])
            for i in range(len(self._paths)):
                name = self._paths[i].text()
                pdffile = PdfFileReader(path)
                pages = pdffile.pages
                writer = PdfFileWriter()
                pagesgroup = getPages(self._pagegroups[i])
                for page in pagesgroup:
                    writer.addPage(pages[page-1])
                with open(f"{savepath}\\{name}.pdf", "wb") as f:
                    writer.write(f)
        QApplication.restoreOverrideCursor()
        MsgBox(self, "Concluído!", "Arquivo separado!")


class MsgBox(QDialog):
    def __init__(self, parent, title, msg):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.text = QLabel(msg)
        self.button = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        self.exec_()


if __name__ == '__main__':
    dropfile = sys.argv[1] if len(sys.argv) > 1 else None
    app = QApplication([])
    window = MainWindow(None, dropfile)
    window.show()
    app.exec_()
    QApplication.restoreOverrideCursor()