"""
Prompt Library Manager Testleri
"""

import tempfile
from pathlib import Path

import pytest

from jarvis.models import ExpertPrompt, Language
from jarvis.prompt_library import PromptLibraryManager


@pytest.fixture
def temp_library_path():
    """Geçici kütüphane dosyası oluştur"""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_path = Path(f.name)
    yield temp_path
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def manager(temp_library_path):
    """PromptLibraryManager instance"""
    return PromptLibraryManager(temp_library_path)


def test_add_prompt(manager):
    """Prompt ekleme testi"""
    prompt = manager.add_prompt(
        name="Test Prompt",
        prompt_text="This is a test prompt.",
        description="Test açıklama",
        tags=["test", "example"],
        language=Language.EN,
    )

    assert prompt.name == "Test Prompt"
    assert prompt.prompt_text == "This is a test prompt."
    assert prompt.description == "Test açıklama"
    assert prompt.tags == ["test", "example"]
    assert prompt.language == Language.EN


def test_add_duplicate_prompt(manager):
    """Aynı isimde prompt ekleme hatası testi"""
    manager.add_prompt(name="Duplicate", prompt_text="First")

    with pytest.raises(ValueError, match="zaten mevcut"):
        manager.add_prompt(name="Duplicate", prompt_text="Second")


def test_get_prompt(manager):
    """Prompt getirme testi"""
    manager.add_prompt(name="Get Test", prompt_text="Content")

    prompt = manager.get_prompt("Get Test")
    assert prompt is not None
    assert prompt.name == "Get Test"

    # Olmayan prompt
    assert manager.get_prompt("NonExistent") is None


def test_delete_prompt(manager):
    """Prompt silme testi"""
    manager.add_prompt(name="Delete Test", prompt_text="Content")
    assert "Delete Test" in manager.library.prompts

    manager.delete_prompt("Delete Test")
    assert "Delete Test" not in manager.library.prompts


def test_delete_nonexistent_prompt(manager):
    """Olmayan prompt silme hatası testi"""
    with pytest.raises(ValueError, match="bulunamadı"):
        manager.delete_prompt("NonExistent")


def test_update_prompt(manager):
    """Prompt güncelleme testi"""
    manager.add_prompt(name="Update Test", prompt_text="Original")

    updated = manager.update_prompt(
        name="Update Test",
        prompt_text="Updated text",
        description="New description",
        tags=["updated"],
    )

    assert updated.prompt_text == "Updated text"
    assert updated.description == "New description"
    assert updated.tags == ["updated"]


def test_set_active_prompt(manager):
    """Aktif prompt ayarlama testi"""
    manager.add_prompt(name="Active Test", prompt_text="Content")

    # Aktif et
    manager.set_active("Active Test")
    assert manager.library.active_prompt_name == "Active Test"

    active = manager.get_active_prompt()
    assert active is not None
    assert active.name == "Active Test"


def test_set_active_to_none(manager):
    """Genel mod (aktif yok) testi"""
    manager.add_prompt(name="Test", prompt_text="Content")
    manager.set_active("Test")

    # Genel moda dön
    manager.set_active(None)
    assert manager.library.active_prompt_name is None
    assert manager.get_active_prompt() is None


def test_list_prompts(manager):
    """Prompt listeleme testi"""
    manager.add_prompt(name="Prompt 1", prompt_text="Content 1")
    manager.add_prompt(name="Prompt 2", prompt_text="Content 2")

    prompts = manager.list_prompts(show_table=False)
    assert len(prompts) == 2
    assert "Prompt 1" in prompts
    assert "Prompt 2" in prompts


def test_search_prompts(manager):
    """Prompt arama testi"""
    manager.add_prompt(
        name="Amazon Expert", prompt_text="Help with Amazon", tags=["amazon", "ads"]
    )
    manager.add_prompt(
        name="Python Expert", prompt_text="Help with Python", tags=["python", "coding"]
    )

    # İsimde ara
    results = manager.search_prompts("Amazon")
    assert len(results) == 1
    assert results[0].name == "Amazon Expert"

    # Tag'de ara
    results = manager.search_prompts("python")
    assert len(results) == 1
    assert results[0].name == "Python Expert"


def test_rename_prompt(manager):
    """Prompt yeniden adlandırma testi"""
    manager.add_prompt(name="Old Name", prompt_text="Content")

    manager.rename_prompt("Old Name", "New Name")

    assert "Old Name" not in manager.library.prompts
    assert "New Name" in manager.library.prompts

    prompt = manager.get_prompt("New Name")
    assert prompt.name == "New Name"


def test_persistence(temp_library_path):
    """Kütüphane kalıcılığı testi (JSON kayıt/yükleme)"""
    # İlk manager ile kaydet
    manager1 = PromptLibraryManager(temp_library_path)
    manager1.add_prompt(name="Persist Test", prompt_text="Content")
    manager1.set_active("Persist Test")

    # Yeni manager ile yükle
    manager2 = PromptLibraryManager(temp_library_path)
    assert "Persist Test" in manager2.library.prompts
    assert manager2.library.active_prompt_name == "Persist Test"

    prompt = manager2.get_prompt("Persist Test")
    assert prompt.prompt_text == "Content"
