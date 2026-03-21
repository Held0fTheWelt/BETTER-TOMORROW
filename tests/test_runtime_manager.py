import json,sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parent.parent))
from runtime import RuntimeManager
class TestRuntimeManager:
 @pytest.fixture
 def temp_state_file(self, tmp_path):
  state_dir = tmp_path / ".claude" / "state"
  state_dir.mkdir(parents=True, exist_ok=True)
  state_file = state_dir / "mode_state.json"
  state_file.write_text(json.dumps({"active_mode": "default"}))
  return state_file
 @pytest.fixture
 def manager(self, temp_state_file, monkeypatch):
  monkeypatch.setattr("runtime.get_mode_state_file", lambda: temp_state_file)
  return RuntimeManager()
 def test_load_mode_returns_default_when_file_missing(self, tmp_path, monkeypatch):
  monkeypatch.setattr("runtime.get_mode_state_file", lambda: tmp_path / "missing.json")
  manager = RuntimeManager()
  assert manager.load_mode() == "default"
 def test_load_mode_returns_current_mode(self, manager):
  assert manager.load_mode() == "default"
 def test_set_mode_validates_mode_name(self, manager):
  result = manager.set_mode("invalid-mode")
  assert result["status"] == "error"
  assert "invalid" in result["message"].lower()
 def test_set_mode_updates_state_file(self, manager):
  result = manager.set_mode("adaptive")
  assert result["status"] == "ok"
  assert manager.load_mode() == "adaptive"
 def test_list_modes_returns_all_modes(self, manager):
  result = manager.list_modes()
  assert result["status"] == "ok"
  assert "default" in result["modes"]
  assert "adaptive" in result["modes"]
  assert "claude-min" in result["modes"]
 def test_get_current_mode_returns_current_mode(self, manager):
  result = manager.get_current_mode()
  assert result["status"] == "ok"
  assert result["mode"] == "default"
 def test_show_menu_returns_formatted_menu(self, manager):
  result = manager.show_menu()
  assert result["status"] == "ok"
  assert result["menu_type"] == "interactive"
  assert "modes" in result
  assert len(result["modes"]) == 3
  assert any(m["active"] for m in result["modes"])
 def test_show_info_returns_mode_details(self, manager):
  result = manager.show_info()
  assert result["status"] == "ok"
  assert "modes" in result
  for mode_key in ["default", "adaptive", "claude-min"]:
   assert mode_key in result["modes"]
   mode_info = result["modes"][mode_key]
   assert "description" in mode_info
   assert "allows_ollama" in mode_info
   assert "allows_claude" in mode_info
