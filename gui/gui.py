"""
An interface for the option pricer
May contain modules for:
- Input fields
- Button clicks
- Results display

May use PyQt5 or Tkinter for GUI
"""
#下载PyQt5

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from options.european_option import EuropeanOption
from options.american_option import AmericanOption
from pricer.implied_volatility_calculator import ImpliedVolatility
from options.asian_option import ArithmeticAsianOption,GeometricAsianOption
from options.kiko_option import KIKOOption
from options.basket_option import ArithmeticBasketOption,GeometricBasketOption
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QGridLayout,
    QFormLayout, QMessageBox,QLineEdit,QComboBox
)

from PyQt5.QtCore import Qt


# -------- 子页面基类 --------
class BasePage(QWidget):
    def __init__(self, title, return_callback):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(500, 400)
        self.return_callback = return_callback
        self.initUI(title)

    def initUI(self, title_text):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        label = QLabel(f"📘 当前页面：{title_text}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold; color: #34495e;")
        layout.addWidget(label)

        desc = QLabel(f"这里是 {title_text} 的功能区域，可以放置表单、图表、输入框等。")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("font-size: 16px; color: #555;")
        layout.addWidget(desc)

        return_btn = QPushButton("← 返回主页面")
        return_btn.setFixedSize(160, 40)
        return_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        return_btn.clicked.connect(self.return_callback)
        layout.addWidget(return_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)



# -------- 主页面 --------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Home")
        self.resize(500, 450)

        self.page_titles = [
            "European option", "Geometric Asian", "Geometric Basket", "Arithmetic Asian",
            "Arithmetic Basket", "KIKO", "American option", "Implied Volatility"
        ]
        self.pages = {}
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        title = QLabel("🌟 Option-Pricer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin: 30px;
        """)
        main_layout.addWidget(title)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        for index, name in enumerate(self.page_titles):
            button = QPushButton(name)
            button.setObjectName(f"btn_{index+1}")
            button.setFixedSize(180, 40)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 8px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            button.clicked.connect(lambda _, n=name: self.open_page(n))
            row = index // 2
            col = index % 2
            grid_layout.addWidget(button, row, col)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

        self.pages["European option"] = EuropeanOptionPage(self.return_to_main)
        self.pages["American option"] = AmericanOptionPage(self.return_to_main)
        self.pages["Implied Volatility"] = ImpliedVolatilityPage(self.return_to_main)
        self.pages["Arithmetic Asian"] = ArithmeticAsianPage(self.return_to_main)
        self.pages["Geometric Asian"] = GeometricAsianPage(self.return_to_main)
        self.pages["KIKO"] = KIKOPage(self.return_to_main)
        self.pages["Geometric Basket"] = GeometricBasketOptionPage(self.return_to_main)
        self.pages["Arithmetic Basket"] = ArithmeticBasketOptionPage(self.return_to_main)


        # 创建所有子页面
        #for name in self.page_titles:
        #    self.pages[name] = BasePage(name, self.return_to_main)

    def open_page(self, name):
        self.hide()
        self.pages[name].show()

    def return_to_main(self):
        sender = self.sender().parent()
        sender.hide()
        self.show()

#European页面
class EuropeanOptionPage(QWidget):
    def __init__(self, return_callback):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("European Option")
        self.resize(500, 550)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("🧮 European Option Pricer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.inputs = {}

        # 输入字段标签加粗
        fields = {
            "spot price": "S0",
            "strike price": "K",
            "maturity (yr)": "T",
            "risk free rate": "r",
            "repo rate": "q",
            "volatility": "sigma"
        }

        for label, key in fields.items():
            edit = QLineEdit()
            edit.setPlaceholderText(f"Enter {label}")
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; font-size: 15px;")
            form_layout.addRow(label_widget, edit)
            self.inputs[key] = edit

        # Option type selector
        self.option_type_box = QComboBox()
        self.option_type_box.addItems(["call", "put"])
        option_label = QLabel("Option Type:")
        option_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        form_layout.addRow(option_label, self.option_type_box)

        layout.addLayout(form_layout)

        # 计算按钮
        calc_btn = QPushButton("Calculate Price")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        calc_btn.clicked.connect(self.calculate_price)
        layout.addWidget(calc_btn, alignment=Qt.AlignCenter)

        # 清空按钮
        clear_btn = QPushButton("Clear Inputs")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #ca6f1e;
            }
        """)
        clear_btn.clicked.connect(self.clear_inputs)
        layout.addWidget(clear_btn, alignment=Qt.AlignCenter)

        # 输出部分
        output_label = QLabel("Option Price:")
        output_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(output_label)

        self.result_output = QLineEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.result_output)

        # 返回按钮
        return_btn = QPushButton("← Back")
        return_btn.clicked.connect(self.return_callback)
        layout.addWidget(return_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def calculate_price(self):
        try:
            S0 = float(self.inputs["S0"].text())
            K = float(self.inputs["K"].text())
            T = float(self.inputs["T"].text())
            r = float(self.inputs["r"].text())
            q = float(self.inputs["q"].text())
            sigma = float(self.inputs["sigma"].text())
            option_type = self.option_type_box.currentText()
            option_european = EuropeanOption(S0, r, T, K, q, sigma, option_type)
            price = option_european.price()
            self.result_output.setText(f"{price:.4f}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"输入参数无效，请检查并重试。\n\n详细信息：{e}")

    def clear_inputs(self):
        for edit in self.inputs.values():
            edit.clear()
        self.result_output.clear()



#American
class AmericanOptionPage(QWidget):
    def __init__(self, return_callback):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("American Option")
        self.resize(500, 550)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("🧮 American Option Pricer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.inputs = {}

        # 输入字段标签加粗
        fields = {
            "spot price": "S0",
            "strike price": "K",
            "maturity (yr)": "T",
            "risk free rate": "r",
            "num_steps": "N",
            "volatility": "sigma"
        }

        for label, key in fields.items():
            edit = QLineEdit()
            edit.setPlaceholderText(f"Enter {label}")
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; font-size: 15px;")
            form_layout.addRow(label_widget, edit)
            self.inputs[key] = edit

        # Option type selector
        self.option_type_box = QComboBox()
        self.option_type_box.addItems(["call", "put"])
        option_label = QLabel("Option Type:")
        option_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        form_layout.addRow(option_label, self.option_type_box)

        layout.addLayout(form_layout)

        # 计算按钮
        calc_btn = QPushButton("Calculate Price")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        calc_btn.clicked.connect(self.calculate_price)
        layout.addWidget(calc_btn, alignment=Qt.AlignCenter)

        # 清空按钮
        clear_btn = QPushButton("Clear Inputs")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #ca6f1e;
            }
        """)
        clear_btn.clicked.connect(self.clear_inputs)
        layout.addWidget(clear_btn, alignment=Qt.AlignCenter)

        # 输出部分
        output_label = QLabel("Option Price:")
        output_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(output_label)

        self.result_output = QLineEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.result_output)

        # 返回按钮
        return_btn = QPushButton("← Back")
        return_btn.clicked.connect(self.return_callback)
        layout.addWidget(return_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def calculate_price(self):
        try:
            S0 = float(self.inputs["S0"].text())
            K = float(self.inputs["K"].text())
            T = float(self.inputs["T"].text())
            r = float(self.inputs["r"].text())
            N= int(self.inputs["N"].text())
            sigma = float(self.inputs["sigma"].text())
            option_type = self.option_type_box.currentText()
            option_american = AmericanOption(S0, r, T, K, sigma, N, option_type)
            price = option_american.price()
            self.result_output.setText(f"{price:.4f}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"输入参数无效，请检查并重试。\n\n详细信息：{e}")

    def clear_inputs(self):
        for edit in self.inputs.values():
            edit.clear()
        self.result_output.clear()

#ImpliedVolatility
class ImpliedVolatilityPage(QWidget):
    def __init__(self, return_callback):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Implied Volatility")
        self.resize(500, 550)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("🧮 Implied Volatility Calculator")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.inputs = {}

        # 使用统一的 key 命名，便于计算函数中引用
        fields = {
            "spot price": "S0",
            "strike price": "K",
            "maturity (yr)": "T",
            "risk free rate": "r",
            "repo rate": "q",
            "option premium": "option_premium"
        }

        for label, key in fields.items():
            edit = QLineEdit()
            edit.setPlaceholderText(f"Enter {label}")
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; font-size: 15px;")
            form_layout.addRow(label_widget, edit)
            self.inputs[key] = edit

        self.option_type_box = QComboBox()
        self.option_type_box.addItems(["call", "put"])
        option_label = QLabel("Option Type:")
        option_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        form_layout.addRow(option_label, self.option_type_box)

        layout.addLayout(form_layout)

        # 计算按钮
        calc_btn = QPushButton("Calculate IV")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        calc_btn.clicked.connect(self.calculate_price)
        layout.addWidget(calc_btn, alignment=Qt.AlignCenter)

        # 清空按钮
        clear_btn = QPushButton("Clear Inputs")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #ca6f1e;
            }
        """)
        clear_btn.clicked.connect(self.clear_inputs)
        layout.addWidget(clear_btn, alignment=Qt.AlignCenter)

        # 输出区域
        output_label = QLabel("Implied Volatility:")
        output_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(output_label)

        self.result_output = QLineEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.result_output)

        # 返回按钮
        return_btn = QPushButton("← Back")
        return_btn.clicked.connect(self.return_callback)
        layout.addWidget(return_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def calculate_price(self):
        try:
            # 转换为 float 的字段
            required_fields = ["S0", "K", "T", "r", "q", "option_premium"]
            values = {}
            for key in required_fields:
                text = self.inputs[key].text()
                if not text.strip():
                    raise ValueError(f"'{key}' 不能为空")
                values[key] = float(text)

            option_type = self.option_type_box.currentText()
            iv_calculator = ImpliedVolatility()
            # 调用 IV 计算
            iv = iv_calculator.calculate(
                option_type,
                values["S0"], values["r"], values["q"],
                values["T"], values["K"], values["option_premium"]
            )
            self.result_output.setText(f"{iv:.4f}")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"输入参数无效，请检查并重试。\n\n详细信息：{e}")

    def clear_inputs(self):
        for edit in self.inputs.values():
            edit.clear()
        self.result_output.clear()


#ArithmeticAsian
class ArithmeticAsianPage(QWidget):
    def __init__(self, return_callback):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Arithmetic Asian Option")
        self.resize(500, 550)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("🧮 Arithmetic Asian Option Pricer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.inputs = {}

        # 输入字段标签加粗
        fields = {
            "spot price": "S0",
            "strike price": "K",
            "maturity (yr)": "T",
            "risk free rate": "r",
            "volatility": "sigma",
            "num_observations": "No",
            "num_paths": "Np"
        }

        for label, key in fields.items():
            edit = QLineEdit()
            edit.setPlaceholderText(f"Enter {label}")
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; font-size: 15px;")
            form_layout.addRow(label_widget, edit)
            self.inputs[key] = edit

        # Option type selector
        self.option_type_box = QComboBox()
        self.option_type_box.addItems(["call", "put"])
        option_label = QLabel("Option Type:")
        option_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        form_layout.addRow(option_label, self.option_type_box)
        # Control Variate selector
        self.cv_box = QComboBox()
        self.cv_box.addItems(["True", "False"])
        cv_label = QLabel("Use Control Variate:")
        cv_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        form_layout.addRow(cv_label, self.cv_box)
        layout.addLayout(form_layout)

        # 计算按钮
        calc_btn = QPushButton("Calculate Price")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        calc_btn.clicked.connect(self.calculate_price)
        layout.addWidget(calc_btn, alignment=Qt.AlignCenter)

        # 清空按钮
        clear_btn = QPushButton("Clear Inputs")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #ca6f1e;
            }
        """)
        clear_btn.clicked.connect(self.clear_inputs)
        layout.addWidget(clear_btn, alignment=Qt.AlignCenter)

        # 输出部分
        output_label = QLabel("Option Price:")
        output_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(output_label)

        self.result_output = QLineEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.result_output)

        
        extra_label = QLabel("95% Confidence Interval:")
        extra_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(extra_label)

        self.std_output = QLineEdit()
        self.std_output.setReadOnly(True)
        self.std_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.std_output)

        # 返回按钮
        return_btn = QPushButton("← Back")
        return_btn.clicked.connect(self.return_callback)
        layout.addWidget(return_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def calculate_price(self):
        try:
            S0 = float(self.inputs["S0"].text())
            K = float(self.inputs["K"].text())
            T = float(self.inputs["T"].text())
            r = float(self.inputs["r"].text())
            No= int(self.inputs["No"].text())
            Np= int(self.inputs["Np"].text())
            sigma = float(self.inputs["sigma"].text())
            option_type = self.option_type_box.currentText()
            cv_box = self.cv_box.currentText()
            option_european = ArithmeticAsianOption(S0, r, T, K, sigma,No,Np,cv_box, option_type)
            price ,conf_interval= option_european.price()
            self.result_output.setText(f"{price:.4f}")
            self.std_output.setText(f"{conf_interval}") 
        except Exception as e:
            QMessageBox.warning(self, "错误", f"输入参数无效，请检查并重试。\n\n详细信息：{e}")

    def clear_inputs(self):
        for edit in self.inputs.values():
            edit.clear()
        self.result_output.clear()
        self.std_output.clear()

#GeometricAsian
class GeometricAsianPage(QWidget):
    def __init__(self, return_callback):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Geometric Asian Option")
        self.resize(500, 550)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("🧮 Geometric Asian Option Pricer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.inputs = {}

        # 输入字段标签加粗
        fields = {
            "spot price": "S0",
            "strike price": "K",
            "maturity (yr)": "T",
            "risk free rate": "r",
            "volatility": "sigma",
            "num_observations": "No"
        }

        for label, key in fields.items():
            edit = QLineEdit()
            edit.setPlaceholderText(f"Enter {label}")
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; font-size: 15px;")
            form_layout.addRow(label_widget, edit)
            self.inputs[key] = edit

        # Option type selector
        self.option_type_box = QComboBox()
        self.option_type_box.addItems(["call", "put"])
        option_label = QLabel("Option Type:")
        option_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        form_layout.addRow(option_label, self.option_type_box)

        layout.addLayout(form_layout)

        # 计算按钮
        calc_btn = QPushButton("Calculate Price")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        calc_btn.clicked.connect(self.calculate_price)
        layout.addWidget(calc_btn, alignment=Qt.AlignCenter)

        # 清空按钮
        clear_btn = QPushButton("Clear Inputs")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #ca6f1e;
            }
        """)
        clear_btn.clicked.connect(self.clear_inputs)
        layout.addWidget(clear_btn, alignment=Qt.AlignCenter)

        # 输出部分
        output_label = QLabel("Option Price:")
        output_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(output_label)

        self.result_output = QLineEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.result_output)

        # 返回按钮
        return_btn = QPushButton("← Back")
        return_btn.clicked.connect(self.return_callback)
        layout.addWidget(return_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def calculate_price(self):
        try:
            S0 = float(self.inputs["S0"].text())
            K = float(self.inputs["K"].text())
            T = float(self.inputs["T"].text())
            r = float(self.inputs["r"].text())
            No= int(self.inputs["No"].text())
            sigma = float(self.inputs["sigma"].text())
            option_type = self.option_type_box.currentText()

            option_european = GeometricAsianOption(S0, r, T, K, sigma,No, option_type)
            price = option_european.price()
            self.result_output.setText(f"{price:.4f}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"输入参数无效，请检查并重试。\n\n详细信息：{e}")

    def clear_inputs(self):
        for edit in self.inputs.values():
            edit.clear()
        self.result_output.clear()
        

 #KIKOPage

class KIKOPage(QWidget):
    def __init__(self, return_callback):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("KIKO Option")
        self.resize(500, 550)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("🧮 KIKO Option Pricer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.inputs = {}

        # 输入字段标签加粗
        fields = {
            "spot price": "S0",
            "strike price": "K",
            "maturity (yr)": "T",
            "risk free rate": "r",
            "volatility": "sigma",
            "num_observations": "No",
            "lower_barrier":"lb",
            "upper_barrier":"ub",
            "rebate":"re"
        }

        for label, key in fields.items():
            edit = QLineEdit()
            edit.setPlaceholderText(f"Enter {label}")
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; font-size: 15px;")
            form_layout.addRow(label_widget, edit)
            self.inputs[key] = edit


        layout.addLayout(form_layout)

        # 计算按钮
        calc_btn = QPushButton("Calculate Price")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        calc_btn.clicked.connect(self.calculate_price)
        layout.addWidget(calc_btn, alignment=Qt.AlignCenter)

        # 清空按钮
        clear_btn = QPushButton("Clear Inputs")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #ca6f1e;
            }
        """)
        clear_btn.clicked.connect(self.clear_inputs)
        layout.addWidget(clear_btn, alignment=Qt.AlignCenter)

        # 输出部分
        output_label = QLabel("Option Price:")
        output_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(output_label)

        self.result_output = QLineEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.result_output)

        
        extra_label = QLabel("95% Confidence Interval:")
        extra_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(extra_label)

        self.std_output = QLineEdit()
        self.std_output.setReadOnly(True)
        self.std_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.std_output)

        
        delta_label = QLabel("delta:")
        delta_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(delta_label)

        self.delta_output = QLineEdit()
        self.delta_output.setReadOnly(True)
        self.delta_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.delta_output)


        # 返回按钮
        return_btn = QPushButton("← Back")
        return_btn.clicked.connect(self.return_callback)
        layout.addWidget(return_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def calculate_price(self):
        try:
            S0 = float(self.inputs["S0"].text())
            K = float(self.inputs["K"].text())
            T = float(self.inputs["T"].text())
            r = float(self.inputs["r"].text())
            No= int(self.inputs["No"].text())
            lb = float(self.inputs["lb"].text())         
            ub = float(self.inputs["ub"].text())
            rebate= float(self.inputs["re"].text())
            sigma = float(self.inputs["sigma"].text())

            option_kiko = KIKOOption(S0, r, T, K, sigma,lb,ub, No,rebate)
            price ,low,high= option_kiko.price()
            delta = option_kiko.calculate_delta()
            self.result_output.setText(f"{price:.4f}")
            self.std_output.setText(f"{low:.4f}, {high:.4f}") 
            self.delta_output.setText(f"{delta:.4f}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"输入参数无效，请检查并重试。\n\n详细信息：{e}")

    def clear_inputs(self):
        for edit in self.inputs.values():
            edit.clear()
        self.result_output.clear()
        self.std_output.clear()
        self.delta_output.clear()


class GeometricBasketOptionPage(QWidget):
    def __init__(self, return_callback):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Geometric Basket Option")
        self.resize(500, 550)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("🧮 Geometric Basket Option Pricer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.inputs = {}

        # 输入字段标签加粗
        fields = {
            "spot prices": "S0",
            "strike price": "K",
            "maturity (yr)": "T",
            "risk free rate": "r",
            "volatilities": "sigma",
            "correlation": "cor"
        }
        hint_label = QLabel("💡 Use comma to separate multiple values in spot prices and volatilities(e.g. 100, 105)")
        hint_label.setStyleSheet("color: gray; font-size: 13px;")
        form_layout.addRow(hint_label)
        for label, key in fields.items():
            edit = QLineEdit()
            edit.setPlaceholderText(f"Enter {label}")
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; font-size: 15px;")
            form_layout.addRow(label_widget, edit)
            self.inputs[key] = edit

        # Option type selector
        self.option_type_box = QComboBox()
        self.option_type_box.addItems(["call", "put"])
        option_label = QLabel("Option Type:")
        option_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        form_layout.addRow(option_label, self.option_type_box)

        layout.addLayout(form_layout)

        # 计算按钮
        calc_btn = QPushButton("Calculate Price")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        calc_btn.clicked.connect(self.calculate_price)
        layout.addWidget(calc_btn, alignment=Qt.AlignCenter)

        # 清空按钮
        clear_btn = QPushButton("Clear Inputs")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #ca6f1e;
            }
        """)
        clear_btn.clicked.connect(self.clear_inputs)
        layout.addWidget(clear_btn, alignment=Qt.AlignCenter)

        # 输出部分
        output_label = QLabel("Option Price:")
        output_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(output_label)

        self.result_output = QLineEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.result_output)

        # 返回按钮
        return_btn = QPushButton("← Back")
        return_btn.clicked.connect(self.return_callback)
        layout.addWidget(return_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def calculate_price(self):
        try:
            S0_str = self.inputs["S0"].text()
            sigma_str = self.inputs["sigma"].text()

            S0 = [float(s.strip()) for s in S0_str.split(",") if s.strip()]
            sigma = [float(s.strip()) for s in sigma_str.split(",") if s.strip()]

            if len(S0) != len(sigma):
                raise ValueError("Spot price 和 Volatility 的数量必须相同。")

            K = float(self.inputs["K"].text())
            T = float(self.inputs["T"].text())
            r = float(self.inputs["r"].text())
            cor = float(self.inputs["cor"].text())
            option_type = self.option_type_box.currentText()

            # 假设你有 GeometricBasketOption 类接收 S0, sigma 为数组
            option = GeometricBasketOption(S0, r, T, K, sigma,cor, option_type)
            price = option.price()
            self.result_output.setText(f"{price:.4f}")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"输入参数无效，请检查并重试。\n\n详细信息：{e}")


    def clear_inputs(self):
        for edit in self.inputs.values():
            edit.clear()
        self.result_output.clear()

#ArithmeticBasket
class ArithmeticBasketOptionPage(QWidget):
    def __init__(self, return_callback):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Arithmetic Basket Option")
        self.resize(500, 550)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("🧮 Arithmetic Basket Option Pricer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.inputs = {}

        # 输入字段标签加粗
        fields = {
            "spot price 1": "S0_1",
            "spot price 2": "S0_2",
            "strike price": "K",
            "maturity (yr)": "T",
            "risk free rate": "r",
            "volatility 1": "sigma_1",
            "volatility 2": "sigma_2",
            "correlation": "cor",
            "num_paths":"N"
        }

        for label, key in fields.items():
            edit = QLineEdit()
            edit.setPlaceholderText(f"Enter {label}")
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; font-size: 15px;")
            form_layout.addRow(label_widget, edit)
            self.inputs[key] = edit

        # Option type selector
        self.option_type_box = QComboBox()
        self.option_type_box.addItems(["call", "put"])
        option_label = QLabel("Option Type:")
        option_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        form_layout.addRow(option_label, self.option_type_box)
       
        layout.addLayout(form_layout)

        # 计算按钮
        calc_btn = QPushButton("Calculate Price")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        calc_btn.clicked.connect(self.calculate_price)
        layout.addWidget(calc_btn, alignment=Qt.AlignCenter)

        # 清空按钮
        clear_btn = QPushButton("Clear Inputs")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #ca6f1e;
            }
        """)
        clear_btn.clicked.connect(self.clear_inputs)
        layout.addWidget(clear_btn, alignment=Qt.AlignCenter)

        # 输出部分
        output_label = QLabel("Option Price:")
        output_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(output_label)

        self.result_output = QLineEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.result_output)

        
        extra_label = QLabel("95% Confidence Interval:")
        extra_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(extra_label)

        self.std_output = QLineEdit()
        self.std_output.setReadOnly(True)
        self.std_output.setStyleSheet("""
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 6px;
                font-size: 16px;
                color: #34495e;
            }
        """)
        layout.addWidget(self.std_output)

        # 返回按钮
        return_btn = QPushButton("← Back")
        return_btn.clicked.connect(self.return_callback)
        layout.addWidget(return_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def calculate_price(self):
        try:
            S0_1 = float(self.inputs["S0_1"].text())
            S0_2 = float(self.inputs["S0_2"].text())
            K = float(self.inputs["K"].text())
            T = float(self.inputs["T"].text())
            r = float(self.inputs["r"].text())
            correlation= float(self.inputs["cor"].text())
            sigma_1 = float(self.inputs["sigma_1"].text())
            sigma_2 = float(self.inputs["sigma_2"].text())
            num_p = int(self.inputs["N"].text())
            option_type = self.option_type_box.currentText()
            S0=[S0_1,S0_2]
            sigma=[sigma_1,sigma_2]
            option_european = ArithmeticBasketOption(S0, r, T, K, sigma,correlation, option_type,num_p)
            price ,conf_interval= option_european.price()
            self.result_output.setText(f"{price:.4f}")
            self.std_output.setText(f"{conf_interval}") 
        except Exception as e:
            QMessageBox.warning(self, "错误", f"输入参数无效，请检查并重试。\n\n详细信息：{e}")

    def clear_inputs(self):
        for edit in self.inputs.values():
            edit.clear()
        self.result_output.clear()
        self.std_output.clear()


# -------- 运行入口 --------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


