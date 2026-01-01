#init_ai_config
import json
import os

class ai_config ():
    def __init__ (self,config_path):
        self.config_path = config_path
        self.config_exist_flag = False

    def create_default_json (self,config_path="",api_key=""):
        if not config_path or config_path.strip() == "":
            config_path = "config.json"
            
        full_config_path = os.path.join("AI_configs", config_path)

        assistant_config = {
            "api_key": f"{api_key}",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 30,
            "stream": True,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "history_size": 10,
            "system_prompt": "You are a helpful AI assistant.",
            "log_file": "conversation_history.json",
            "auto_save": True,
        }

        def create_path_execution (full_config_path):
            parent_dir = os.path.dirname(full_config_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
                print(f"固定目录 {parent_dir} 处理完成（创建成功/已存在）")
            with open (full_config_path,'w',encoding='utf-8') as f:
                        json.dump(assistant_config,f,indent = 2,ensure_ascii=False,sort_keys=False)
                        print(f"默认配置文件已经覆盖/创建{full_config_path}.")
                        self.config_exist_flag = True
                        self.config_path = full_config_path
        try :
            if os.path.exists(full_config_path):
                print(f"警告:配置文件{full_config_path}已经存在.")
                print("是否覆盖?(Y/N)")
                is_coverage = input().strip().upper()
                if is_coverage == "Y":
                    create_path_execution(full_config_path)
                    return True
                elif is_coverage == "N":
                    print(f"文件{full_config_path}未覆盖/未创建.")
                    return False
                else:
                    print("无效输入，请输入 Y 或 N")
                    return False
            else :
                create_path_execution(full_config_path)
                return True
        except Exception as e :
            print(f"Error : 配置文件创建失败 {e}")
            return False
        
    def read_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.config_exist_flag = True
            return config
        except:
            return None