import platform
import os
import init_ai_config
import json
from AI_client_service import AIClientService

class Command_handler :
    def __init__ (self):
        self.IsLoop = True
        self.ai_client = None
        self.current_config = None

    def help(self):
        help_info =  """
        ========================================
        DeepMiniClient_AI 对话系统 - 命令列表
        ========================================
        基础命令:
          1. exit             退出程序
            用法: exit
            说明: 退出时会自动卸载AI客户端并保存对话历史
          2. help             显示此帮助信息
            用法: help
          3. system_cmd       启动内置系统终端
            用法: system_cmd
            说明: 输入 'exit' 可退出终端，支持 cd 命令
          4. get_system_info  获取系统信息
            用法: get_system_info
            说明: 显示当前操作系统和版本信息
        配置文件管理:
          5. create_config    创建或更新AI配置文件
            用法: create_config <api_key> [config_name]
            示例: create_config sk-1234567890abcdef
                  create_config sk-1234567890abcdef my_config.json
          6. show_config      显示配置文件内容
            用法: show_config [config_name]
            说明: API密钥会部分隐藏显示
          7. list_configs     列出所有配置文件
            用法: list_configs
            说明: 显示文件名、模型和API密钥状态
        AI客户端管理:
          8. load_ai_client   加载AI客户端服务
            用法: load_ai_client [config_name]
            注意: 使用AI功能前必须加载客户端
          9. unload_ai_client 卸载当前AI客户端服务
            用法: unload_ai_client
            说明: 如果配置了auto_save，会自动保存对话历史
          10. reload_ai_config 重新加载配置文件
             用法: reload_ai_config
             说明: 修改配置文件后刷新，无需重启客户端
        AI对话功能:
          11. chat            与AI进行对话
             用法: chat <消息内容> [--stream/--no-stream]
             示例: chat 你好
                   chat 写一个Python函数 --no-stream
             参数: --stream    流式输出(实时显示)
                   --no-stream 非流式输出(一次性显示)
        对话历史管理:
          12. load_conversation  加载对话历史
             用法: load_conversation [filename]
             说明: 默认使用配置文件中的log_file
          13. save_conversation  保存对话历史
             用法: save_conversation [filename]
             说明: 默认使用配置文件中的log_file
          14. clear_conversation 清空当前对话历史
             用法: clear_conversation
             说明: 需要确认操作
          15. show_conversation  显示对话摘要
             用法: show_conversation
             显示: 对话轮数、消息数、字符数等
        ========================================
        使用流程:
          1. 首次使用: create_config <你的API密钥>
          2. 加载客户端: load_ai_client
          3. 开始对话: chat 你好，请问...
          4. 退出程序: exit
        配置文件位置: AI_configs/
        默认配置: config.json
        ========================================
        """

        print(help_info)

    #def helloworld (self,j=int(1)):
    #    j = int(j)
    #    for i in range (j) :
    #        print("Helloworld!")

    #输入你的函数

    def get_system_info(self):
        """获取系统信息"""
        system = platform.system()
        version = platform.version()
        return f"{system} {version}"

    def create_config(self, api_key="", config_path="config.json"):
        """
        创建或更新AI配置文件
        
        参数:
            api_key: DeepSeek API密钥
            config_name: 配置文件名 (默认: config.json)
        """
        print(f"\n正在创建/更新配置文件: {config_path}")
        print(f"API密钥: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else ''}")
        config_manager = init_ai_config.ai_config(config_path)
        success = config_manager.create_default_json(config_path=config_path,api_key=api_key)
        
        if success:
            print(f"配置文件操作成功: {config_manager.config_path}")
            config = config_manager.read_config()
            if config:
                print(f"配置文件内容已更新")
                print(f"模型: {config.get('model', '')}")
                print(f"API密钥: 已设置 (长度: {len(config.get('api_key', ''))})")
        else:
            print("配置文件操作失败")
        
        return success
    
    def show_config(self, config_name="config.json"):
        """显示配置文件内容"""
        config_path = os.path.join("AI_configs", config_name)
        if not os.path.exists(config_path):
            print(f"配置文件不存在: {config_path}")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"\n配置文件: {config_name}")
            print("=" * 40)
            # 安全显示API密钥
            if "api_key" in config:
                api_key = config["api_key"]
                if api_key:
                    masked_key = api_key[:8] + "..." + (api_key[-4:] if len(api_key) > 12 else "")
                    config["api_key"] = masked_key
                else:
                    config["api_key"] = "(未设置)"
            # 显示所有配置项
            for key, value in config.items():
                print(f"  {key}: {value}")
            print("=" * 40)
        except Exception as e:
            print(f"读取配置文件失败: {e}")
    
    def list_configs(self):
        """列出所有配置文件"""
        config_dir = "AI_configs"
        
        if not os.path.exists(config_dir):
            print(f"配置目录不存在: {config_dir}")
            return
        
        config_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        
        if not config_files:
            print("暂无配置文件")
            return
        
        print(f"\nAI配置目录: {config_dir}")
        print("=" * 40)
        
        for i, file in enumerate(config_files, 1):
            config_path = os.path.join(config_dir, file)
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                model = config.get('model', '未知')
                has_api_key = "True" if config.get('api_key') else "False"
                print(f"  {i}. {file}")
                print(f"     模型: {model}, API密钥: {has_api_key}")
            except:
                print(f"  {i}. {file} (读取失败)")
        print("=" * 40)
        print(f"共 {len(config_files)} 个配置文件")

    def load_ai_client(self, config_name: str = "config.json"):
        """加载AI客户端服务"""
        config_path = os.path.join("AI_configs", config_name)
        
        if not os.path.exists(config_path):
            print(f"配置文件不存在: {config_path}")
            print("请先使用 create_config 命令创建配置文件")
            return False
        
        try:
            print(f"正在加载AI客户端...")
            print(f"配置文件: {config_path}")
            
            self.ai_client = AIClientService(config_path)
            self.current_config = config_path
            
            # 测试配置文件读取
            config = self.ai_client.read_config()
            
            if not config.get("api_key"):
                print("警告: API密钥为空,可能需要设置有效的API密钥")
            
            print("AI客户端加载成功!")
            print(f"模型: {config.get('model')}")
            print(f"API端点: {config.get('base_url')}")
            print(f"流式模式: {'启用' if config.get('stream') else '禁用'}")
            
            return True
            
        except Exception as e:
            print(f"加载AI客户端失败: {str(e)}")
            self.ai_client = None
            self.current_config = None
            return False
    
    def unload_ai_client(self):
        """unload当前AI客户端服务"""
        if self.ai_client:
            print("正在卸载AI客户端...")
            
            # 保存对话历史
            try:
                config = self.ai_client.read_config()
                if config.get("auto_save", False):
                    print("自动保存对话历史...")
                    self.ai_client.save_conversation_to_file()
            except:
                pass
            
            self.ai_client = None
            self.current_config = None
            print("AI客户端已卸载")
        else:
            print("当前没有加载的AI客户端")
    
    def chat(self, *args):
        """与AI进行对话"""
        if not self.ai_client:
            print("请先加载AI客户端: load_ai_client [config_name]")
            return
        
        if not args:
            print("请提供要发送的消息")
            print("用法: chat <message> [--stream/--no-stream]")
            return
        
        # 解析参数
        message = ""
        use_stream = None  # None 表示使用配置文件中的设置
        
        for arg in args:
            if arg == "--stream":
                use_stream = True
            elif arg == "--no-stream":
                use_stream = False
            else:
                if message:
                    message += " " + arg
                else:
                    message = arg
        
        if not message:
            print("请提供要发送的消息")
            return
        
        print(f"发送消息: {message}")
        print("-" * 40)
        
        try:
            # 获取配置以确定是否使用流式
            config = self.ai_client.read_config()
            stream_mode = use_stream if use_stream is not None else config.get("stream", False)
            
            if stream_mode:
                print("流式输出模式:")
                print("-" * 40)
                
                response_generator = self.ai_client.usr_request(message)
                
                for chunk in response_generator:
                    if chunk["success"]:
                        if chunk["type"] == "chunk":
                            print(chunk["content"], end="", flush=True)
                        elif chunk["type"] == "complete":
                            print()  # 换行
                            print("-" * 40)
                            print(f"完整响应已接收,共{len(chunk['full_response'])}字符")
                    else:
                        print(f"\n错误: {chunk.get('error', chunk.get('content', '未知错误'))}")
                        break
            else:
                print("非流式模式...")
                print("-" * 40)
                
                response = self.ai_client.usr_request(message)
                
                if isinstance(response, dict):
                    if response["success"]:
                        print(response["data"])
                        print("-" * 40)
                        print(f"响应完成,共{len(response['data'])}字符")
                    else:
                        print(f"错误: {response['error']}")
            # 显示对话摘要
            summary = self.ai_client.get_conversation_summary()
            print(f"对话统计: {summary['total_turns']}轮对话, {summary['total_characters']}字符")
            
        except KeyboardInterrupt:
            print("\n\n用户中断操作")
        except Exception as e:
            print(f"对话过程中发生错误: {str(e)}")
    
    def load_conversation(self, filename: str = ""):
        """加载对话历史"""
        if not self.ai_client:
            print("请先加载AI客户端")
            return
        
        try:
            success = self.ai_client.load_conversation_from_file(filename)
            if success:
                print("对话历史加载成功")
            else:
                print("对话历史加载失败")
        except Exception as e:
            print(f"加载对话历史时出错: {str(e)}")
    
    def save_conversation(self, filename: str = ""):
        """保存对话历史"""
        if not self.ai_client:
            print("请先加载AI客户端")
            return
        
        try:
            success = self.ai_client.save_conversation_to_file(filename)
            if success:
                print("对话历史保存成功")
            else:
                print("对话历史保存失败")
        except Exception as e:
            print(f"保存对话历史时出错: {str(e)}")
    
    def clear_conversation(self):
        """清空当前对话历史"""
        if not self.ai_client:
            print("请先加载AI客户端")
            return
        
        print("确定要清空对话历史吗？(Y/N)")
        confirmation = input().strip().upper()
        
        if confirmation == "Y":
            self.ai_client.clear_conversation_history()
            print("对话历史已清空")
        else:
            print("操作已取消")
    
    def show_conversation(self):
        """显示当前对话摘要"""
        if not self.ai_client:
            print("请先加载AI客户端")
            return
        
        try:
            summary = self.ai_client.get_conversation_summary()
            
            print("\n对话摘要:")
            print("=" * 40)
            print(f"总对话轮数: {summary['total_turns']}")
            print(f"总消息数: {summary['total_messages']}")
            print(f"总字符数: {summary['total_characters']}")
            
            last_message = summary.get('last_user_message')
            if last_message:
                preview = last_message[:50] + "..." if len(last_message) > 50 else last_message
                print(f"最后用户消息: {preview}")
            
            print("=" * 40)
            
        except Exception as e:
            print(f"获取对话摘要时出错: {str(e)}")
    
    def reload_ai_config(self):
        """重新加载配置文件"""
        if not self.ai_client:
            print("请先加载AI客户端")
            return
        
        try:
            # 清除配置缓存
            self.ai_client._config_cache = None
            config = self.ai_client.read_config()
            print("配置文件重新加载成功")
            print(f"模型: {config.get('model')}")
            print(f"API端点: {config.get('base_url')}")
        except Exception as e:
            print(f"重新加载配置文件失败: {str(e)}")
    
    def exit(self):
        """退出程序"""
        if self.ai_client:
            self.unload_ai_client()
        
        print("Exiting ...")
        self.IsLoop = False

    def system_cmd (self):
        while True:
            print("\n警告:此内置终端会执行你输入的所有系统命令,请注意操作风险！")
            try:
                usr_cwd = os.getcwd()
                print(f"提示:输入 'exit' 可退出终端")
                user_input = input(f"{usr_cwd}> ").strip()
                if user_input:
                    if user_input == "exit" :
                        break
                    elif user_input.lower().startswith("cd "):
                    # 提取要切换的目录（兼容cd后无参数的情况,比如cd回到用户主目录）
                        target_dir = user_input.split(" ", 1)[1] if len(user_input.split(" ", 1)) > 1 else os.path.expanduser("~")
                        try:
                            os.chdir(target_dir)
                        except Exception as e:
                            print(f"ERROR : {e}")
                    else :
                            os.system(user_input)
            except Exception as e :
                print(f"ERROR : {e}")

def main (Script_name = 'DeepMiniClient' ):#命名脚本
    try:
        Current_handler = Command_handler()
        print(f"Wellcome to {Script_name}!\nInput 'help' to check commands.")

        while Current_handler.IsLoop:
            print("Please input your command \n> ",end = "")
            usr_Input = input().strip()

            if not usr_Input :
                continue

            cmd_parts = usr_Input.split()
            command = cmd_parts[0]
            args = cmd_parts[1:]
            
            try:
                Target_handler = getattr(Current_handler,command)
                Target_handler(*args)
            except AttributeError:
                print(f"Unknown command : '{command}' !\n")
            except ValueError as e:
                print(f"ValueError : '{e}'")
            except Exception as e:
                print(f"Except : '{e}'")
    except KeyboardInterrupt:
        print("KeyboardInterrupted,exiting...")

if __name__ == "__main__":
    main()