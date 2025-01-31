import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QPushButton, QWidget, QCheckBox,
    QLabel, QLineEdit, QMessageBox, QStackedWidget, QHBoxLayout, QGroupBox, QFrame, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
import importlib.util
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas
)

# Importa as funções necessárias dos arquivos fornecidos
simulacao_path = "funcao_simulacao_final.py"
modelagem_path = "funcoes_modelagem_final.py"

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

        input_group = QGroupBox("Parâmetros da Simulação")
        input_layout = QVBoxLayout()

        self.inputs = {}
        parametros = [
            ("E0", "Concentração Inicial da Enzima (mol/L)", "0.01"),
            ("Kcat_a", "Kcat do Substrato A", "100"),
            ("Kcat_b", "Kcat do Substrato B", "100"),
            ("s0_a", "Concentração Inicial Substrato A (mol/L)", "0.1"),
            ("s0_b", "Concentração Inicial Substrato B (mol/L)", "0.1"),
            ("t_input", "Tempo de Simulação (min)", "60"),
            ("k1", "Constante k1", "1.0"),
            ("k_1", "Constante k_1", "0"),
            ("k2", "Constante k2", "1.0"),
            ("k3", "Constante k3", "1.0"),
            ("k_3", "Constante k_3", "0"),
            ("k4", "Constante k4", "1.0")
        ]

        for key, label, default in parametros:
            row = QHBoxLayout()
            lbl = QLabel(label)
            input_field = QLineEdit()
            input_field.setText(default)
            self.inputs[key] = input_field
            row.addWidget(lbl)
            row.addWidget(input_field)
            input_layout.addLayout(row)

        input_group.setLayout(input_layout)
        layout.addWidget(header)
        layout.addWidget(input_group)

        button_layout = QHBoxLayout()
        sim_button = QPushButton("Gerar Simulação")
        sim_button.clicked.connect(self.run_simulation)
        back_button = QPushButton("Voltar")
        back_button.clicked.connect(lambda: self.central_widget.setCurrentIndex(0))
        button_layout.addWidget(sim_button)
        button_layout.addWidget(back_button)

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

        # Passo 1: Inserir dados do Excel
        file_group = QGroupBox("1. Inserir Dados do Arquivo Excel")
        file_layout = QVBoxLayout()
        self.file_label = QLabel("Nenhum arquivo selecionado.")
        file_button = QPushButton("Selecionar Arquivo Excel")
        file_button.clicked.connect(self.load_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(file_button)
        file_group.setLayout(file_layout)

        # Passo 2: Inserir Enzima e Substratos Iniciais
        conc_group = QGroupBox("2. Inserir Enzima e Substratos Iniciais")
        conc_layout = QVBoxLayout()
        self.e0_input = QLineEdit()
        self.e0_input.setPlaceholderText("Concentração Inicial da Enzima (mol/L)")
        self.s0_a_input = QLineEdit()
        self.s0_a_input.setPlaceholderText("Concentração Inicial Substrato A (mol/L)")
        self.s0_b_input = QLineEdit()
        self.s0_b_input.setPlaceholderText("Concentração Inicial Substrato B (mol/L)")
        conc_layout.addWidget(self.e0_input)
        conc_layout.addWidget(self.s0_a_input)
        conc_layout.addWidget(self.s0_b_input)
        conc_group.setLayout(conc_layout)

        # Passo 3: Inserir Parâmetros da Função
        param_group = QGroupBox("3. Inserir Parâmetros da Função")
        param_layout = QVBoxLayout()
        self.maxiter_input = QLineEdit()
        self.maxiter_input.setPlaceholderText("maxiter (padrão: 1000)")
        self.popsize_input = QLineEdit()
        self.popsize_input.setPlaceholderText("popsize (padrão: 15)")
        self.mutation_input = QLineEdit()
        self.mutation_input.setPlaceholderText("mutation (padrão: (0.5,1))")
        self.recombination_input = QLineEdit()
        self.recombination_input.setPlaceholderText("recombination (padrão: 0.7)")
        param_layout.addWidget(self.maxiter_input)
        param_layout.addWidget(self.popsize_input)
        param_layout.addWidget(self.mutation_input)
        param_layout.addWidget(self.recombination_input)
        param_group.setLayout(param_layout)

        # Passo 4: Ajustes Disponíveis (Checkboxes)
        check_group = QGroupBox("4. Ajustes Disponíveis")
        check_layout = QVBoxLayout()
        self.checkboxes = {}
        for param in ["S1_adjust", "S2_adjust", "P1_adjust", "P2_adjust"]:
            self.checkboxes[param] = QCheckBox(param)
            check_layout.addWidget(self.checkboxes[param])
        check_group.setLayout(check_layout)
       

         # Botão para rodar modelagem
        run_button = QPushButton("Gerar Modelagem")
        run_button.clicked.connect(self.run_modeling)

        # Layout Principal
        layout.addWidget(header)
        layout.addWidget(file_group)
        layout.addWidget(conc_group)
        layout.addWidget(param_group)
        layout.addWidget(check_group)
        layout.addWidget(run_button)

        # Saída de K's
        output_group = QGroupBox("Parâmetros Cinéticos")
        output_inner_layout = QVBoxLayout()
        self.parametros_output = QTextEdit()
        self.parametros_output.setReadOnly(True)
        self.parametros_output.setPlaceholderText("Os parâmetros cinéticos aparecerão aqui...")
        output_inner_layout.addWidget(self.parametros_output)
        output_group.setLayout(output_inner_layout)
        layout.addWidget(output_group)
       
    #     # Gráfico
    #     # graph_group = QGroupBox("Resultados Gráficos")
    #     # graph_inner_layout = QVBoxLayout()
    #     # self.figure_canvas = FigureCanvas(plt.figure())
    #     # graph_inner_layout.addWidget(self.figure_canvas)
    #     # graph_group.setLayout(graph_inner_layout)

        self.graph_group = QGroupBox("Resultados Gráficos")
        self.graph_layout = QVBoxLayout()
        self.figure_canvas = FigureCanvas()
        self.graph_layout.addWidget(self.figure_canvas)
        self.graph_group.setLayout(self.graph_layout)

        model_widget.setLayout(layout)
        self.central_widget.addWidget(model_widget)


    def run_simulation(self):
        try:
            params = [float(self.inputs[key].text()) for key in self.inputs]
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
            s0_a = float(self.s0_a_input.text())
            s0_b = float(self.s0_b_input.text())

            maxiter = int(self.maxiter_input.text()) if self.maxiter_input.text() else 1000
            popsize = int(self.popsize_input.text()) if self.popsize_input.text() else 15
            mutation = tuple(map(float, self.mutation_input.text().split(','))) if self.mutation_input.text() else (0.5, 1)
            recombination = float(self.recombination_input.text()) if self.recombination_input.text() else 0.7

            adjustments = {param: self.checkboxes[param].isChecked() for param in self.checkboxes}

            # Obter parâmetros e função de plotagem
            params, plot_function = funcoes_modelagem.funcao_final(self.excel_file, E0, s0_a, s0_b, adjustments, maxiter=maxiter, popsize=popsize, mutation=mutation, recombination=recombination)
            k1, k_1, k2, k3, k_3, k4, Km_A, Km_B, Vmax = params

            # Exibir os parâmetros cinéticos
            self.parametros_output.setText(
                f"k1: {k1:.4f}\nk_1: {k_1:.4f}\nk2: {k2:.4f}\nk3: {k3:.4f}\nk_3: {k_3:.4f}\nk4: {k4:.4f}\n"
                f"Km_A: {Km_A:.4f}\nKm_B: {Km_B:.4f}\nVmax: {Vmax:.4f}"
            )

            #self.figure_canvas(plot_function)
            # Atualizar o gráfico na mesma figura
            self.figure_canvas.figure.clear()  # Limpa a figura existente
            ax = self.figure_canvas.figure.add_subplot(111)  # Cria um único eixo na figura
            plot_function(ax)  # Passa o eixo para a função de plotagem
            self.figure_canvas.draw()  # Redesenha o gráfico na tela

        except Exception as e:
            QMessageBox.critical(self, "Erro na Modelagem", str(e))

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Selecione o arquivo Excel", "", "Excel Files (*.xlsx; *.xls)", options=options
        )
        if file_name:
            self.file_label.setText(f"Arquivo: {os.path.basename(file_name)}")
            self.excel_file = file_name

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
