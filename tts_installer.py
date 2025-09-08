import sys
import subprocess
import threading
import ensurepip
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

try:
    import pip
except ImportError:
    print("pip 不存在，正在通过 ensurepip 安装 …")
    ensurepip.bootstrap()


def _run_dialog_sync(dialog):
    """Helper to run a dialog synchronously in GTK4 using GLib.MainLoop."""
    loop = GLib.MainLoop()
    dialog.set_modal(True)
    response_holder = {"response": Gtk.ResponseType.NONE}

    def on_response(d, response_id):
        response_holder["response"] = response_id
        loop.quit()

    dialog.connect("response", on_response)
    dialog.show()
    loop.run()  # Starts a nested main loop
    dialog.destroy()
    return response_holder["response"]


def _run_install(window, text_buffer, text_view, on_done, loop):
    """Runs the installation in a separate thread with real-time output."""
    try:
        # Start the pip install process with real-time output
        process = subprocess.Popen(
            [sys.executable, "-m", "pip", "install", "-v", "coqui-tts>=0.27.1", "coqpit-config>=0.2.1", "--i", "https://mirrors.aliyun.com/pypi/simple/"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stdout and stderr
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8'
        )

        # Read output in real-time
        full_output = []
        while True:
            line = process.stdout.readline()
            if not line:
                break

            line = line.rstrip()
            full_output.append(line)

            # Update the text view in the main thread
            def update_text_view():
                end_iter = text_buffer.get_end_iter()
                text_buffer.insert(end_iter, line + '\n')
                # Scroll to bottom
                adj = text_view.get_parent().get_vadjustment()
                adj.set_value(adj.get_upper() - adj.get_page_size())
                return False

            GLib.idle_add(update_text_view)

        # Wait for process to complete
        returncode = process.wait()

        # Final result handling
        if returncode == 0:
            GLib.idle_add(on_done, window, True, None, loop)
        else:
            error_output = '\n'.join(full_output)
            GLib.idle_add(on_done, window, False, error_output, loop)

    except Exception as e:
        # Catch other exceptions like file not found
        GLib.idle_add(on_done, window, False, str(e), loop)


def check_and_install_tts():
    """
    Checks if coqui-tts is installed and prompts for installation if not.
    This function is synchronous.
    Returns True if TTS is available, False otherwise.
    """
    try:
        import TTS
        print("TTS is already installed.")
        return True
    except ImportError:
        Gtk.init_check()

        dialog = Gtk.MessageDialog(
            transient_for=None,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="缺少依赖",
            secondary_text="语音生成功能需要安装核心组件 (coqui-tts)，大约需要 1-2 GB 空间。\n\n" \
                         "是否现在开始下载并安装？ (这可能需要几分钟时间)"
        )
        response = _run_dialog_sync(dialog)

        if response != Gtk.ResponseType.YES:
            print("Installation cancelled by user.")
            info_dialog = Gtk.MessageDialog(
                transient_for=None,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="安装已取消",
                secondary_text="没有安装核心组件，应用即将退出。"
            )
            _run_dialog_sync(info_dialog)
            return False

        install_window = Gtk.Window(title="正在安装")
        install_window.set_deletable(False)
        install_window.set_modal(True)
        install_window.set_default_size(600, 400)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin_top=20, margin_bottom=20, margin_start=30, margin_end=30)
        install_window.set_child(box)

        label = Gtk.Label(label="正在安装核心组件...")
        box.append(label)

        spinner = Gtk.Spinner()
        spinner.start()
        box.append(spinner)

        # Create scrolled text area for real-time output
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_min_content_height(300)
        scrolled.set_margin_top(10)
        text_buffer = Gtk.TextBuffer()
        text_view = Gtk.TextView(buffer=text_buffer)
        text_view.set_editable(False)
        text_view.set_monospace(True)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        scrolled.set_child(text_view)
        box.append(scrolled)


        install_window.show()

        install_result = {"success": False, "error": None}
        install_loop = GLib.MainLoop()

        def on_install_done(window, success, error_message, loop):
            window.destroy()
            install_result['success'] = success
            install_result['error'] = error_message
            loop.quit()

        install_thread = threading.Thread(target=_run_install, args=(install_window, text_buffer, text_view, on_install_done, install_loop))
        install_thread.start()

        install_loop.run()

        if install_result['success']:
            success_dialog = Gtk.MessageDialog(
                transient_for=None,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="安装成功",
                secondary_text="核心组件已成功安装！应用现在将继续启动。"
            )
            _run_dialog_sync(success_dialog)
            return True
        else:
            error_dialog = Gtk.MessageDialog(
                transient_for=None,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="安装失败",
                secondary_text=f"安装过程中发生错误。请检查你的网络连接，或尝试手动安装。\n\n详细错误: {install_result['error']}"
            )
            _run_dialog_sync(error_dialog)
            return False
