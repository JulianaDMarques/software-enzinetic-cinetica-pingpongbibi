import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QPushButton, QWidget,
    QLabel, QLineEdit, QMessageBox, QStackedWidget, QHBoxLayout, QGroupBox, QFrame, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon
import importlib.util
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas
)

# Importa as funções necessárias dos arquivos fornecidos
simulacao_path = "funcao_simulacao_2.py"
modelagem_path = "funcoes_modelagem_3.py"

spec_sim = importlib.util.spec_from_file_location("funcoes_simulacao", simulacao_path)
funcoes_simulacao = importlib.util.module_from_spec(spec_sim)
spec_sim.loader.exec_module(funcoes_simulacao)

spec_mod = importlib.util.spec_from_file_location("funcoes_modelagem", modelagem_path)
funcoes_modelagem = importlib.util.module_from_spec(spec_mod)
spec_mod.loader.exec_module(funcoes_modelagem)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modelagem e Simulação de Reações")
        self.setGeometry(300, 150, 700, 500)
        self.setWindowIcon(QIcon("imagem_unesp.png"))  # Define um ícone do aplicativo
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7f9fc;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QPushButton {
                background-color: #2E86C1;
                color: white;
                font-size: 14px;
                padding: 8px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1B4F72;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #bfc9ca;
                border-radius: 8px;
            }
            QGroupBox {
                border: 2px solid #5dade2;
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: #5dade2;
            }
        """)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.main_menu_ui()
        self.simulation_ui()
        self.modeling_ui()
        self.central_widget.setCurrentIndex(0)

    def main_menu_ui(self):
        """Tela inicial"""
        main_widget = QWidget()
        layout = QVBoxLayout()

        # Logo e título
        logo = QLabel()
        pixmap = QPixmap("imagem_unesp.png").scaled(150, 150, Qt.KeepAspectRatio)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)

        title = QLabel("Modelagem e Simulação de Reações")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2E4053;")

        button_frame = QFrame()
        button_layout = QVBoxLayout()

        simulation_button = QPushButton("Ir para Simulação")
        simulation_button.setIcon(QIcon.fromTheme("media-playback-start"))
        simulation_button.clicked.connect(lambda: self.central_widget.setCurrentIndex(1))

        modeling_button = QPushButton("Ir para Modelagem")
        modeling_button.setIcon(QIcon.fromTheme("document-open"))
        modeling_button.clicked.connect(lambda: self.central_widget.setCurrentIndex(2))

        button_layout.addWidget(simulation_button)
        button_layout.addWidget(modeling_button)
        button_layout.setSpacing(20)
        button_frame.setLayout(button_layout)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(button_frame)
        layout.addStretch()

        main_widget.setLayout(layout)
        self.central_widget.addWidget(main_widget)

    def simulation_ui(self):
        """Tela de Simulação"""
        sim_widget = QWidget()
        layout = QVBoxLayout()

        header = QLabel("Simulação de Reações")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)

        input_group = QGroupBox("Parâmetros")
        input_layout = QVBoxLayout()

        self.sim_input = QLineEdit()
        self.sim_input.setPlaceholderText("E0, Kcat_a, Kcat_b, s0_a, s0_b, t_input, k1, k_1, k2, k3, k_3, k4")
        input_layout.addWidget(self.sim_input)
        input_group.setLayout(input_layout)

        button_layout = QHBoxLayout()
        sim_button = QPushButton("Gerar Simulação")
        sim_button.clicked.connect(self.run_simulation)

        back_button = QPushButton("Voltar")
        back_button.clicked.connect(lambda: self.central_widget.setCurrentIndex(0))

        button_layout.addWidget(sim_button)
        button_layout.addWidget(back_button)

        layout.addWidget(header)
        layout.addWidget(input_group)
        layout.addLayout(button_layout)
        sim_widget.setLayout(layout)
        self.central_widget.addWidget(sim_widget)

    def modeling_ui(self):
        """Tela de Modelagem"""
        model_widget = QWidget()
        layout = QVBoxLayout()

        # Título
        header = QLabel("Modelagem de Reações")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #00B0FF;")

        # Seção de entrada de dados
        input_layout = QHBoxLayout()
        input_group = QGroupBox("Entrada de Dados")
        input_inner_layout = QVBoxLayout()

        self.file_label = QLabel("Nenhum arquivo selecionado.")
        file_button = QPushButton("Selecionar Arquivo Excel")
        file_button.clicked.connect(self.load_file)
        self.e0_input = QLineEdit()
        self.e0_input.setPlaceholderText("Digite o valor de E0 (mol/L)")

        run_button = QPushButton("Gerar Modelagem")
        run_button.clicked.connect(self.run_modeling)

        input_inner_layout.addWidget(self.file_label)
        input_inner_layout.addWidget(file_button)
        input_inner_layout.addWidget(self.e0_input)
        input_inner_layout.addWidget(run_button)
        input_group.setLayout(input_inner_layout)

        # Saída de K's
        output_group = QGroupBox("Parâmetros Cinéticos")
        output_inner_layout = QVBoxLayout()
        self.parametros_output = QTextEdit()
        self.parametros_output.setReadOnly(True)
        self.parametros_output.setPlaceholderText("Os parâmetros cinéticos aparecerão aqui...")
        output_inner_layout.addWidget(self.parametros_output)
        output_group.setLayout(output_inner_layout)

        input_layout.addWidget(input_group, 50)
        input_layout.addWidget(output_group, 50)

        # Gráfico
        graph_group = QGroupBox("Resultados Gráficos")
        graph_inner_layout = QVBoxLayout()
        self.figure_canvas = FigureCanvas(plt.figure())
        graph_inner_layout.addWidget(self.figure_canvas)
        graph_group.setLayout(graph_inner_layout)

        layout.addWidget(header)
        layout.addLayout(input_layout)
        layout.addWidget(graph_group)

        model_widget.setLayout(layout)
        self.central_widget.addWidget(model_widget)


    def run_simulation(self):
        try:
            params = [float(x) for x in self.sim_input.text().split(",")]
            if len(params) != 12:
                raise ValueError("Forneça 12 parâmetros separados por vírgulas.")
            funcoes_simulacao.plot_sim(*params)
        except Exception as e:
            QMessageBox.critical(self, "Erro na Simulação", f"Erro: {str(e)}")

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Selecione o arquivo Excel", "", "Excel Files (*.xlsx; *.xls)", options=options
        )
        if file_name:
            self.file_label.setText(f"Arquivo: {os.path.basename(file_name)}")
            self.excel_file = file_name

    def run_modeling(self):
        try:
            if not hasattr(self, 'excel_file'):
                raise FileNotFoundError("Selecione um arquivo Excel primeiro.")
            E0 = float(self.e0_input.text())

            # Obter parâmetros e função de plotagem
            params, plot_function = funcoes_modelagem.funcao_final(self.excel_file, E0)
            k1, k2, k3, k4, Km_A, Km_B, Vmax = params

            # Exibir os parâmetros cinéticos
            self.parametros_output.setText(
                f"k1: {k1:.4f}\nk2: {k2:.4f}\nk3: {k3:.4f}\nk4: {k4:.4f}\n"
                f"Km_A: {Km_A:.4f}\nKm_B: {Km_B:.4f}\nVmax: {Vmax:.4f}"
            )

            # Atualizar o gráfico na mesma figura
            self.figure_canvas.figure.clear()  # Limpa a figura existente
            ax = self.figure_canvas.figure.add_subplot(111)  # Cria um único eixo na figura
            plot_function(ax)  # Passa o eixo para a função de plotagem
            self.figure_canvas.draw()  # Redesenha o gráfico na tela

        except Exception as e:
            QMessageBox.critical(self, "Erro na Modelagem", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
