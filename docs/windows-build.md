# Windows EXE build (macOS'dan)

PyInstaller Windows EXE faylini Windows muhitida yaratadi. Mac'da
GitHub Actions orqali Windows runner'da build qilish mumkin.

1. Ushbu o'zgarishlarni GitHub'ga commit va push qiling.
2. Repo ichida **Actions → Build Windows EXE** bo'limini oching.
3. `main` branch'ga push qilinganda build avtomatik boshlanadi.
   Qo'lda boshlash uchun **Run workflow** tugmasini bosing va kerakli branch'ni tanlang.
4. Build yashil bo'lgach, uning sahifasidagi **Artifacts** bo'limidan
   `HR-Control-windows-<commit>` arxivini yuklab oling.
5. ZIP'ni oching: yangi dastur `HR-Control.exe`.

Repo ildizidagi `HR-Control.exe` va `task-manager.exe` avtomatik yangilanmaydi.
Yangi build natijasi Actions artifact'ida bo'ladi. Commit identifikatori qaysi
koddan build qilinganini ko'rsatadi.

Windows kompyuterda mahalliy build:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\build.ps1
```

Natija: `dist\HR-Control.exe`.
