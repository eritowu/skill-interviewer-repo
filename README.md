# Skill 訪談員（skill-interviewer）

透過結構化訪談把專家的判斷方式萃取出來，編譯成可安裝、可攜的跨平台 Skill（Claude / Codex）。
現行凍結版 **v0.2.6**，內層 SHA-256 `2bef9b4e7dc4341ed3693181b6d52152c648e14f048f3644c7eb7543815d69ac`。

## 結構
- `skill-interviewer/` — 套件本體（7 檔）：SKILL.md、references/×4、agents/openai.yaml、scripts/preflight.py
- `docs/changelog.html` — 改版總表（雜湊鏈、逐版公告）
- `CHANGELOG.md` — 精簡版本帳

## 安裝
- Claude：將 `skill-interviewer/` 打包為 zip 後以 Save skill 匯入（或使用官方 package 腳本產出 `.skill`）。
- Codex：置入 skills 目錄，`$skill-interviewer` 觸發。

## 驗證
新環境首次使用先跑：
```
python skill-interviewer/scripts/preflight.py --selftest   # 八夾具全綠才可用於驗收
```
驗收生成的 skill 產出：
```
python skill-interviewer/scripts/preflight.py <目錄或zip> --expect SKILL.md,references/cases.md,agents/openai.yaml
```

## 版本紀律
一版一雜湊（內層）；外層 zip 為信使側封裝，不入版本契約。生成之 skill 的私有訪談 checkpoint 一律置於 `<skill-name>-private/`，永不入庫、永不入包（.gitignore 已涵蓋）。


## License

Licensed under the Apache License 2.0. See `LICENSE`.
