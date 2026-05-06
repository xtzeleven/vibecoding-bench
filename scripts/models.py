"""
Model client adapters - 统一接口适配多家模型 API。

支持：
  - claude-sonnet-4-5 / claude-opus-4   (Anthropic)
  - gpt-4o / gpt-4.1                    (OpenAI)
  - mimo-v2.5                           (Xiaomi MiMo, OpenAI-compatible)
  - deepseek-v3                         (DeepSeek, OpenAI-compatible)
  - qwen3-coder                         (Aliyun DashScope, OpenAI-compatible)

只在调用 .complete() 时才 import SDK，避免不必要的依赖。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol


class ModelClient(Protocol):
    name: str
    last_input_tokens: int | None
    last_output_tokens: int | None

    def complete(self, prompt: str) -> str: ...


@dataclass
class ClaudeClient:
    name: str
    model_id: str
    max_tokens: int = 8192
    last_input_tokens: int | None = None
    last_output_tokens: int | None = None

    def complete(self, prompt: str) -> str:
        from anthropic import Anthropic

        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        resp = client.messages.create(
            model=self.model_id,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        self.last_input_tokens = resp.usage.input_tokens
        self.last_output_tokens = resp.usage.output_tokens
        return resp.content[0].text


@dataclass
class OpenAICompatClient:
    """Works for OpenAI itself, MiMo, DeepSeek, Qwen — anything that speaks OpenAI Chat Completion API."""

    name: str
    model_id: str
    base_url: str = "https://api.openai.com/v1"
    api_key_env: str = "OPENAI_API_KEY"
    max_tokens: int = 8192
    last_input_tokens: int | None = None
    last_output_tokens: int | None = None

    def complete(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ[self.api_key_env],
            base_url=self.base_url,
        )
        resp = client.chat.completions.create(
            model=self.model_id,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        if resp.usage:
            self.last_input_tokens = resp.usage.prompt_tokens
            self.last_output_tokens = resp.usage.completion_tokens
        return resp.choices[0].message.content or ""


REGISTRY: dict[str, ModelClient] = {
    # --- Anthropic ---
    "claude-sonnet-4-5": ClaudeClient(
        name="claude-sonnet-4-5",
        model_id="claude-sonnet-4-5",
    ),
    "claude-opus-4": ClaudeClient(
        name="claude-opus-4",
        model_id="claude-opus-4",
    ),
    # --- OpenAI ---
    "gpt-4o": OpenAICompatClient(
        name="gpt-4o",
        model_id="gpt-4o",
    ),
    "gpt-4.1": OpenAICompatClient(
        name="gpt-4.1",
        model_id="gpt-4.1",
    ),
    # --- Xiaomi MiMo (TODO: confirm exact model_id and base_url with platform docs) ---
    "mimo-v2.5": OpenAICompatClient(
        name="mimo-v2.5",
        model_id="mimo-v2.5",
        base_url="https://api.xiaomimimo.com/v1",
        api_key_env="MIMO_API_KEY",
    ),
    # --- DeepSeek ---
    "deepseek-v3": OpenAICompatClient(
        name="deepseek-v3",
        model_id="deepseek-chat",
        base_url="https://api.deepseek.com/v1",
        api_key_env="DEEPSEEK_API_KEY",
    ),
    # --- Qwen (Aliyun DashScope) ---
    "qwen3-coder": OpenAICompatClient(
        name="qwen3-coder",
        model_id="qwen3-coder-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key_env="DASHSCOPE_API_KEY",
    ),
}


def get_client(name: str) -> ModelClient:
    if name not in REGISTRY:
        raise ValueError(
            f"Unknown model '{name}'. Registered: {sorted(REGISTRY.keys())}"
        )
    return REGISTRY[name]
