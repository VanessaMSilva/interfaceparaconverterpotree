import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QFileDialog, QVBoxLayout

class PotreeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor LAS para Potree")
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.label_file = QLabel("Selecione um arquivo LAS:")
        self.input_file = QLineEdit()

        
        self.btn_file = QPushButton("Procurar")
        self.btn_file.clicked.connect(self.select_file)

        self.label_folder = QLabel("Selecione uma pasta:")
        self.input_folder = QLineEdit()

        self.btn_folder = QPushButton("Procurar")
        self.btn_folder.clicked.connect(self.select_folder)

        self.label_name = QLabel("Nome do projeto:")
        self.input_name = QLineEdit()

        self.btn_convert = QPushButton("Converter")
        self.btn_convert.clicked.connect(self.convert_file)

        layout.addWidget(self.label_file)
        layout.addWidget(self.input_file)
        layout.addWidget(self.btn_file)

        layout.addWidget(self.label_folder)
        layout.addWidget(self.input_folder)
        layout.addWidget(self.btn_folder)

        layout.addWidget(self.label_name)
        layout.addWidget(self.input_name)
        layout.addWidget(self.btn_convert)

        self.setLayout(layout)

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Selecionar LAS", "", "LAS Files (*.las)")
        if file:
            self.input_file.setText(file)

    def select_folder(self):
        dir = QFileDialog.getExistingDirectory(self, "Selecione uma pasta")

        if dir:
            self.input_folder.setText(dir)

    def convert_file(self):
        las_file = self.input_file.text()
        folder_name = self.input_folder.text()
        project_name = self.input_name.text()
        fixed_file = las_file.replace(".las", "_fixed.las")

        # Caminhos (ajustar conforme instalação)
        las_tools = r"C:\LAStools\LAStools\bin\las2las64.exe"
        potree = r"C:\xampp\htdocs\PotreeConverter_2.1.1_x64_windows\PotreeConverter_windows_x64\PotreeConverter.exe"
    
        output_dir = folder_name

        # Etapa 1: corrigir bounding box
        subprocess.run([las_tools, "-i", las_file, "-o", fixed_file])

        # Etapa 2: converter com potree
        subprocess.run([potree, fixed_file, "-o", output_dir, "--generate-page", project_name])

        print(f"Conversão concluída! Página: {output_dir}\\{project_name}.html")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PotreeApp()
    window.show()
    sys.exit(app.exec_())
