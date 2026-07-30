# Changelog

一版一雜湊（僅約束內層 zip）。完整敘事版見 `docs/changelog.html`。

| 版本 | 內層 SHA-256（前 16） | 重點 |
|---|---|---|
| v0.2 | 876509d583e6f83c | 基準：七步流程、雙模式、三入口、資料模型、統一骨架＋必填矩陣、agents/openai.yaml |
| v0.2.1 | 62d99d5338b52df1 | routing 事件化、open/assumed 三態不互轉、owner 同意＋allowlist、語意去識別化、三欄 self-test seed、封閉 allowlist 打包、簽核對實際草稿 |
| v0.2.2 | 0b1247fb00e37eb0 | routing_events 陣列 append-only＋時間戳；版本中立措辭 |
| v0.2.3 | 74d5e9f6071cfaf6 | 三入口一律必經藍圖硬閘門；第七步前置；掃除「兩模式」排除性量詞 |
| v0.2.4 | 5bb1fc4c89327048 | compile receipt；scripts/preflight.py 確定性閘（6→7 檔）；type 機讀欄；禁 Compress-Archive；重開驗證 |
| v0.2.5 | 7b500e4ff88a595f | 腳本六缺口修復（orig_filename、--expect 雙向、yaml 逐行驗、順序表、CRLF、觸發/排除句 FAIL）；--selftest 六夾具內嵌 |
| v0.2.6 | 2bef9b4e7dc4341e | Windows read 崩潰修復（norm→ZipInfo）；重複鍵恰好一次；$name token boundary；暫存清理；夾具 6→8。雙平台簽核，凍結 |

作廢未流通位元組（勘誤）：b24a6bbbe42becc1（v0.2.3 殘留重打）、a284d504c4e4cd8e（v0.2.6 殘留重打）。

v0.3 backlog：13 條，凍結待議。
