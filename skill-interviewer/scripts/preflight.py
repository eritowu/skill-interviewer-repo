#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skill-interviewer 產出確定性 preflight（v0.2.6）

用法：
    python preflight.py <skill 目錄或 .zip/.skill> [--expect f1,f2,...]
    python preflight.py --selftest

--expect：以 compile receipt 的檔案清單做雙向完全相等（多、缺都擋）。
--selftest：以內建對抗夾具全數驗證腳本自身 fail-closed；新環境
（尤其 Windows）首次使用前必跑。

只檢查機械可判定項；語意項走 compile receipt 與 owner 簽核。
必填矩陣、章節順序與 references/output-template.md 同步維護。
任一 [FAIL] → exit 1。
"""
import base64, io, re, sys, tempfile, zipfile
from pathlib import Path

SYNC_VERSION = "v0.2.6"
COLON = "[：:]"
MASTER = ["範圍自檢", "適用範圍", "輸入與缺失資料處理", "判斷精神", "決策規則",
          "取捨", "例外", "衝突", "工作流程", "工具與環境依賴",
          "交付物格式與驗收標準", "判例集", "需請示區", "測試題",
          "coverage 與未確認假設", "版次與所有權"]
ALWAYS = {"範圍自檢", "適用範圍", "輸入與缺失資料處理", "例外",
          "需請示區", "測試題", "coverage 與未確認假設", "版次與所有權"}
JUDGE = {"判斷精神", "決策規則", "取捨", "判例集"}
WORK = {"工作流程", "工具與環境依賴", "交付物格式與驗收標準"}
MATRIX = {"判斷型": ALWAYS | JUDGE, "做事型": ALWAYS | WORK,
          "混合型": ALWAYS | JUDGE | WORK}
ALLOW = {"SKILL.md", "references/cases.md", "agents/openai.yaml", "governance.yaml"}
FORBID_NAME = ("private", "checkpoint", "receipt", "台帳")

def load(target, errs):
    """回傳 (files: dict[路徑→bytes], root)。zip 一律以 orig_filename 驗路徑。"""
    p = Path(target)
    if p.is_dir():
        return {str(f.relative_to(p)).replace("\\", "/"): f.read_bytes()
                for f in p.rglob("*") if f.is_file()}, p.name
    with zipfile.ZipFile(p) as zf:
        infos = [i for i in zf.infolist() if not i.orig_filename.endswith(("/", "\\"))]
        seen = {}
        for i in infos:
            raw = i.orig_filename                # Windows 下 filename 已被正規化
            if "\\" in raw:
                errs.append(f"壓縮包原始路徑含反斜線：{raw}（Windows 禁用 Compress-Archive）")
            if raw.startswith(("/", "\\")) or ".." in raw:
                errs.append(f"絕對路徑或路徑穿越：{raw}")
            norm = raw.replace("\\", "/")
            if norm in seen:
                errs.append(f"正規化後路徑碰撞：{seen[norm].orig_filename} 與 {raw}")
            seen[norm] = i                       # 存 ZipInfo：read() 直接接受，查找鍵跨平台一致
        names = list(seen)
        roots = {n.split("/", 1)[0] for n in names if "/" in n}
        root = roots.pop() if (len(roots) == 1 and all("/" in n for n in names)) else None
        return {(n.split("/", 1)[1] if root else n): zf.read(seen[n]) for n in names}, root

def check_openai_yaml(raw, skill_name, errs):
    txt = raw.decode("utf-8").replace("\r\n", "\n")
    if len(re.findall(r"^interface\s*:\s*$", txt, re.M)) != 1:
        errs.append("openai.yaml interface: 應恰好出現一次")
    fields = {}
    for k in ("display_name", "short_description", "default_prompt"):
        ms = re.findall(rf'^\s+{k}\s*:\s*(.*)$', txt, re.M)
        if not ms:
            errs.append(f"openai.yaml 缺 {k}"); continue
        if len(ms) > 1:
            errs.append(f"openai.yaml {k} 應恰好出現一次（實得 {len(ms)}）"); continue
        v = ms[0].strip()
        if not (v.startswith('"') and v.endswith('"') and len(v) >= 2):
            errs.append(f"openai.yaml {k} 未加雙引號"); continue
        fields[k] = v[1:-1]
    extra = [ln for ln in txt.splitlines()
             if re.match(r"^\s*[\w-]+\s*:", ln)
             and not re.match(r"^\s*(interface|display_name|short_description|default_prompt)\s*:", ln)]
    if extra:
        errs.append(f"openai.yaml 有預期外欄位：{[l.strip() for l in extra]}")
    sd = fields.get("short_description")
    if sd is not None and not (25 <= len(sd) <= 64):
        errs.append(f"short_description 長度 {len(sd)}，需 25–64")
    dp = fields.get("default_prompt")
    if dp is not None and skill_name and not re.search(
            rf"(?<![A-Za-z0-9-])\${re.escape(skill_name)}(?![A-Za-z0-9-])", dp):
        errs.append(f"default_prompt 缺精確 ${skill_name}（前綴延伸不算）")
    try:
        import yaml
        try: yaml.safe_load(txt)
        except Exception as e: errs.append(f"openai.yaml 無法解析：{e}")
    except ImportError:
        pass                                      # 無 PyYAML 時以上列嚴格逐行檢查為準

def run(files, root, expect=None):
    errs, wrns = [], []
    for f in files:
        if any(k in f.lower() for k in FORBID_NAME):
            errs.append(f"疑似私有製程檔進包：{f}")
    if expect is not None:
        exp = {e.strip() for e in expect if e.strip()}
        if set(files) != exp:
            miss, extra = exp - set(files), set(files) - exp
            if miss: errs.append(f"expected manifest 缺檔：{sorted(miss)}")
            if extra: errs.append(f"expected manifest 外多檔：{sorted(extra)}")
    else:
        extra = set(files) - ALLOW
        if extra: errs.append(f"allowlist 之外的檔案：{sorted(extra)}")
    if "SKILL.md" not in files:
        errs.append("缺 SKILL.md"); return errs, wrns
    text = files["SKILL.md"].decode("utf-8").replace("\r\n", "\n")

    name = None
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errs.append("frontmatter 缺失")
    else:
        keys = dict(re.findall(r"^(\w[\w-]*)\s*:\s*(.+)$", m.group(1), re.M))
        if set(keys) != {"name", "description"}:
            errs.append(f"frontmatter 鍵應恰為 name+description，實得 {sorted(keys)}")
        name = keys.get("name", "").strip().strip('"')
        desc = keys.get("description", "").strip().strip('"')
        if name and not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
            errs.append(f"name 不符小寫連字號 ≤64：{name}")
        if root and name and root != name:
            errs.append(f"資料夾/壓縮根名（{root}）≠ frontmatter name（{name}）")
        if not desc:
            errs.append("description 空白")
        else:
            if not re.search(r"當使用者.+時使用", desc):
                errs.append("description 缺固定觸發句（「當使用者…時使用」）")
            if not re.search(r"不處理|不適用|排除|不產出", desc):
                errs.append("description 缺明確不適用句")
            if len(desc) < 40: wrns.append("description 偏短，觸發語可能不足")

    tm = re.search(rf"^- type{COLON}\s*(判斷型|做事型|混合型)", text, re.M)
    heads = [ln[3:].strip() for ln in text.splitlines() if ln.startswith("## ")]
    def to_master(h):
        for i, mk in enumerate(MASTER):
            if h.startswith(mk): return i
        return None
    if not tm:
        errs.append("版次與所有權缺機讀 type 欄（判斷型｜做事型｜混合型）")
    else:
        need = MATRIX[tm.group(1)]
        present = {MASTER[i] for i in filter(lambda x: x is not None, map(to_master, heads))}
        for n in [k for k in MASTER if k in need]:
            if n not in present:
                errs.append(f"必填章缺失：{n}（缺資料也須保留標題並標 #待補）")
    idxs = [i for i in map(to_master, heads) if i is not None]
    if len(set(idxs)) != len(idxs):
        errs.append("骨架章節重複")
    if idxs != sorted(idxs):
        errs.append("骨架章節順序違約（標題與位置就是契約，順序不可調）")

    st = re.search(r"## 測試題.*?(?=\n## |\Z)", text, re.S)
    if st:
        blk = st.group(0)
        for t in ("正常題", "邊界題"):
            if t not in blk: errs.append(f"self-test seed 缺{t}")
        for fld in ("prompt", "expected behavior", "pass criteria"):
            if len(re.findall(rf"{fld}{COLON}", blk)) < 2:
                errs.append(f"self-test seed 欄位不齊：{fld} 應正常＋邊界各一")

    sm = re.search(rf"^- source{COLON}\s*skill-interviewer\s+(v[\d.]+)", text, re.M)
    if not sm: errs.append("缺 source：skill-interviewer v<版本> 行")
    elif sm.group(1) != SYNC_VERSION:
        wrns.append(f"source 版本 {sm.group(1)} ≠ 腳本同步版本 {SYNC_VERSION}")

    cv = re.search(r"## coverage.*?(?=\n## |\Z)", text, re.S)
    if cv and not ("assumed" in cv.group(0) and "待補" in cv.group(0)):
        wrns.append("coverage 區未見 assumed／#待補 標記，確認是否如實列出")

    for ref in set(re.findall(r"references/[A-Za-z0-9_.\-]+", text)):
        if ref not in files:
            errs.append(f"SKILL.md 引用了 {ref}，但包內不存在")
    for f in files:
        if f.startswith("references/"):
            lines = [ln for ln in text.splitlines() if Path(f).name in ln]
            if not lines:
                errs.append(f"{f} 未被 SKILL.md 引用")
            elif not any(re.search(r"遇到|時讀取|時載入|需要時|相似", ln) for ln in lines):
                errs.append(f"{f} 引用非條件式（「詳見」不合格），須寫明何時讀取")
    if "agents/openai.yaml" in files:
        check_openai_yaml(files["agents/openai.yaml"], name, errs)
    return errs, wrns

def report(errs, wrns):
    for e in errs: print(f"[FAIL] {e}")
    for w in wrns: print(f"[WARN] {w}")
    print(f"== preflight {'FAIL' if errs else 'PASS'}（{len(errs)} 錯誤，{len(wrns)} 警告）==")
    return 1 if errs else 0

GOOD_DOC = """---
name: fx-quote-review
description: 協助新人與 LLM 依主管判準審核供應商報價，產出審核結論與退補件清單。當使用者提到報價單審核、比價、退件時使用。不處理合約談判與付款作業。
---

# 供應商報價審核

## 範圍自檢（執行任何任務前先過這關）
三件事核對。

## 適用範圍
- 處理：報價審核

## 輸入與缺失資料處理
缺報價明細：停止並請示。

## 判斷精神
> 「規格先於價格。」

## 決策規則
**規則 1：規格完整才比價**

## 取捨
先保完整。

## 例外
**例外 1：緊急維修**

## 判例集
遇到與既有判例相似、需核對規則例外或理由時，讀取 references/cases.md；一般案件不必預載。

## 需請示區
- 唯一來源且金額未知

## 測試題（self-test seed）
**正常題**
- prompt：審這張齊備報價
- expected behavior：進入比價
- pass criteria：處置正確，且引用規則 #1
**邊界題**
- prompt：抽走規格欄
- expected behavior：退回補件
- pass criteria：處置翻轉，且引用例外 #1

## coverage 與未確認假設
- `#待補`：未涵蓋情境
- `assumed` 清單：無

## 版次與所有權
- type：判斷型
- owner：採購部
- version：0.1
- interviewed：2026-07-29
- source：skill-interviewer v0.2.6
"""
GOOD_YAML = ('interface:\n  display_name: "報價審核"\n'
             '  short_description: "依主管既有判準審核供應商報價，輸出審核結論與退補件清單"\n'
             '  default_prompt: "Use $fx-quote-review to review this quote."\n')
EVIL_ZIP_B64 = "UEsDBBQAAAAAAAAAAACDFtyMAQAAAAEAAAASAAAAYmFkLXF1b3RlXFNLSUxMLm1keFBLAwQUAAAAAAAAAAAAFSbb+wEAAAABAAAAHAAAAGJhZC1xdW90ZVxhZ2VudHNcb3BlbmFpLnlhbWx5UEsBAhQAFAAAAAAAAAAAAIMW3IwBAAAAAQAAABIAAAAAAAAAAAAAAAAAAAAAAGJhZC1xdW90ZVxTS0lMTC5tZFBLAQIUABQAAAAAAAAAAAAVJtv7AQAAAAEAAAAcAAAAAAAAAAAAAAAAADEAAABiYWQtcXVvdGVcYWdlbnRzXG9wZW5haS55YW1sUEsFBgAAAAACAAIAigAAAGwAAAAAAA=="

def selftest():
    ok = True
    def case(tag, expect_fail, errs, must=None):
        nonlocal ok
        hit = bool(errs) == expect_fail and (must is None or any(must in e for e in errs))
        print(f"[{'OK' if hit else 'NG'}] {tag}" + ("" if hit else f" → {errs}"))
        ok &= hit
    G = {"SKILL.md": GOOD_DOC.encode(), "references/cases.md": b"x",
         "agents/openai.yaml": GOOD_YAML.encode()}
    case("好包通過", False, run(dict(G), "fx-quote-review")[0])
    case("CRLF 合法通過", False,
         run({**G, "SKILL.md": GOOD_DOC.replace("\n", "\r\n").encode()}, "fx-quote-review")[0])
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
        f.write(base64.b64decode(EVIL_ZIP_B64)); evil = f.name
    try:
        e = []; load(evil, e)
        case("原始反斜線 zip 必擋", True, e, must="反斜線")
    finally:
        Path(evil).unlink(missing_ok=True)
    miss = dict(G); miss.pop("references/cases.md")
    case("被引用的 reference 缺檔必擋", True, run(miss, "fx-quote-review")[0], must="不存在")
    bad = dict(G); bad["agents/openai.yaml"] = (
        'interface:\n  display_name: 報價審核\n  short_description: "太短"\n'
        '  default_prompt: "Use $wrong-name here."\n  rogue: "x"\n').encode()
    case("壞 openai.yaml 必擋", True, run(bad, "fx-quote-review")[0], must="openai.yaml")
    parts = GOOD_DOC.split("## coverage 與未確認假設")
    tail = parts[1].split("## 版次與所有權")
    swapped = parts[0] + "## 版次與所有權" + tail[1] + "\n## coverage 與未確認假設" + tail[0]
    case("章節順序違約必擋", True,
         run({**G, "SKILL.md": swapped.encode()}, "fx-quote-review")[0], must="順序")
    dup = dict(G); dup["agents/openai.yaml"] = (
        'interface:\n  display_name: "測試 Skill"\n  display_name: "另一個名稱"\n'
        '  short_description: "依主管既有判準審核供應商報價，輸出審核結論與退補件清單"\n'
        '  default_prompt: "Use $fx-quote-review to review this quote."\n').encode()
    case("重複 metadata 鍵必擋", True, run(dup, "fx-quote-review")[0], must="恰好出現一次")
    pfx = dict(G); pfx["agents/openai.yaml"] = GOOD_YAML.replace(
        "$fx-quote-review", "$fx-quote-review-extra").encode()
    case("skill 名前綴碰撞必擋", True, run(pfx, "fx-quote-review")[0], must="精確")
    print(f"== selftest {'PASS' if ok else 'FAIL'}（8 夾具）==")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    args = sys.argv[1:]
    if args == ["--selftest"]:
        sys.exit(selftest())
    if not args or len(args) > 3:
        print(__doc__); sys.exit(2)
    expect = None
    if "--expect" in args:
        i = args.index("--expect"); expect = args[i + 1].split(","); args = args[:i]
    errs = []
    files, root = load(args[0], errs)
    e2, w2 = run(files, root, expect)
    sys.exit(report(errs + e2, w2))
