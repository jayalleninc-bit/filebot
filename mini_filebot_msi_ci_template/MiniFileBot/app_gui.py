from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from pathlib import Path
import yaml, sys, traceback
from engine.core import Engine

CFG=Path('config.yaml')
def load(): return yaml.safe_load(CFG.read_text()) if CFG.exists() else {}
def save(cfg): CFG.write_text(yaml.safe_dump(cfg, sort_keys=False))

class App(QWidget):
  def __init__(self):
    super().__init__(); self.setWindowTitle('Mini FileBot — Rename')
    self.cfg=load(); self.engine=None; self.roots=[]; self.plans=[]
    self.ui()
  def ui(self):
    v=QVBoxLayout(self)
    top=QHBoxLayout(); self.add=QPushButton('Add Folder'); self.db=QComboBox(); self.db.addItems(['Auto','TMDb','TVDB','AniList'])
    self.fetch=QPushButton('Fetch Data'); self.match=QPushButton('Match'); self.rename=QPushButton('Rename')
    top.addWidget(self.add); top.addStretch(1); top.addWidget(QLabel('Database:')); top.addWidget(self.db); top.addWidget(self.fetch); top.addWidget(self.match); top.addWidget(self.rename); v.addLayout(top)
    cols=QHBoxLayout(); self.left=QListWidget(); self.left.setToolTip('Original Files — drop here'); self.left.setAcceptDrops(True); self.left.setDragDropMode(QListWidget.DropOnly)
    mid=QVBoxLayout(); mid.addWidget(QLabel('→')); self.right=QListWidget(); self.right.setToolTip('New Names (preview)')
    cols.addWidget(self.left,4); midw=QWidget(); midw.setLayout(mid); cols.addWidget(midw,1); cols.addWidget(self.right,5); v.addLayout(cols)
    self.progress=QProgressBar(); v.addWidget(self.progress); self.log=QTextEdit(); self.log.setReadOnly(True); v.addWidget(self.log)
    self.add.clicked.connect(self.on_add); self.fetch.clicked.connect(self.on_fetch); self.match.clicked.connect(self.on_match); self.rename.clicked.connect(self.on_rename)
  def ensure_engine(self):
    if not self.engine:
      self.cfg.setdefault('providers',{})['preference']=self.db.currentText(); save(self.cfg); self.engine=Engine(self.cfg)
  def on_add(self):
    d=QFileDialog.getExistingDirectory(self,'Choose folder to scan')
    if d: self.roots.append(Path(d)); self.log.append(f'Added: {d}')
  def on_fetch(self):
    if not self.roots: QMessageBox.information(self,'No folders','Add a folder first.'); return
    self.ensure_engine(); self.left.clear(); self.plans=[]; tot=len(self.roots)
    for i,r in enumerate(self.roots,1):
      self.plans+=self.engine.plan_batch(r); self.progress.setValue(int(i/tot*100))
    for s,_ in self.plans: self.left.addItem(str(s))
    self.log.append(f'Fetched {len(self.plans)} file(s).')
  def on_match(self):
    if not self.plans: QMessageBox.information(self,'Nothing to match','Click Fetch Data first.'); return
    self.right.clear(); [self.right.addItem(str(d)) for _,d in self.plans]; self.log.append('Matched — preview on the right.')
  def on_rename(self):
    if not self.plans: QMessageBox.information(self,'Nothing to rename','Click Match first.'); return
    self.ensure_engine()
    if QMessageBox.question(self,'Confirm','Apply rename/move now?')!=QMessageBox.Yes: return
    try: self.engine.execute(self.plans); self.log.append('Rename complete.')
    except Exception: self.log.append(traceback.format_exc()); QMessageBox.critical(self,'Rename Error','See log.')

if __name__=='__main__':
  app=QApplication(sys.argv); w=App(); w.resize(1200,700); w.show(); sys.exit(app.exec())
