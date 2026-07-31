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
| v0.2.6 | 2bef9b4e7dc4341e | Windows read 崩潰修復（norm→ZipInfo）；重複鍵恰好一次；$name token boundary；暫存清理；夾具 6→8。雙平台簽核 |
| v0.2.7 | manifest b8744fe6fc7dec93 | 第三方稽核 15 項回修：UTF-16/BOM 受控 FAIL、--expect 雙序與缺值、frontmatter 重複鍵、反掃擴 scripts\|assets、好包零警戒（版本脫鉤可自檢）、--manifest-hash 版本錨、夾具 8→11、description 文件轉換召回＋單次排除、預設值三級消歧、適用範圍註明。待 Codex 副署 |

作廢未流通位元組（勘誤）：b24a6bbbe42becc1（v0.2.3 殘留重打）、a284d504c4e4cd8e（v0.2.6 殘留重打）。

**雜湊政策**：自 v0.2.7 起版本錨＝manifest 雜湊（`preflight.py --manifest-hash` 可重現重算）；v0.2～v0.2.6 為 zip 位元組雜湊，受打包時間與實作影響、無法從內容重算，僅供歷史紀錄與傳輸完整性。v0.2.1–v0.2.5 為開發中版本、未入庫，其雜湊僅為當時產物紀錄。

完整雜湊：

```
v0.2    876509d583e6f83c68a4a7b6b7e1beef40c8f924d21b07af2cc0407cb335a809
v0.2.1  62d99d5338b52df16f24c665536783c438c15981b409feda979005b161da5643
v0.2.2  0b1247fb00e37eb089d8ce00c0debb67f09692d941e4f92bcc147cc5e56ee7fb
作廢    b24a6bbbe42becc125ed260980e698ce2c823ffb51cca1737784d10d67026f80
v0.2.3  74d5e9f6071cfaf6843955a2d86e7a7f47c6a4579b70af720a0b888cf051fff9
v0.2.4  5bb1fc4c89327048ce2c2e953147a0c8d43e394546196e5b1e55b32756fb3636
v0.2.5  7b500e4ff88a595fe8d6d3a500705c4790dbf79ee8a32887a09b9b4475017717
作廢    a284d504c4e4cd8e83c70a083e8d04069fbe858e725bee7a1311c95c91362d02
v0.2.6  2bef9b4e7dc4341ed3693181b6d52152c648e14f048f3644c7eb7543815d69ac
```

v0.3 backlog：12 條（計數由清單推導）——1 F12 人話護欄＋表達／狀態層分離；2 路由載入失敗分支；3 啟動判準題；4 圈外失效案例重圈；5 材料未到手中間態；6 routing event_id；7 失效案例定結構條文；8 traceback 受控錯誤介面；9 checkpoint 一致性診斷；10 projection 語意稽核條文；11 夾具虛構領域護欄；12 判例編號一致性檢查。
（#8 於 v0.2.7 部分落地：編碼與 CLI 類 malformed input 已改受控 FAIL；Codex 六攻擊之三個 traceback 案例待其對 v0.2.7 回驗比對是否同源。）

```
v0.2.7  manifest  b8744fe6fc7dec93a8c8cc4adcd4a5c590b0ec002ee5925c840d892453152f69
        zip傳輸   4343147894a14608…（不入版本契約）
```
