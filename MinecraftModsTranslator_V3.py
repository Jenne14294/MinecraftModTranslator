import zipfile
import os
import json5 as json
import shutil
import locale
import tkinter as tk
import threading  # Import threading module
from googletrans import Translator
from tkinter import messagebox, ttk, filedialog

# Initialize
translator = Translator()
current_locale = locale.getdefaultlocale()
current_lang = current_locale[0].replace("_", "-") if "_" in current_locale[0] else current_locale[0]

Title = translator.translate("Minecraft模組自動翻譯器", dest=current_lang).text
Start_trans = translator.translate("開始翻譯", dest=current_lang).text
mod_route = translator.translate("模組路徑：", dest=current_lang).text
empty_input_title = translator.translate("模組路徑", dest=current_lang).text
empty_input_content = translator.translate("模組路徑不能為空", dest=current_lang).text
wrong_input_content = translator.translate("找不到該模組路徑", dest=current_lang).text
language = translator.translate("翻譯語言：", dest=current_lang).text
Welcome_info = translator.translate(f"歡迎使用 - {Title}", dest=current_lang).text
Suggest_info = translator.translate("使用前建議將模組額外複製一份再進行翻譯，否則可能會出現模組損毀", dest=current_lang).text
Translating = translator.translate("正在翻譯", dest=current_lang).text
Trans_failed = translator.translate("\n以下模組翻譯失敗...", dest=current_lang).text
Translation_failed = translator.translate("Translation failed for", dest=current_lang).text
Already_trans = translator.translate("Module already contains", dest=current_lang).text
Already_trans_2 = translator.translate("language file.", dest=current_lang).text
Extract_fail = translator.translate("Failed to extract：", dest=current_lang).text
Translate_Complete = translator.translate("Translate Complete", dest=current_lang).text

def modify_jar(jar_path, file, file_lang, dest_lang, failed_list, temp_path):
    origin_file = file
    # Extract JAR file
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar_file:
            jar_file.extractall(temp_path)

    except Exception as e:
        failed_list.append(f"{file}\n")
        log_message(f"{Extract_fail} {file}: {e}")
        return

    if modify_lang(temp_path, origin_file, file_lang, dest_lang, failed_list):
        # Compress back into JAR
        with zipfile.ZipFile(jar_path, 'w', zipfile.ZIP_DEFLATED) as jar_file:
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_path)
                    if file.endswith(f'{file_lang}.json'):
                        arcname = arcname.replace('zh_cn.json', f'{file_lang}.json').replace('en_us.json', f'{file_lang}.json')
                    jar_file.write(file_path, arcname)

def modify_lang(dir, filename, file_lang, dest_lang, failed_list):
    for entry in os.scandir(dir):
        if entry.is_dir() and entry.name == 'lang':    
            json_final = os.path.join(entry.path, f'{file_lang}.json')
            if os.path.exists(json_final):
                log_message(f"{Already_trans} {dest_lang} {Already_trans_2}")
                return False

            json_file = os.path.join(entry.path, 'en_us.json')
            if os.path.exists(json_file):
                try:
                    with open(json_file, "r", encoding="utf8") as file:
                        data = json.load(file)
                    
                    data_dest = {k: translator.translate(v, dest=dest_lang).text if v else "" for k, v in data.items()}

                    with open(json_final, "w", encoding="utf8") as file_dest:
                        json.dump(data_dest, file_dest, indent=4, ensure_ascii=False, trailing_commas=False)
                    return True
                    
                except Exception as e:
                    failed_list.append(f"{filename}\n")
                    log_message(f"{Translation_failed} {filename}: {e}")
                    return False
                
        elif entry.is_dir():
            if not modify_lang(entry.path, filename, file_lang, dest_lang, failed_list):
                return False
            
    return True

def open_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        input_route.delete(0, tk.END)
        input_route.insert(0, folder_path)

def start_translator():
    # Run the translation process in a separate thread
    translation_thread = threading.Thread(target=run_translation)
    translation_thread.start()

def run_translation():
    # Get the folder path and validate it
    if not input_route.get():
        messagebox.showwarning(empty_input_title, empty_input_content)
        return

    root_path = input_route.get()
    temp_path = os.path.join(root_path, "temp")

    if not os.path.isdir(root_path):
        messagebox.showerror(empty_input_title, wrong_input_content)
        return

    # Ensure the temp directory exists
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path, ignore_errors=True)

    raw_lang = dropdown.current()
    value = values[raw_lang]
    dest_lang = value.replace("_", "-") if "_" in value else value
    file_lang = value.replace("-", "_") if "-" in value else value
    failed_list = []

    for file in os.scandir(root_path):
        if file.name.endswith(".jar"):
            filepath = os.path.join(root_path, file.name)
            log_message(f"{Translating} : {file.name}")
            modify_jar(filepath, file.name, file_lang, dest_lang, failed_list, temp_path)
            shutil.rmtree(temp_path, ignore_errors=True)
            # Update GUI immediately after each translation
            window.update()

    if failed_list:
        with open(os.path.join(root_path, "Failed_Mods.txt"), "w", encoding="utf8") as file:
            file.writelines(failed_list)
        log_message(Trans_failed)
        for mod in failed_list:
            log_message(mod.strip())

    log_message(Translate_Complete)

def log_message(message):
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, message + "\n")
    text_area.config(state=tk.DISABLED)
    text_area.see(tk.END)

# Initialize the GUI
window = tk.Tk()
window.title(Title)
window.geometry('800x600')
window.resizable(False, False)
window.configure(bg='lightblue')
window.iconbitmap('./icons/icon.ico')

folder_icon = tk.PhotoImage(file='./icons/search_folder.png')

intro_label = tk.Label(window, text=f"{Welcome_info}\n{Suggest_info}", bg='lightblue', font=("Arial", 14, "bold"))
intro_label.place(relx=0.5, rely=0.1, anchor='center')

route_frame = tk.Frame(window, bg='lightblue')
route_frame.place(relx=0.5, rely=0.2, anchor='center')

route_label = tk.Label(route_frame, text=mod_route, bg='lightblue', font=("Arial", 12))
route_label.pack(side=tk.LEFT)

input_route_var = tk.StringVar()
input_route = tk.Entry(route_frame, textvariable=input_route_var, width=50)
input_route.pack(side=tk.LEFT, padx=10)

open_button = tk.Button(route_frame, image=folder_icon, command=open_folder, bg='lightblue', borderwidth=0)
open_button.pack(side=tk.LEFT)

language_label = tk.Label(text=language, bg='lightblue', font=("Arial", 12))
language_label.place(relx=0.3, rely=0.3, anchor='center')

options = ["English", "日本語", "한국어", "繁體中文", "簡體中文"]
values = ["en-us", "ja-jp", "ko-kr", "zh-tw", "zh-cn"]
dropdown = ttk.Combobox(window, values=options, state='readonly')
dropdown.current(0)
dropdown.place(relx=0.5, rely=0.3, anchor='center')

text_area = tk.Text(window, height=15, width=80, state=tk.DISABLED)
text_area.place(relx=0.5, rely=0.55, anchor='center')

start_translate = tk.Button(window, text=Start_trans, bg="green", fg="white", font=("Arial", 12, "bold"), command=start_translator)
start_translate.place(relx=0.5, rely=0.85, anchor='center')

window.mainloop()
