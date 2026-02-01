from enum import StrEnum


class Qwen3Model(StrEnum):
    """Qwen3プロバイダーで利用可能なモデル"""

    QWEN_4B = "Qwen/Qwen3-4B-Instruct-2507"
    QWEN_30B = "Qwen/Qwen3-30B-A3B-Instruct-2507"


class Gemma3Model(StrEnum):
    """Gemma3プロバイダーで利用可能なモデル"""

    GEMMA_4B = "google/gemma-3-4b-it"
    GEMMA_27B = "google/gemma-3-27b-it"


class MockModel(StrEnum):
    """Mockプロバイダー"""

    MOCK = "mock"
