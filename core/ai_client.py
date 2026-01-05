"""
Gemini API 客戶端封裝
用於 HR 資料處理工具的 AI 功能整合
僅在需要時呼叫，以節省 API 成本
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


class GeminiClient:
    """
    Gemini API 客戶端

    設計原則：
    1. 延遲初始化 - 只在真正需要時才載入 API
    2. 成本追蹤 - 記錄每次呼叫的使用量
    3. 錯誤處理 - 優雅處理 API 錯誤
    """

    def __init__(self, config_path: str = 'config/api_config.json'):
        """
        初始化 Gemini 客戶端

        Args:
            config_path: API 配置檔案路徑
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.usage_log = []
        self._client = None  # 延遲初始化

    def _load_config(self) -> Dict[str, Any]:
        """載入 API 配置"""
        # 確保目錄存在
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

        # 載入配置
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"載入配置失敗: {e}")
                return self._get_default_config()

        # 如果不存在，建立預設配置
        default_config = self._get_default_config()
        self._save_config(default_config)
        return default_config

    def _get_default_config(self) -> Dict[str, Any]:
        """取得預設配置"""
        return {
            'api_key': None,
            'model': 'gemini-1.5-flash',  # 使用較便宜的模型
            'temperature': 0.7,
            'max_tokens': 1000
        }

    def _save_config(self, config: Dict[str, Any]):
        """儲存配置到檔案"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存配置失敗: {e}")

    def is_configured(self) -> bool:
        """檢查 API 是否已配置"""
        return self.config.get('api_key') is not None and self.config['api_key'] != ''

    def set_api_key(self, api_key: str):
        """
        設定 API Key

        Args:
            api_key: Gemini API Key
        """
        self.config['api_key'] = api_key
        self._save_config(self.config)
        self._client = None  # 重置客戶端

    def _initialize_client(self):
        """初始化 Gemini 客戶端（延遲載入）"""
        if self._client is not None:
            return

        if not self.is_configured():
            raise ValueError("Gemini API Key 尚未設定，請先在系統設定中配置")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config['api_key'])
            self._client = genai.GenerativeModel(self.config['model'])
        except ImportError:
            raise ImportError(
                "未安裝 google-generativeai 套件。\n"
                "請執行: pip install google-generativeai"
            )
        except Exception as e:
            raise Exception(f"初始化 Gemini 客戶端失敗: {str(e)}")

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        呼叫 Gemini API 生成回應

        Args:
            prompt: 提示詞
            temperature: 生成溫度 (0-1)，較低更確定性，較高更創意
            max_tokens: 最大生成字符數

        Returns:
            AI 生成的回應文字

        Raises:
            ValueError: 如果 API 未配置
            Exception: 如果 API 呼叫失敗
        """
        # 初始化客戶端
        self._initialize_client()

        # 使用預設值或自訂參數
        temp = temperature if temperature is not None else self.config['temperature']
        max_tok = max_tokens if max_tokens is not None else self.config.get('max_tokens', 1000)

        try:
            # 呼叫 API
            start_time = datetime.now()

            response = self._client.generate_content(
                prompt,
                generation_config={
                    'temperature': temp,
                    'max_output_tokens': max_tok
                }
            )

            end_time = datetime.now()
            response_text = response.text

            # 記錄使用統計
            self._log_usage(
                prompt_length=len(prompt),
                response_length=len(response_text),
                duration=(end_time - start_time).total_seconds()
            )

            return response_text

        except Exception as e:
            # 詳細錯誤處理
            error_msg = str(e)
            if "API_KEY" in error_msg.upper():
                raise ValueError("API Key 無效，請檢查配置")
            elif "QUOTA" in error_msg.upper():
                raise Exception("API 配額已用盡，請稍後再試")
            elif "RATE_LIMIT" in error_msg.upper():
                raise Exception("API 呼叫頻率過高，請稍後再試")
            else:
                raise Exception(f"Gemini API 呼叫失敗: {error_msg}")

    def _log_usage(self, prompt_length: int, response_length: int, duration: float):
        """記錄 API 使用統計"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'prompt_length': prompt_length,
            'response_length': response_length,
            'duration_seconds': duration
        }
        self.usage_log.append(log_entry)

        # 只保留最近 100 筆記錄
        if len(self.usage_log) > 100:
            self.usage_log = self.usage_log[-100:]

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        取得 API 使用統計

        Returns:
            包含使用統計的字典
        """
        if not self.usage_log:
            return {
                'total_calls': 0,
                'total_prompt_chars': 0,
                'total_response_chars': 0,
                'average_duration': 0
            }

        total_calls = len(self.usage_log)
        total_prompt = sum(log['prompt_length'] for log in self.usage_log)
        total_response = sum(log['response_length'] for log in self.usage_log)
        avg_duration = sum(log['duration_seconds'] for log in self.usage_log) / total_calls

        return {
            'total_calls': total_calls,
            'total_prompt_chars': total_prompt,
            'total_response_chars': total_response,
            'average_duration': round(avg_duration, 2)
        }

    def clear_usage_log(self):
        """清空使用記錄"""
        self.usage_log = []

    def test_connection(self) -> tuple[bool, str]:
        """
        測試 API 連接

        Returns:
            (成功與否, 訊息)
        """
        try:
            response = self.generate("測試連接，請回覆 'OK'", max_tokens=10)
            return True, f"連接成功！回應: {response[:50]}"
        except Exception as e:
            return False, f"連接失敗: {str(e)}"
