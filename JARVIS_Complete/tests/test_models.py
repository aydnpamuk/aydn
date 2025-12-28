"""
Models Testleri
"""

from datetime import datetime

import pytest

from jarvis.models import ExpertPrompt, Language, PromptLibrary


def test_expert_prompt_creation():
    """ExpertPrompt oluşturma testi"""
    prompt = ExpertPrompt(
        name="Test",
        prompt_text="Test content",
        description="Test desc",
        tags=["tag1", "tag2"],
        language=Language.TR,
    )

    assert prompt.name == "Test"
    assert prompt.prompt_text == "Test content"
    assert prompt.description == "Test desc"
    assert prompt.tags == ["tag1", "tag2"]
    assert prompt.language == Language.TR
    assert isinstance(prompt.created_at, datetime)
    assert isinstance(prompt.updated_at, datetime)


def test_expert_prompt_update_timestamp():
    """Timestamp güncelleme testi"""
    prompt = ExpertPrompt(name="Test", prompt_text="Content")

    old_time = prompt.updated_at
    import time

    time.sleep(0.01)  # Küçük bir bekleme
    prompt.update_timestamp()

    assert prompt.updated_at > old_time


def test_prompt_library_add():
    """PromptLibrary ekleme testi"""
    library = PromptLibrary()
    prompt = ExpertPrompt(name="Test", prompt_text="Content")

    library.add_prompt(prompt)

    assert "Test" in library.prompts
    assert library.prompts["Test"] == prompt


def test_prompt_library_delete():
    """PromptLibrary silme testi"""
    library = PromptLibrary()
    prompt = ExpertPrompt(name="Test", prompt_text="Content")

    library.add_prompt(prompt)
    library.set_active("Test")

    # Sil
    result = library.delete_prompt("Test")

    assert result is True
    assert "Test" not in library.prompts
    assert library.active_prompt_name is None  # Aktif de silinmeli


def test_prompt_library_set_active():
    """PromptLibrary aktif ayarlama testi"""
    library = PromptLibrary()
    prompt = ExpertPrompt(name="Test", prompt_text="Content")

    library.add_prompt(prompt)
    library.set_active("Test")

    assert library.active_prompt_name == "Test"
    assert library.get_active_prompt() == prompt


def test_prompt_library_get_nonexistent():
    """Olmayan prompt getirme testi"""
    library = PromptLibrary()

    assert library.get_prompt("NonExistent") is None
    assert library.get_active_prompt() is None


def test_prompt_library_list():
    """Prompt listeleme testi"""
    library = PromptLibrary()

    library.add_prompt(ExpertPrompt(name="Prompt1", prompt_text="Content1"))
    library.add_prompt(ExpertPrompt(name="Prompt2", prompt_text="Content2"))

    names = library.list_prompts()

    assert len(names) == 2
    assert "Prompt1" in names
    assert "Prompt2" in names


def test_language_enum():
    """Language enum testi"""
    assert Language.TR.value == "tr"
    assert Language.EN.value == "en"
    assert Language.TR_EN.value == "tr+en"

    # String'den oluşturma
    lang = Language("tr")
    assert lang == Language.TR
