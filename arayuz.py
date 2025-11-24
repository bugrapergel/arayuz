from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from datetime import datetime
import cv2

class ImageProcessingApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.processed_image = None
        self.current_image = None
        self.brightness_value = 100
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Gelişmiş Görüntü İşleme Aracı")
        self.setGeometry(100, 100, 1400, 900)
        
        # Ana widget ve layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("⚙ GELİŞMİŞ GÖRÜNTÜ İŞLEME PLATFORMU")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #fff;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        main_layout.addLayout(title_layout)
        
        # Yükleme butonu
        upload_btn = QtWidgets.QPushButton("📁 YÜKLE: Görsel Seç (JPG, PNG vb.)")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 30px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """)
        upload_btn.clicked.connect(self.load_image)
        main_layout.addWidget(upload_btn)
        
        # Ana içerik alanı (3 panel)
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(15)
        
        # 1. Orjinal Görsel Paneli
        original_panel = self.create_image_panel("ORJİNAL GÖRSEL", "original")
        content_layout.addWidget(original_panel, 1)
        
        # 2. İşlenmiş Görsel Paneli
        processed_panel = self.create_image_panel("İŞLENMİŞ GÖRSEL", "processed")
        content_layout.addWidget(processed_panel, 1)
        
        # 3. Görsel İşlemler Paneli
        operations_panel = self.create_operations_panel()
        content_layout.addWidget(operations_panel, 1)
        
        main_layout.addLayout(content_layout, 2)
        
        # Parlaklık slider
        slider_layout = QtWidgets.QHBoxLayout()
        brightness_label = QtWidgets.QLabel("Parlaklık:")
        brightness_label.setStyleSheet("font-size: 14px; color: #fff;")
        slider_layout.addWidget(brightness_label)
        
        self.brightness_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 8px;
                background: #333;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0066cc;
                border: 1px solid #0052a3;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -6px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #0080ff;
            }
        """)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        slider_layout.addWidget(self.brightness_slider)
        
        self.brightness_value_label = QtWidgets.QLabel("100")
        self.brightness_value_label.setStyleSheet("font-size: 14px; color: #fff; min-width: 50px;")
        slider_layout.addWidget(self.brightness_value_label)
        
        main_layout.addLayout(slider_layout)
        
        # Durum mesajı ve tarih
        status_layout = QtWidgets.QHBoxLayout()
        self.status_label = QtWidgets.QLabel("Hazır")
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #4CAF50;
            padding: 8px;
        """)
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Tarih ve saat
        now = datetime.now()
        turkish_months = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
            5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
            9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
        }
        turkish_days = {
            "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
            "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi",
            "Sunday": "Pazar"
        }
        day_short = {
            "Monday": "Pzt", "Tuesday": "Sal", "Wednesday": "Çar",
            "Thursday": "Per", "Friday": "Cum", "Saturday": "Cmt",
            "Sunday": "Paz"
        }
        month_name = turkish_months[now.month]
        day_name = turkish_days[now.strftime("%A")]
        day_short_name = day_short[now.strftime("%A")]
        date_str = f"{now.day} {month_name} {now.year} {day_name}"
        time_str = f"{day_short_name} {now.strftime('%H:%M')} (Yerel saat)"
        datetime_label = QtWidgets.QLabel(f"{date_str} - {time_str}")
        datetime_label.setStyleSheet("font-size: 12px; color: #aaa;")
        status_layout.addWidget(datetime_label)
        
        main_layout.addLayout(status_layout)
        
        # Karanlık tema
        self.setStyleSheet("""
            QMainWindow {
                background-color: #232629;
            }
            QWidget {
                background-color: #232629;
                color: #EEE;
            }
            QLabel {
                color: #EEE;
            }
        """)
        
    def create_image_panel(self, title, panel_type):
        panel = QtWidgets.QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #18191b;
                border: 2px solid #444;
                border-radius: 10px;
            }
        """)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #fff;
            padding: 10px;
            background-color: #2b2f33;
            border-radius: 5px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Görsel alanı
        image_label = QtWidgets.QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setMinimumSize(400, 500)
        image_label.setStyleSheet("""
            QLabel {
                background-color: #0f0f0f;
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)
        image_label.setText("Görsel yüklenmedi")
        image_label.setStyleSheet(image_label.styleSheet() + """
            color: #888;
            font-size: 14px;
        """)
        
        layout.addWidget(image_label, 1)
        
        if panel_type == "original":
            self.original_label = image_label
        else:
            self.processed_label = image_label
            
        return panel
    
    def create_operations_panel(self):
        panel = QtWidgets.QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #18191b;
                border: 2px solid #444;
                border-radius: 10px;
            }
        """)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QtWidgets.QLabel("GÖRSEL İŞLEMLER")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #fff;
            padding: 10px;
            background-color: #2b2f33;
            border-radius: 5px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # İşlem butonları
        operations = [
            ("☀ Parlaklık Ayarı", self.adjust_brightness),
            ("⚡ Kontrast Ayarı", self.adjust_contrast),
            ("🎞️ Görsel Negatifi", self.image_negative),
            ("📊 Histogram Görüntüle", self.show_histogram),
            ("🔍 Kontrast Germe", self.contrast_stretching),
            ("📈 Histogram Eşitleme", self.histogram_equalization),
            ("γ Gamma Düzeltmesi", self.gamma_correction),
        ]
        
        for text, func in operations:
            btn = QtWidgets.QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0066cc;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 12px;
                    border-radius: 8px;
                    border: none;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #0052a3;
                }
                QPushButton:pressed {
                    background-color: #003d7a;
                }
            """)
            btn.clicked.connect(func)
            layout.addWidget(btn)
        
        layout.addStretch()
        return panel
    
    def load_image(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Görsel Seç", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.original_image = Image.open(file_path).convert('RGB')
            self.processed_image = self.original_image.copy()
            self.current_image = self.original_image
            self.display_image(self.original_image, self.original_label)
            self.display_image(self.processed_image, self.processed_label)
            self.status_label.setText("Görsel yüklendi")
            self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; padding: 8px;")
    
    def display_image(self, image, label):
        if image is None:
            return
        
        # PIL Image'ı QPixmap'e dönüştür
        img_array = np.array(image)
        height, width, channel = img_array.shape
        bytes_per_line = 3 * width
        q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # Label boyutuna göre ölçekle
        label_size = label.size()
        scaled_pixmap = pixmap.scaled(
            label_size.width() - 20, 
            label_size.height() - 20, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
    
    def on_brightness_changed(self, value):
        self.brightness_value = value
        self.brightness_value_label.setText(str(value))
        if self.current_image is not None:
            self.adjust_brightness()
            self.status_label.setText(f"Parlaklık **{value}** değerinde ayarlandı.")
            self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; padding: 8px;")
    
    def adjust_brightness(self):
        if self.original_image is None:
            return
        enhancer = ImageEnhance.Brightness(self.original_image)
        # Slider değeri 0-200 arası, enhancer 0.0-2.0 arası
        factor = self.brightness_value / 100.0
        self.processed_image = enhancer.enhance(factor)
        self.display_image(self.processed_image, self.processed_label)
    
    def adjust_contrast(self):
        if self.original_image is None:
            return
        enhancer = ImageEnhance.Contrast(self.original_image)
        # Varsayılan kontrast faktörü 1.5
        self.processed_image = enhancer.enhance(1.5)
        self.display_image(self.processed_image, self.processed_label)
        self.status_label.setText("Kontrast ayarı uygulandı.")
        self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; padding: 8px;")
    
    def image_negative(self):
        if self.original_image is None:
            return
        self.processed_image = ImageOps.invert(self.original_image)
        self.display_image(self.processed_image, self.processed_label)
        self.status_label.setText("Görsel negatifi uygulandı.")
        self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; padding: 8px;")
    
    def show_histogram(self):
        if self.original_image is None:
            return
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        
        # Histogram penceresi
        hist_window = QtWidgets.QDialog(self)
        hist_window.setWindowTitle("Histogram")
        hist_window.setGeometry(200, 200, 800, 600)
        layout = QtWidgets.QVBoxLayout(hist_window)
        
        fig, axes = plt.subplots(3, 1, figsize=(8, 6))
        fig.patch.set_facecolor('#18191b')
        
        img_array = np.array(self.processed_image if self.processed_image else self.original_image)
        colors = ['red', 'green', 'blue']
        
        for i, color in enumerate(colors):
            axes[i].hist(img_array[:, :, i].ravel(), bins=256, color=color, alpha=0.7)
            axes[i].set_title(f'{color.upper()} Kanalı', color='white')
            axes[i].set_xlabel('Piksel Değeri', color='white')
            axes[i].set_ylabel('Frekans', color='white')
            axes[i].set_facecolor('#0f0f0f')
            axes[i].tick_params(colors='white')
            axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        hist_window.exec_()
        plt.close()
        
        self.status_label.setText("Histogram görüntülendi.")
        self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; padding: 8px;")
    
    def contrast_stretching(self):
        if self.original_image is None:
            return
        img_array = np.array(self.original_image, dtype=np.float32)
        
        # Min-max normalizasyonu
        for i in range(3):
            channel = img_array[:, :, i]
            min_val = np.min(channel)
            max_val = np.max(channel)
            if max_val > min_val:
                img_array[:, :, i] = ((channel - min_val) / (max_val - min_val)) * 255
        
        self.processed_image = Image.fromarray(img_array.astype(np.uint8))
        self.display_image(self.processed_image, self.processed_label)
        self.status_label.setText("Kontrast germe uygulandı.")
        self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; padding: 8px;")
    
    def histogram_equalization(self):
        if self.original_image is None:
            return
        img_array = np.array(self.original_image)
        
        # Her kanal için histogram eşitleme
        equalized_channels = []
        for i in range(3):
            channel = img_array[:, :, i]
            equalized = cv2.equalizeHist(channel)
            equalized_channels.append(equalized)
        
        self.processed_image = Image.fromarray(np.dstack(equalized_channels))
        self.display_image(self.processed_image, self.processed_label)
        self.status_label.setText("Histogram eşitleme uygulandı.")
        self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; padding: 8px;")
    
    def gamma_correction(self):
        if self.original_image is None:
            return
        gamma = 1.5  # Varsayılan gamma değeri
        img_array = np.array(self.original_image, dtype=np.float32) / 255.0
        corrected = np.power(img_array, 1.0 / gamma)
        corrected = (corrected * 255).astype(np.uint8)
        self.processed_image = Image.fromarray(corrected)
        self.display_image(self.processed_image, self.processed_label)
        self.status_label.setText(f"Gamma düzeltmesi (γ={gamma}) uygulandı.")
        self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; padding: 8px;")

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = ImageProcessingApp()
    window.show()
    sys.exit(app.exec_())

