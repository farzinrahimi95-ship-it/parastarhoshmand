from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.core.text import LabelBase
from kivy.uix.filechooser import FileChooserIconView
from kivy.clock import Clock
from kivy.core.window import Window
import arabic_reshaper
from bidi.algorithm import get_display
import json
import os
import shutil
from datetime import datetime
import winsound

Window.clearcolor = (0.76, 0.89, 0.77, 1)
LabelBase.register(name="Farsi", fn_regular="C:/Windows/Fonts/tahoma.ttf")

def f(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

DATA_FILE = "medicines.json"
IMAGE_DIR = "medicine_images"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

class AlertPopup(Popup):
    def __init__(self, medicine, **kwargs):
        super().__init__(**kwargs)
        self.title = f("یادآور دارو")
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = False
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        if medicine.get("image") and os.path.exists(medicine["image"]):
            img = KivyImage(source=medicine["image"], size_hint=(1, 0.5))
            layout.add_widget(img)
        layout.add_widget(Label(text=f(medicine["name"]), font_name="Farsi", font_size=28, size_hint=(1, 0.2)))
        taken_btn = Button(text=f("خوردم دارو"), font_name="Farsi", font_size=22, size_hint=(1, 0.3),
                           background_color=(0.2, 0.7, 0.2, 1))
        taken_btn.bind(on_press=self.dismiss_popup)
        layout.add_widget(taken_btn)
        self.content = layout

    def dismiss_popup(self, instance):
        self.dismiss()

class AddMedicinePopup(Popup):
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.selected_image = ""
        self.title = f("افزودن داروی جدید")
        self.size_hint = (0.85, 0.75)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=f("نام دارو:"), font_name="Farsi", font_size=16))
        self.name_input = TextInput(font_name="Farsi", font_size=16, multiline=False)
        layout.add_widget(self.name_input)
        layout.add_widget(Label(text=f("ساعت مصرف (مثلاً 08:00):"), font_name="Farsi", font_size=16))
        self.time_input = TextInput(font_name="Farsi", font_size=16, multiline=False)
        layout.add_widget(self.time_input)
        self.img_btn = Button(text=f("انتخاب عکس دارو"), font_name="Farsi", font_size=16,
                              background_color=(0.3, 0.5, 0.8, 1))
        self.img_btn.bind(on_press=self.open_file_chooser)
        layout.add_widget(self.img_btn)
        self.img_label = Label(text=f("عکسی انتخاب نشده"), font_name="Farsi", font_size=14)
        layout.add_widget(self.img_label)
        save_btn = Button(text=f("ذخیره دارو"), font_name="Farsi", font_size=18,
                          background_color=(0.2, 0.7, 0.2, 1))
        save_btn.bind(on_press=self.save_medicine)
        layout.add_widget(save_btn)
        self.content = layout

    def open_file_chooser(self, instance):
        file_chooser = FileChooserIconView(filters=["*.png", "*.jpg", "*.jpeg", "*.gif"])
        chooser_popup = Popup(title=f("انتخاب عکس"), content=file_chooser, size_hint=(0.9, 0.8))
        file_chooser.bind(on_submit=self.on_image_selected)
        chooser_popup.open()
        self._chooser_popup = chooser_popup

    def on_image_selected(self, file_chooser, selection, touch):
        if selection:
            self.selected_image = selection[0]
            self.img_label.text = f(f"عکس انتخاب شد: {os.path.basename(self.selected_image)}")
            self._chooser_popup.dismiss()

    def save_medicine(self, instance):
        name = self.name_input.text.strip()
        time = self.time_input.text.strip()
        if name and time:
            image_path = ""
            if self.selected_image:
                ext = os.path.splitext(self.selected_image)[1]
                dest_name = f"{name}_{time.replace(':', '-')}{ext}"
                dest_path = os.path.join(IMAGE_DIR, dest_name)
                shutil.copy2(self.selected_image, dest_path)
                image_path = dest_path
            data = load_data()
            data.append({"name": name, "time": time, "image": image_path})
            save_data(data)
            self.main_screen.refresh_list()
            self.dismiss()

class DeleteMedicinePopup(Popup):
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.title = f("حذف دارو")
        self.size_hint = (0.8, 0.4)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text=f("شماره دارو را وارد کنید (مطابق لیست):"), font_name="Farsi", font_size=16))
        self.number_input = TextInput(font_name="Farsi", font_size=18, multiline=False, input_filter='int')
        layout.add_widget(self.number_input)
        delete_btn = Button(text=f("حذف"), font_name="Farsi", font_size=18, background_color=(0.9, 0.2, 0.2, 1))
        delete_btn.bind(on_press=self.delete_medicine)
        layout.add_widget(delete_btn)
        self.content = layout

    def delete_medicine(self, instance):
        num_text = self.number_input.text.strip()
        if not num_text:
            return
        try:
            index = int(num_text) - 1
        except:
            return
        data = load_data()
        if 0 <= index < len(data):
            removed = data.pop(index)
            if removed.get("image") and os.path.exists(removed["image"]):
                os.remove(removed["image"])
            save_data(data)
            self.main_screen.refresh_list()
        self.dismiss()

class EditMedicinePopup(Popup):
    def __init__(self, main_screen, index, old_data, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.index = index
        self.old_data = old_data
        self.selected_image = old_data.get("image", "")
        self.title = f("ویرایش دارو")
        self.size_hint = (0.85, 0.75)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=f("نام دارو:"), font_name="Farsi", font_size=16))
        self.name_input = TextInput(font_name="Farsi", font_size=16, multiline=False)
        self.name_input.text = old_data["name"]
        layout.add_widget(self.name_input)
        layout.add_widget(Label(text=f("ساعت مصرف (مثلاً 08:00):"), font_name="Farsi", font_size=16))
        self.time_input = TextInput(font_name="Farsi", font_size=16, multiline=False)
        self.time_input.text = old_data["time"]
        layout.add_widget(self.time_input)
        if self.selected_image and os.path.exists(self.selected_image):
            self.img_label = Label(text=f(f"عکس فعلی: {os.path.basename(self.selected_image)}"), font_name="Farsi", font_size=14)
        else:
            self.img_label = Label(text=f("عکسی انتخاب نشده"), font_name="Farsi", font_size=14)
        layout.add_widget(self.img_label)
        self.img_btn = Button(text=f("تغییر عکس دارو"), font_name="Farsi", font_size=16,
                              background_color=(0.3, 0.5, 0.8, 1))
        self.img_btn.bind(on_press=self.open_file_chooser)
        layout.add_widget(self.img_btn)
        save_btn = Button(text=f("ذخیره تغییرات"), font_name="Farsi", font_size=18,
                          background_color=(0.2, 0.7, 0.2, 1))
        save_btn.bind(on_press=self.save_changes)
        layout.add_widget(save_btn)
        self.content = layout

    def open_file_chooser(self, instance):
        file_chooser = FileChooserIconView(filters=["*.png", "*.jpg", "*.jpeg", "*.gif"])
        chooser_popup = Popup(title=f("انتخاب عکس جدید"), content=file_chooser, size_hint=(0.9, 0.8))
        file_chooser.bind(on_submit=self.on_image_selected)
        chooser_popup.open()
        self._chooser_popup = chooser_popup

    def on_image_selected(self, file_chooser, selection, touch):
        if selection:
            self.selected_image = selection[0]
            self.img_label.text = f(f"عکس جدید: {os.path.basename(self.selected_image)}")
            self._chooser_popup.dismiss()

    def save_changes(self, instance):
        name = self.name_input.text.strip()
        time = self.time_input.text.strip()
        if not name or not time:
            return
        if self.selected_image != self.old_data.get("image", ""):
            old_img = self.old_data.get("image", "")
            if old_img and os.path.exists(old_img):
                try:
                    os.remove(old_img)
                except:
                    pass
            if self.selected_image:
                ext = os.path.splitext(self.selected_image)[1]
                dest_name = f"{name}_{time.replace(':', '-')}{ext}"
                dest_path = os.path.join(IMAGE_DIR, dest_name)
                shutil.copy2(self.selected_image, dest_path)
                self.selected_image = dest_path
            else:
                self.selected_image = ""
        data = load_data()
        if 0 <= self.index < len(data):
            data[self.index] = {"name": name, "time": time, "image": self.selected_image}
            save_data(data)
            self.main_screen.refresh_list()
        self.dismiss()

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [40, 20, 40, 20]
        self.spacing = 15

        self.title_label = Label(text=f("پرستار هوشمند"), font_name="Farsi", font_size=26,
                                 size_hint=(1, 0.08), color=(0.1, 0.1, 0.1, 1))
        self.add_widget(self.title_label)

        self.add_btn = Button(text=f("+ افزودن داروی جدید"), font_name="Farsi", font_size=18,
                              size_hint=(1, 0.08), background_color=(0.2, 0.6, 0.2, 1))
        self.add_btn.bind(on_press=self.open_add_popup)
        self.add_widget(self.add_btn)

        self.edit_btn = Button(text=f("✏️ ویرایش دارو"), font_name="Farsi", font_size=18,
                               size_hint=(1, 0.08), background_color=(0.3, 0.5, 0.8, 1))
        self.edit_btn.bind(on_press=self.open_edit_number_popup)
        self.add_widget(self.edit_btn)

        self.del_btn = Button(text=f("🗑️ حذف دارو"), font_name="Farsi", font_size=18,
                              size_hint=(1, 0.08), background_color=(0.9, 0.3, 0.3, 1))
        self.del_btn.bind(on_press=self.open_delete_popup)
        self.add_widget(self.del_btn)

        # --- اینجا رنگ متن لیست را تیره کردیم ---
        self.med_list = Label(text=f("هیچ دارویی ثبت نشده"), font_name="Farsi", font_size=14,
                              size_hint=(1, 0.5), color=(0.1, 0.1, 0.1, 1))
        self.add_widget(self.med_list)

        self.test_btn = Button(text=f("تست آلارم"), font_name="Farsi", font_size=18,
                               size_hint=(1, 0.08), background_color=(1, 0.3, 0.3, 1))
        self.test_btn.bind(on_press=self.test_alarm)
        self.add_widget(self.test_btn)

        self.refresh_list()
        Clock.schedule_interval(self.check_alarms, 30)

    def open_add_popup(self, instance):
        AddMedicinePopup(self).open()

    def open_delete_popup(self, instance):
        DeleteMedicinePopup(self).open()

    def open_edit_number_popup(self, instance):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text=f("شماره دارو را وارد کنید:"), font_name="Farsi"))
        number_input = TextInput(font_name="Farsi", multiline=False, input_filter='int')
        layout.add_widget(number_input)
        continue_btn = Button(text=f("ادامه"), font_name="Farsi", size_hint=(1, 0.3))
        popup = Popup(title=f("ویرایش دارو"), content=layout, size_hint=(0.8, 0.3))
        def on_continue(btn):
            num = number_input.text.strip()
            if num:
                try:
                    idx = int(num) - 1
                    data = load_data()
                    if 0 <= idx < len(data):
                        popup.dismiss()
                        EditMedicinePopup(self, idx, data[idx]).open()
                except:
                    pass
        continue_btn.bind(on_press=on_continue)
        layout.add_widget(continue_btn)
        popup.open()

    def refresh_list(self):
        data = load_data()
        if data:
            lines = []
            for i, med in enumerate(data, 1):
                img_status = "✅" if med.get("image") else "❌"
                lines.append(f"{i}. {med['name']} - ساعت {med['time']} {img_status}")
            self.med_list.text = f("\n".join(lines))
        else:
            self.med_list.text = f("هیچ دارویی ثبت نشده")

    def check_alarms(self, dt):
        now = datetime.now().strftime("%H:%M")
        data = load_data()
        for med in data:
            if med.get("time") == now:
                self.show_alert(med)
                break

    def test_alarm(self, instance):
        self.show_alert({"name": "تست دارو", "time": "00:00", "image": ""})

    def show_alert(self, medicine):
        try:
            winsound.PlaySound("alarm.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass
        AlertPopup(medicine).open()
        Clock.schedule_interval(lambda dt: self.show_alert(medicine), 300)

class ParastarApp(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    ParastarApp().run()