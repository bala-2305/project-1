import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView, FileChooser
from kivy.uix.popup import Popup
import qrcode
from io import BytesIO
import cv2
import numpy as np
from PIL import Image as PilImage

class QRCodeApp(App):
    def build(self):
        self.title = 'QR Code Generator and Reader'
        Window.size = (400, 700)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.text_input = TextInput(hint_text='Enter text to generate QR code', multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.text_input)
        
        generate_button = Button(text='Generate QR Code', size_hint=(1, 0.1))
        generate_button.bind(on_press=self.generate_qr_code)
        layout.add_widget(generate_button)
        
        self.qr_image = Image(size_hint=(1, 0.5))
        layout.add_widget(self.qr_image)
        
        save_button = Button(text='Save QR Code', size_hint=(1, 0.1))
        save_button.bind(on_press=self.save_qr_code)
        layout.add_widget(save_button)
        
        read_button = Button(text='Read QR Code', size_hint=(1, 0.1))
        read_button.bind(on_press=self.show_file_chooser)
        layout.add_widget(read_button)
        
        self.result_label = Label(text='', size_hint=(1, 0.1))
        layout.add_widget(self.result_label)
        
        return layout

    def generate_qr_code(self, instance):
        text = self.text_input.text
        if text:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            self.qr_image.texture = CoreImage(buffer, ext='png').texture
            self.qr_image.buffer = buffer

    def save_qr_code(self, instance):
        buffer = self.qr_image.buffer
        if buffer:
            file_chooser = self.create_file_chooser(self.save_to_file, 'Save QR Code', True)
            self.popup = Popup(title='Save QR Code', content=file_chooser, size_hint=(0.9, 0.9))
            self.popup.open()

    def save_to_file(self, file_path):
        if file_path:
            if not file_path.lower().endswith('.png'):
                file_path += '.png'
            buffer = self.qr_image.buffer
            img = PilImage.open(buffer)
            img.save(file_path)
            self.popup.dismiss()

    def show_file_chooser(self, instance):
        file_chooser = self.create_file_chooser(self.load_image, 'Load QR Code', False)
        self.popup = Popup(title='Load QR Code', content=file_chooser, size_hint=(0.9, 0.9))
        self.popup.open()

    def load_image(self, file_path):
        if file_path:
            img = cv2.imread(file_path)
            detector = cv2.QRCodeDetector()
            val, _, _ = detector.detectAndDecode(img)
            if val:
                self.result_label.text = f'Read QR Code: {val}'
            else:
                self.result_label.text = 'No QR Code detected'
            self.popup.dismiss()

    def create_file_chooser(self, on_select, button_text, is_save):
        layout = BoxLayout(orientation='vertical')
        filechooser = FileChooserIconView(size_hint=(1, 0.9), filters=['*.png', '*.jpg', '*.jpeg', '*.bmp'])
        if is_save:
            filechooser.mode = 'save'
        layout.add_widget(filechooser)
        select_button = Button(text=button_text, size_hint=(1, 0.1))
        select_button.bind(on_press=lambda x: on_select(filechooser.selection[0] if filechooser.selection else filechooser.path))
        layout.add_widget(select_button)
        return layout

if __name__ == '__main__':
    QRCodeApp().run()

