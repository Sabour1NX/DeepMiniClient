import json
import os
import openai
from openai._exceptions import (
    AuthenticationError,
    APIConnectionError,
    RateLimitError,
    APIError
)
from typing import Any, Dict, List, Union, Generator
from datetime import datetime

class AIClientService:
    """AI客户端服务类,用于处理与OpenAI兼容API的交互"""
    
    def __init__(self, config_name):
        self.config_name = config_name
        self.conversation_history = []
        self._config_cache = None
    def read_config(self) -> Dict[str, Any]:
        if self._config_cache is not None:
            return self._config_cache
        
        with open(f'{self.config_name}', 'r', encoding="utf-8") as f:
            AI_config_data = json.load(f)
        AI_config_dict = {
            "api_key": AI_config_data.get('api_key', ''),
            "base_url": AI_config_data.get('base_url', 'https://api.openai.com/v1'),
            "model": AI_config_data.get('model', 'gpt-3.5-turbo'),
            "temperature": float(AI_config_data.get('temperature', 0.7)),
            "max_tokens": int(AI_config_data.get('max_tokens', 2048)),
            "timeout": float(AI_config_data.get('timeout', 30)),
            "stream": bool(AI_config_data.get('stream', False)),
            "top_p": float(AI_config_data.get('top_p', 1.0)),
            "frequency_penalty": float(AI_config_data.get('frequency_penalty', 0.0)),
            "presence_penalty": float(AI_config_data.get('presence_penalty', 0.0)),
            "history_size": int(AI_config_data.get('history_size', 0)),
            "system_prompt": AI_config_data.get('system_prompt', 'You are a helpful assistant.'),
            "log_file": AI_config_data.get('log_file', 'conversation_history.json'),
            "auto_save": bool(AI_config_data.get('auto_save', False))
        }
        self._config_cache = AI_config_dict
        return self._config_cache
    def usr_request(self, content: str) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """处理用户请求
        非流式模式返回字典，流式模式返回生成器
        字典结构: {
            "success": bool,           # 是否成功
            "data": str,               # 成功时的响应内容
            "error": str,              # 失败时的错误信息
            "type": str                # 响应类型: "normal", "stream_chunk", "stream_complete", "error"
        }
        """
        config_dict = self.read_config()
        messages = self._prepare_messages(content, config_dict)
        try:
            client = openai.OpenAI(
                api_key=config_dict["api_key"],
                base_url=config_dict["base_url"],
                timeout=config_dict.get("timeout", 30)
            )
            response = client.chat.completions.create(
                model=config_dict["model"],
                messages=messages,
                temperature=config_dict["temperature"],
                max_tokens=config_dict["max_tokens"],
                stream=config_dict["stream"],
                top_p=config_dict["top_p"],
                frequency_penalty=config_dict["frequency_penalty"],
                presence_penalty=config_dict["presence_penalty"]
            )
            if config_dict["stream"]:
                return self._handle_stream_response(response, content, config_dict)
            else:
                return self._handle_normal_response(response, content, config_dict)

        except AuthenticationError as e:
            error_msg = f"认证失败：{e.message},请检查API Key"
            print(error_msg)
            if config_dict["stream"]:
                return self._stream_error(error_msg)
            else:
                return {
                    "success": False,
                    "data": "",
                    "error": error_msg,
                    "type": "error"
                }
        except APIConnectionError as e:
            error_msg = f"连接服务失败：{e.message}，请检查接口地址和网络"
            print(error_msg)
            if config_dict["stream"]:
                return self._stream_error(error_msg)
            else:
                return {
                    "success": False,
                    "data": "",
                    "error": error_msg,
                    "type": "error"
                }
        except RateLimitError as e:
            error_msg = f"限流触发：{e.message}，请降低请求频率或提升配额"
            print(error_msg)
            if config_dict["stream"]:
                return self._stream_error(error_msg)
            else:
                return {
                    "success": False,
                    "data": "",
                    "error": error_msg,
                    "type": "error"
                }
        except APIError as e:
            error_msg = f"服务接口异常：{e.message}，请检查参数或联系服务提供商"
            print(error_msg)
            if config_dict["stream"]:
                return self._stream_error(error_msg)
            else:
                return {
                    "success": False,
                    "data": "",
                    "error": error_msg,
                    "type": "error"
                }
        except Exception as e:
            error_msg = f"未知错误：{str(e)}"
            print(error_msg)
            if config_dict["stream"]:
                return self._stream_error(error_msg)
            else:
                return {
                    "success": False,
                    "data": "",
                    "error": error_msg,
                    "type": "error"
                }
    def _handle_stream_response(self, response, user_content: str, config_dict: Dict) -> Generator[Dict[str, Any], None, None]:
        """处理流式响应"""
        try:
            full_response = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield {
                        "success": True,
                        "type": "chunk",
                        "content": content,
                        "full_response": full_response,
                        "done": False
                    }
            
            # 完成消息
            yield {
                "success": True,
                "type": "complete",
                "content": full_response,
                "full_response": full_response,
                "done": True
            }
            # 保存对话
            self._save_conversation_turn(user_content, full_response, config_dict)
            
        except Exception as e:
            yield {
                "success": False,
                "type": "error",
                "content": f"流式处理错误: {str(e)}",
                "full_response": "",
                "done": True
            }
    def _handle_normal_response(self, response, user_content: str, config_dict: Dict) -> Dict[str, Any]:
        """处理非流式响应"""
        if response.choices and response.choices[0].message.content:
            ai_response = response.choices[0].message.content
            self._save_conversation_turn(user_content, ai_response, config_dict)
            return {
                "success": True,
                "data": ai_response,
                "error": "",
                "type": "normal"
            }
        return {
            "success": False,
            "data": "",
            "error": "未收到有效响应",
            "type": "error"
        }
    def _stream_error(self, error_message: str) -> Generator[Dict[str, Any], None, None]:
        """返回流式错误信息的生成器"""
        yield {
            "success": False,
            "type": "error",
            "content": error_message,
            "full_response": "",
            "done": True
        }
    
    def _prepare_messages(self, content: str, config_dict: Dict) -> List[Dict]:
        messages = [{"role": "system", "content": config_dict["system_prompt"]}]
        history_size = config_dict.get("history_size", 0)
        if history_size > 0 and self.conversation_history:
            recent_history = self.conversation_history[-history_size:]
            messages.extend(recent_history)
        messages.append({"role": "user", "content": content})
        return messages
    
    def _save_conversation_turn(self, user_content: str, ai_content: str, config_dict: Dict):
        self.conversation_history.extend([
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": ai_content}
        ])
        if config_dict.get("auto_save", False):
            # 直接传递 log_file，让 save_conversation_to_file 处理空字符串
            self.save_conversation_to_file(config_dict.get("log_file"))

    
    def save_conversation_to_file(self, filename: str = None):
        if not filename:
            config_dict = self.read_config()
            filename = config_dict.get("log_file", "conversation_history.json")
        if not filename or filename.strip() == "":
            filename = "conversation_history.json"
        try:
            full_path = os.path.join("Chat_history", filename)
            directory = os.path.dirname(full_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"已创建目录: {directory}")
            conversation_data = {
                "metadata": {
                    "save_time": datetime.now().isoformat(),
                    "config_file": self.config_name,
                    "total_turns": len(self.conversation_history) // 2
                },
                "conversation": self.conversation_history
            }
            with open(full_path, 'w', encoding="utf-8") as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            print(f"对话历史已保存到: {full_path}")
            return True
        except Exception as e:
            print(f"保存对话历史失败: {str(e)}")
            return False
    
    def load_conversation_from_file(self, filename: str = None) -> bool:
        if not filename:
            config_dict = self.read_config()
            filename = config_dict.get("log_file", "conversation_history.json")
        if not filename or filename.strip() == "":
            filename = "conversation_history.json"

        try:
            full_path = os.path.join("Chat_history", filename)

            if not os.path.exists(full_path):
                print(f"对话历史文件不存在: {full_path}")
                return False

            with open(full_path, 'r', encoding="utf-8") as f:
                conversation_data = json.load(f)

            self.conversation_history = conversation_data.get("conversation", [])

            metadata = conversation_data.get("metadata", {})
            save_time = metadata.get("save_time", "未知时间")
            total_turns = metadata.get("total_turns", 0)

            print(f"已加载对话历史 (保存于: {save_time}, 共{total_turns}轮对话)")
            return True

        except json.JSONDecodeError as e:
            print(f"解析对话历史文件失败: {str(e)}")
            return False
        except Exception as e:
            print(f"加载对话历史失败: {str(e)}")
            return False
    
    def clear_conversation_history(self):
        self.conversation_history = []
        print("对话历史已清空")
    
    def get_conversation_summary(self) -> Dict:
        total_turns = len(self.conversation_history) // 2
        total_chars = sum(len(msg.get("content", "")) for msg in self.conversation_history)
        
        return {
            "total_turns": total_turns,
            "total_messages": len(self.conversation_history),
            "total_characters": total_chars,
            "last_user_message": next(
                (msg["content"] for msg in reversed(self.conversation_history) if msg["role"] == "user"),
                None
            )
        }