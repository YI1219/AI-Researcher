#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM API 客户端
提供简单易用的接口来调用多种大语言模型
"""

import requests
import json
import time
from typing import Dict, List, Optional, Generator
from dataclasses import dataclass
from enum import Enum
import os

class FunctionSpec:
    """函数规范"""
    name: str
    description: str
    parameters: Dict
    
    def as_openai_tool_dict(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def openai_tool_choice_dict(self):
        return {
            "type": "function",
            "function": {
                "name": self.name
            }
        }

class ModelType(Enum):
    """模型类型枚举"""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"
    DEEPSEEK_R1 = "deepseek-r1"
    DEEPSEEK_V3 = "deepseek-v3"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    QWEN_MAX = "qwen-max-latest"
    O1_PREVIEW = "o1-preview"
    O1_MINI = "o1-mini"

@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # "user", "assistant", "system"
    content: str

@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    model: str
    usage: Dict
    finish_reason: str
    raw_response: Dict

class LLMClient:
    """LLM API 客户端"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or "sk-8bTBbIPyXCqmvgyU83887a149eB145709c9dA58455E0F7F2"
        self.base_url = base_url or "https://api2.road2all.com/v1"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_available_models(self) -> List[Dict]:
        """获取可用模型列表"""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=10)
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                raise Exception(f"获取模型列表失败: {response.status_code}")
        except Exception as e:
            raise Exception(f"获取模型列表异常: {e}")
    
    def chat(self, 
             message: str, 
             model: ModelType = ModelType.GPT_4O_MINI,
             system_prompt: str = None,
             history: List[ChatMessage] = None,
             tools: List[FunctionSpec] = None,
             tool_choice: str = None,
             temperature: float = 0.7,
             max_tokens: int = 1000,
             stream: bool = False) -> ChatResponse:
        """
        发送聊天消息
        
        Args:
            message: 用户消息
            model: 使用的模型
            system_prompt: 系统提示
            history: 历史对话
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
        
        Returns:
            ChatResponse: 聊天响应
        """
        messages = []
        
        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加历史对话
        if history:
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": model.value,
            "messages": messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    choice = result['choices'][0]
                    return ChatResponse(
                        content=choice['message']['content'],
                        model=result.get('model', model.value),
                        usage=result.get('usage', {}),
                        finish_reason=choice.get('finish_reason', 'unknown'),
                        raw_response=result
                    )
                else:
                    raise Exception("响应格式异常")
            else:
                raise Exception(f"API调用失败: {response.status_code}, {response.text}")
                
        except Exception as e:
            raise Exception(f"聊天请求异常: {e}")
    
    def chat_stream(self, 
                   message: str, 
                   model: ModelType = ModelType.GPT_4O_MINI,
                   system_prompt: str = None,
                   history: List[ChatMessage] = None,
                   tools: List[FunctionSpec] = None,
                   tool_choice: str = None,
                   temperature: float = 0.7,
                   max_tokens: int = 1000) -> Generator[str, None, None]:
        """
        流式聊天
        
        Yields:
            str: 流式输出的文本片段
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if history:
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": model.value,
            "messages": messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=60,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                raise Exception(f"流式请求失败: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"流式聊天异常: {e}")
    
    def compare_models(self, 
                      message: str, 
                      models: List[ModelType] = None,
                      system_prompt: str = None) -> Dict[str, ChatResponse]:
        """
        比较多个模型的回答
        
        Args:
            message: 用户消息
            models: 要比较的模型列表
            system_prompt: 系统提示
        
        Returns:
            Dict[str, ChatResponse]: 各模型的响应
        """
        if models is None:
            models = [
                ModelType.GPT_4O_MINI,
                ModelType.CLAUDE_3_5_HAIKU,
                ModelType.DEEPSEEK_R1,
                ModelType.GEMINI_2_0_FLASH
            ]
        
        results = {}
        
        for model in models:
            try:
                print(f"正在测试模型: {model.value}")
                response = self.chat(
                    message=message,
                    model=model,
                    system_prompt=system_prompt,
                    max_tokens=500
                )
                results[model.value] = response
                time.sleep(0.5)  # 避免请求过快
            except Exception as e:
                print(f"模型 {model.value} 调用失败: {e}")
                results[model.value] = None
        
        return results

# 使用示例
def main():
    """使用示例"""
    client = LLMClient()
    
    print("🚀 LLM客户端测试")
    
    # 1. 简单聊天
    print("\n1. 简单聊天测试")
    try:
        response = client.chat("请用一句话介绍量子计算", ModelType.GPT_4O_MINI)
        print(f"回答: {response.content}")
        print(f"Token使用: {response.usage}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 2. 带系统提示的聊天
    print("\n2. 带系统提示的聊天")
    try:
        response = client.chat(
            message="什么是机器学习？",
            model=ModelType.CLAUDE_3_5_HAIKU,
            system_prompt="你是一个专业的AI研究员，请用简洁专业的语言回答问题。"
        )
        print(f"回答: {response.content}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 3. 模型比较
    print("\n3. 模型比较测试")
    try:
        results = client.compare_models(
            message="用一句话解释什么是人工智能",
            models=[ModelType.GPT_4O_MINI, ModelType.CLAUDE_3_5_HAIKU, ModelType.DEEPSEEK_R1]
        )
        
        for model_name, response in results.items():
            if response:
                print(f"\n{model_name}:")
                print(f"  回答: {response.content}")
                print(f"  Token: {response.usage.get('total_tokens', 'N/A')}")
            else:
                print(f"\n{model_name}: 调用失败")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main() 