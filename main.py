import sys
import os

# Set HF endpoint for Chinese users to download models
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# --- Step 1: Perform dependency check before anything else ---
# This is a blocking call that will use a temporary GTK loop if needed.
from tts_installer import check_and_install_tts


if not check_and_install_tts():
    print("TTS dependencies not met. Exiting.")
    sys.exit(1) # Exit with an error code

# --- Step 2: Dependencies are met, now we can import and run the main app ---
import time
import gi
# Set version requirements for GTK4
gi.require_version("Gtk", "4.0")
import threading
import torch
from gi.repository import GLib, Gdk
from gi.repository import Gtk
from TTS.api import TTS
import settings


class XttsApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.remy.xtts-gtk")
        self.tts_model = None
        self.main_window = None
        self.connect("activate", self.on_activate)

    def _load_model(self):
        """
        Worker function to load the TTS model in a separate thread.
        Reports success or failure back to the main thread.
        """
        print("Starting to load TTS model in background thread...")
        try:
            # This is the time-consuming operation
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            # Schedule the UI update on the main GTK thread
            GLib.idle_add(self._on_model_loaded, "success")
        except Exception as e:
            print(f"Failed to load TTS model: {e}")
            # Report failure back to the main thread
            GLib.idle_add(self._on_model_loaded, "failure", str(e))

    def _on_model_loaded(self, status, error_message=None):
        """
        Callback function executed in the main GTK thread after model loading is attempted.
        """
        self.spinner.stop()
        self.spinner.set_visible(False)

        if status == "success":
            print("TTS model successfully loaded.")
            self.generate_button.set_sensitive(True)
            self.generate_button.set_label("生成语音")
            self.generate_button.connect("clicked", self._on_generate_clicked)
        else:
            print("Disabling generation functionality due to model load failure.")
            self.generate_button.set_label("模型加载失败")
            # Optionally, show an error dialog to the user
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window,
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="无法加载语音模型",
                secondary_text=f"应用将无法生成语音。请检查你的网络连接或模型文件.\n\n错误: {error_message}",
            )
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.show()
        return False # Important: GLib.idle_add callbacks should return False to be removed

    def on_activate(self, app):
        # Create the main window
        self.main_window = Gtk.ApplicationWindow(application=app)
        self.main_window.set_title("XTTS 语音生成")
        self.main_window.set_default_size(1200, 700)


        self.output_folder = None

        # Main horizontal box container
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.main_window.set_child(main_box)

        # --- Left Panel: History ---
        history_frame = Gtk.Frame(label="生成历史", margin_start=6, margin_top=6, margin_bottom=6)
        history_frame.set_size_request(250, -1)
        main_box.append(history_frame)

        history_scrolled_window = Gtk.ScrolledWindow()
        history_frame.set_child(history_scrolled_window)

        self.history_list_box = Gtk.ListBox()
        self.history_list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.history_list_box.connect("row-activated", self._on_history_row_activated)
        history_scrolled_window.set_child(self.history_list_box)

        # --- Center Panel: Text Input ---
        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_top=6, margin_bottom=6)
        center_box.set_hexpand(True)
        main_box.append(center_box)

        input_frame = Gtk.Frame(label="输入文本")
        input_frame.set_vexpand(True)
        center_box.append(input_frame)

        input_scrolled_window = Gtk.ScrolledWindow()
        input_frame.set_child(input_scrolled_window)

        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_view.grab_focus()
        input_scrolled_window.set_child(self.text_view)

        # Add a spinner for loading indication
        self.spinner = Gtk.Spinner()
        center_box.append(self.spinner)

        self.generate_button = Gtk.Button(label="正在加载模型...")
        self.generate_button.set_sensitive(False)  # Disable initially
        center_box.append(self.generate_button)

        # --- Right Panel: Settings ---
        settings_frame = Gtk.Frame(label="设置", margin_end=6, margin_top=6, margin_bottom=6)
        settings_frame.set_size_request(100, -1)
        main_box.append(settings_frame)

        settings_grid = Gtk.Grid(margin_top=6, margin_bottom=6, margin_start=6, margin_end=6, row_spacing=12, column_spacing=6)
        settings_frame.set_child(settings_grid)

        # Language
        lang_label = Gtk.Label(label="语言", halign=Gtk.Align.START)
        settings_grid.attach(lang_label, 0, 0, 1, 1)

        lang_list = Gtk.StringList()
        lang_list.append("中文 (zh-cn)")
        lang_list.append("English (en)")
        self.lang_combo = Gtk.DropDown.new(lang_list, None)
        self.lang_combo.set_selected(0)
        settings_grid.attach(self.lang_combo, 1, 0, 1, 1)

        # speaker
        speaker_label = Gtk.Label(label="音色", halign=Gtk.Align.START)
        settings_grid.attach(speaker_label, 0, 1, 1, 1)

        speaker_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.speaker_entry = Gtk.Entry()
        speaker_box.append(self.speaker_entry)

        self.speaker_button = Gtk.Button(label="浏览...")
        self.speaker_button.connect("clicked", self.select_speaker_clicked)
        speaker_box.append(self.speaker_button)
        settings_grid.attach(speaker_box, 1, 1, 1, 1)

        # Output Directory
        output_label = Gtk.Label(label="输出目录", halign=Gtk.Align.START)
        settings_grid.attach(output_label, 0, 2, 1, 1)

        output_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.output_entry = Gtk.Entry()
        output_box.append(self.output_entry)

        self.output_button = Gtk.Button(label="浏览...")
        self.output_button.connect("clicked", self.on_select_folder_clicked)
        output_box.append(self.output_button)
        settings_grid.attach(output_box, 1, 2, 1, 1)

        self.main_window.present()

        # Start the spinner and the background thread for model loading
        self.spinner.start()
        thread = threading.Thread(target=self._load_model)
        thread.daemon = True  # Allows main thread to exit even if this thread is running
        thread.start()

    def select_speaker_clicked(self, button):
        dialog = Gtk.FileChooserNative(
            title="选择音色",
            transient_for=self.get_active_window(),
            action=Gtk.FileChooserAction.OPEN,
            accept_label="_Select",
            cancel_label="_Cancel",
        )

        def on_response(dialog_instance, response_id):
            if response_id == Gtk.ResponseType.ACCEPT:
                files = dialog_instance.get_files()
                if files:
                    self.speaker_file = files[0]
                    self.speaker_entry.set_text(self.speaker_file.get_path())
            dialog_instance.destroy()

        dialog.connect("response", on_response)
        dialog.show()


    def on_select_folder_clicked(self, button):
        dialog = Gtk.FileChooserNative(
            title="选择输出目录",
            transient_for=self.get_active_window(),
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            accept_label="_Select",
            cancel_label="_Cancel",
        )

        def on_response(dialog_instance, response_id):
            if response_id == Gtk.ResponseType.ACCEPT:
                files = dialog_instance.get_files()
                if files:
                    folder = files[0]
                    self.output_folder = folder.get_path()
                    self.output_entry.set_text(self.output_folder)
            dialog_instance.destroy()

        dialog.connect("response", on_response)
        dialog.show()

    def _on_generate_clicked(self, button):
        buffer = self.text_view.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text_content = buffer.get_text(start_iter, end_iter, True)

        if not text_content.strip():
            return

        speaker_path = self.speaker_entry.get_text()
        output_path = self.output_entry.get_text()
        selected_index = self.lang_combo.get_selected()
        model = self.lang_combo.get_model()

        if model and selected_index != Gtk.INVALID_LIST_POSITION:
            selected_text = model.get_string(selected_index)
            language_id = settings.LANG_ID[selected_text]
            output_file = os.path.join(output_path, f"{int(time.time())}.wav")

            self.spinner.start()
            self.generate_button.set_sensitive(False)
            self.generate_button.set_label("正在生成...")

            thread = threading.Thread(
                target=self._generate_speech_worker,
                args=(text_content, language_id, speaker_path, output_file),
            )
            thread.daemon = True
            thread.start()

    def _generate_speech_worker(self, text, language, speaker_wav, file_path):
        """
        Worker function to generate speech in a separate thread.
        """
        try:
            self.tts_model.tts_to_file(
                text=text,
                language=language,
                speaker_wav=speaker_wav,
                file_path=file_path
            )
            # Pass back a dictionary with all the info
            GLib.idle_add(self._on_generation_finished, "success", {"file_path": file_path, "text": text})
        except Exception as e:
            print(f"Failed to generate speech: {e}")
            GLib.idle_add(self._on_generation_finished, "failure", str(e))

    def _on_generation_finished(self, status, message):
        """
        Callback executed in the main GTK thread after speech generation.
        """
        self.spinner.stop()
        self.generate_button.set_sensitive(True)
        self.generate_button.set_label("生成语音")

        if status == "success":
            file_path = message["file_path"]
            text = message["text"]
            print(f"Speech successfully saved to {file_path}")
            self._add_to_history(text)
        else:
            # message is an error string here
            dialog = Gtk.MessageDialog(
                transient_for=self.main_window,
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="无法生成语音",
                secondary_text=f"生成过程中发生错误。\n\n错误: {message}",
            )
            dialog.connect("response", lambda d, r: d.destroy())
            dialog.show()

        return False

    def _add_to_history(self, full_text):
        """Adds a new entry to the history list."""
        # Create a shortened label for display
        short_text = full_text.replace('\n', ' ').strip()
        if len(short_text) > 35:
            short_text = short_text[:35] + "..."

        label = Gtk.Label(label=short_text, halign=Gtk.Align.START, margin_top=5, margin_bottom=5)

        row = Gtk.ListBoxRow()
        row.set_child(label)

        # Store the full original text within the row widget itself
        row.full_text = full_text

        self.history_list_box.insert(row, 0)

    def _on_history_row_activated(self, list_box, row):
        """Callback for when a history item is clicked."""
        if row and hasattr(row, 'full_text'):
            full_text = row.full_text
            self.text_view.get_buffer().set_text(full_text)

def main():
    app = XttsApp()
    app.run(sys.argv)



if __name__ == "__main__":
    main()
