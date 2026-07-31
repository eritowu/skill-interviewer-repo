# Skill 訪談員（skill-interviewer）

透過結構化訪談把專家的判斷方式萃取出來，編譯成可安裝、可攜的跨平台 Skill（Claude / Codex）。
現行版 **v0.2.7**，版本錨（manifest 雜湊）`b8744fe6fc7dec93a8c8cc4adcd4a5c590b0ec002ee5925c840d892453152f69`。
自 v0.2.7 起，版本契約以 **manifest 雜湊**為準（`preflight.py <目錄或zip> --manifest-hash` 任何人可重算）；zip 位元組雜湊降為傳輸完整性紀錄。雙平台簽核至 v0.2.7（Codex 2026-07-31 副署：Windows selftest 11/11、manifest 獨立重算相符）。

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
python skill-interviewer/scripts/preflight.py --selftest   # 11 夾具全綠才可用於驗收
python skill-interviewer/scripts/preflight.py skill-interviewer --manifest-hash   # 重算版本錨
```
驗收生成的 skill 產出：
```
python skill-interviewer/scripts/preflight.py <目錄或zip> --expect SKILL.md,references/cases.md,agents/openai.yaml
```

**適用範圍**：preflight 只驗「生成的」skill；對訪談員本體執行會有預期內失敗（allowlist、觸發句、type 欄、source 行、條件式引用），不代表本體有問題。fork 期間資料夾名維持 `skill-interviewer`，版本以 branch 或外層目錄區分，勿放進資料夾名。

## 版本紀律
一版一雜湊：v0.2.7 起錨定 manifest 雜湊（內容可重現）；歷史各版為 zip 位元組雜湊，僅供紀錄。外層 zip 為信使側封裝，不入版本契約。生成之 skill 的私有訪談 checkpoint 一律置於 `<skill-name>-private/`，永不入庫、永不入包（.gitignore 已涵蓋）。


## License

Licensed under the Apache License 2.0. See `LICENSE`.
