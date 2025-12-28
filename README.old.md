# aydn  
Bu depo Codex Python Starter için başlangıç iskeletidir.  
Proje klasör yapısı:  
- `src/` — örnek CLI uygulaması  
- `tests/` — pytest örnek testleri  
- `Makefile` — format, lint ve test komutları  
- `requirements.txt` — bağımlılıklar  
- `requirements-dev.txt` — geliştirme bağımlılıkları  
- `.ruff.toml` — Ruff linter yapılandırması  
- `pyproject.toml` — paket yapılandırması  
- `devcontainer.json` — VS Code Dev Container yapılandırması  
  
## Kurulum  
Projenin kurulum adımları:  
  
```bash  
python -m venv .venv  
source .venv/bin/activate  # Windows: .venv\Scripts\activate  
pip install -r requirements.txt -r requirements-dev.txt  
make test  
python -m src.app --help  
```
