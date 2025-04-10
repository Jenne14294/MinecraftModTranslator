import zipfile
import os
import json
import shutil
import locale
import opencc
import time

from deep_translator import GoogleTranslator

class Translator_function():
    def __init__(self):
        self.cc = opencc.OpenCC('s2t.json')
        # 初始化程式
        self.current_locale = locale.getdefaultlocale()
        self.current_lang = self.current_locale[0].replace("_","-") if "_" in self.current_locale[0] else self.current_locale[0]

        self.info = "正在翻譯"
        # self.info = GoogleTranslator(source='auto', target='zh-TW').translate("正在翻譯", dest = self.current_lang)

    def translate_text(self, text):
        return GoogleTranslator(source='auto', target='zh-TW').translate(text)


    def modify_jar(self, jar_path, file, language_iso):
        try:
            if os.path.exists(self.temp_path):
                os.remove(self.temp_path)

            with zipfile.ZipFile(jar_path, 'r') as jar_file:
                jar_file.extractall(self.temp_path)
        except Exception as e:
            print(e)
            print()
            return

        result = self.modify_lang(self.temp_path, language_iso)
            # 將修改後的資料夾重新壓縮成 JAR 檔案
        if result:
            with zipfile.ZipFile(jar_path, 'a', zipfile.ZIP_DEFLATED) as jar_file:
                # filename (或 file 參數) 是來源檔案的完整路徑
                source_path = os.path.join(self.temp_path, result[0], result[1])
                # arcname 是在 ZIP/JAR 內部的相對路徑
                archive_path = os.path.join(result[0], result[1])

                jar_file.write(source_path, arcname=archive_path)
                # 或者 jar_file.write(file=source_path, arcname=archive_path)

    def modify_lang(self, dir, language_iso):
            dir = os.path.join(dir, "assets")
            if os.path.exists(dir):
                for folder in os.listdir(dir):
                    new_dir = os.path.join(dir, folder, "lang")
                    if os.path.exists(new_dir):
                        final_json = os.path.join(new_dir, f"{language_iso}.json")
                        cn_json = os.path.join(new_dir, f"zh_cn.json")
                        en_json = os.path.join(new_dir, f"en_us.json")

                        final_path = os.path.relpath(final_json, self.temp_path)
                        
                        if os.path.exists(final_json):
                            print(f"該模組已存在 {language_iso} 檔案")
                            return False
                        
                        if os.path.exists(cn_json):
                            with open(cn_json, "r", encoding="utf-8-sig") as file:
                                data = json.load(file)

                            new_data = {k: self.cc.convert(v) for k, v in data.items()}

                            with open(final_json, "w", encoding="utf-8") as file:
                                json.dump(new_data, file, indent=4, ensure_ascii=False)

                            dirpath, filename = os.path.split(final_path)
                            return (dirpath, filename)

                        elif os.path.exists(en_json):
                            with open(en_json, "r", encoding="utf-8-sig") as file:
                                data = json.load(file)

                            new_data = {k: self.translate_text(v) if isinstance(v, str) else v for k, v in data.items()}

                            with open(final_json, "w", encoding="utf-8") as file:
                                json.dump(new_data, file, indent=4, ensure_ascii=False)

                            dirpath, filename = os.path.split(final_path)
                            return (dirpath, filename)
                        
                    return False
            return False

    def start_translate(self, root_path, language_iso, signal=None):
        # os.mkdir(self.temp_path)
        # if self.reset_temp(root_path):
            self.root = root_path
            self.temp_path = os.path.join(root_path, "temp")
            count = len(list(filter(lambda f: f.endswith('.jar'), os.listdir(root_path))))

            for index, file in enumerate(os.scandir(root_path)):
                if file.name.endswith(".jar"):
                    filepath = os.path.join(root_path, file.name)
                    
                    if signal:
                        signal.emit(f"{self.info} : {file.name}\n第 {index + 1} 個 / 共 {count} 個")

                    self.modify_jar(filepath, file.name, language_iso)
                    shutil.rmtree(self.temp_path, ignore_errors=True)

            if signal:
                signal.emit(f"全數模組以翻譯完成！")