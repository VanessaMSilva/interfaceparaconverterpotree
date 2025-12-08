import sys
import subprocess
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QFileDialog,
    QVBoxLayout, QTabWidget, QTextEdit, QHBoxLayout, QMessageBox
)

CONFIG_FILE = "config.json"


class PotreeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor LAS/LAZ para Potree")
        self.resize(600, 400)

        # Tabs
        self.tabs = QTabWidget()
        self.tab_convert = QWidget()
        self.tab_config = QWidget()

        self.tabs.addTab(self.tab_convert, "Conversão")
        self.tabs.addTab(self.tab_config, "Propriedades")

        # Criar abas
        self.create_convert_tab()
        self.create_config_tab()

        # Terminal (logs)
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(QLabel("Terminal de execução:"))
        layout.addWidget(self.terminal)
        self.setLayout(layout)

        # Carregar configurações salvas
        self.config = self.load_config()
        self.input_lastools.setText(self.config.get("lastools", ""))
        self.input_potree.setText(self.config.get("potree", ""))
        self.input_output.setText(self.config.get("output_dir", ""))

    def create_convert_tab(self):
        layout = QVBoxLayout()

        # Arquivo LAS/LAZ
        hlayout_file = QHBoxLayout()
        self.label_file = QLabel("Arquivo LAS/LAZ:")
        self.add_info_icon(self.label_file, "Selecione o arquivo .las ou .laz que será convertido.")
        self.input_file = QLineEdit()
        self.btn_file = QPushButton("Procurar")
        self.btn_file.clicked.connect(self.select_file)
        hlayout_file.addWidget(self.label_file)
        hlayout_file.addWidget(self.input_file)
        hlayout_file.addWidget(self.btn_file)

        # Pasta de saída
        hlayout_folder = QHBoxLayout()
        self.label_folder = QLabel("Pasta de saída:")
        self.add_info_icon(self.label_folder, "Escolha onde os arquivos convertidos serão salvos.")
        self.input_output = QLineEdit()
        self.btn_folder = QPushButton("Procurar")
        self.btn_folder.clicked.connect(self.select_folder)
        hlayout_folder.addWidget(self.label_folder)
        hlayout_folder.addWidget(self.input_output)
        hlayout_folder.addWidget(self.btn_folder)

        # Nome do projeto
        hlayout_name = QHBoxLayout()
        self.label_name = QLabel("Nome do projeto:")
        self.add_info_icon(self.label_name, "Nome da página HTML gerada pelo Potree.")
        self.input_name = QLineEdit()
        hlayout_name.addWidget(self.label_name)
        hlayout_name.addWidget(self.input_name)

        # Botão converter
        self.btn_convert = QPushButton("Converter")
        self.btn_convert.clicked.connect(self.convert_file)

        layout.addLayout(hlayout_file)
        layout.addLayout(hlayout_folder)
        layout.addLayout(hlayout_name)
        layout.addWidget(self.btn_convert)

        self.tab_convert.setLayout(layout)

    def create_config_tab(self):
        layout = QVBoxLayout()

        # Caminho LAStools
        hlayout_lastools = QHBoxLayout()
        self.label_lastools = QLabel("LAStools.exe:")
        self.add_info_icon(self.label_lastools, "Selecione o caminho para o executável do LAStools (ex: las2las64.exe).")
        self.input_lastools = QLineEdit()
        self.btn_lastools = QPushButton("Procurar")
        self.btn_lastools.clicked.connect(self.select_lastools)
        hlayout_lastools.addWidget(self.label_lastools)
        hlayout_lastools.addWidget(self.input_lastools)
        hlayout_lastools.addWidget(self.btn_lastools)

        # Caminho Potree
        hlayout_potree = QHBoxLayout()
        self.label_potree = QLabel("PotreeConverter.exe:")
        self.add_info_icon(self.label_potree, "Selecione o caminho para o executável do PotreeConverter.")
        self.input_potree = QLineEdit()
        self.btn_potree = QPushButton("Procurar")
        self.btn_potree.clicked.connect(self.select_potree)
        hlayout_potree.addWidget(self.label_potree)
        hlayout_potree.addWidget(self.input_potree)
        hlayout_potree.addWidget(self.btn_potree)

        # Botão salvar configs
        self.btn_save = QPushButton("Salvar Configurações")
        self.btn_save.clicked.connect(self.save_config)

        layout.addLayout(hlayout_lastools)
        layout.addLayout(hlayout_potree)
        layout.addWidget(self.btn_save)

        self.tab_config.setLayout(layout)

    def add_info_icon(self, text, message):
        """Retorna um QWidget com label + botão de info"""
        label = QLabel(text)
        btn_info = QPushButton("!")
        btn_info.setFixedSize(20, 20)
        btn_info.clicked.connect(lambda: QMessageBox.information(self, "Ajuda", message))

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(btn_info)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        return container

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Selecionar LAS/LAZ", "", "LAS/LAZ Files (*.las *.laz)")
        if file:
            self.input_file.setText(file)

    def select_folder(self):
        dir = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        if dir:
            self.input_output.setText(dir)

    def select_lastools(self):
        file, _ = QFileDialog.getOpenFileName(self, "Selecionar LAStools", "", "Executável (*.exe)")
        if file:
            self.input_lastools.setText(file)

    def select_potree(self):
        file, _ = QFileDialog.getOpenFileName(self, "Selecionar PotreeConverter", "", "Executável (*.exe)")
        if file:
            self.input_potree.setText(file)

    def log(self, message):
        self.terminal.append(message)

    def convert_file(self):
        las_file = self.input_file.text()
        output_dir = self.input_output.text()
        project_name = self.input_name.text()
        las_tools = self.input_lastools.text()
        potree = self.input_potree.text()

        if not (las_file and output_dir and project_name and las_tools and potree):
            self.log("Erro: Preencha todos os campos e configure os executáveis!")
            return

        fixed_file = las_file.replace(".las", "_fixed.las").replace(".laz", "_fixed.las")

        try:
            self.log("Corrigindo arquivo LAS/LAZ...")
            subprocess.run([las_tools, "-i", las_file, "-o", fixed_file], check=True)

            self.log("Convertendo para Potree...")
            subprocess.run([potree, fixed_file, "-o", output_dir, "--generate-page", project_name], check=True)

            self.log(f"Conversão concluída! Página: {output_dir}\\{project_name}.html")
        except subprocess.CalledProcessError as e:
            self.log(f"Erro na execução: {e}")

    def save_config(self):
        self.config = {
            "lastools": self.input_lastools.text(),
            "potree": self.input_potree.text(),
            "output_dir": self.input_output.text()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)
        self.log("Configurações salvas com sucesso!")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PotreeApp()
    window.show()
    sys.exit(app.exec_())
