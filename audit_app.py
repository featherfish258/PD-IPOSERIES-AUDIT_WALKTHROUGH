"""
穿行底稿核查管理 v3.2
===============================================
架构: 配置层 / 解析引擎 / 文件操作层 / 归档索引 / UI 层
UI:   企业级审计仪表盘风格，深色主色调 + 数据可视化
"""

import streamlit as st
import pandas as pd
import os
import re
import io
import shutil
import json
import subprocess
import platform
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
# ============================================================
# 🎨 自定义样式系统
# ============================================================

def inject_custom_css():
    st.markdown("""
    <style>
    /* ========== 导入字体 ========== */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ========== CSS 变量 ========== */
    :root {
        --navy-900: #0a1628;
        --navy-800: #111d33;
        --navy-700: #1a2942;
        --navy-600: #243656;
        --slate-500: #64748b;
        --slate-400: #94a3b8;
        --slate-300: #cbd5e1;
        --slate-100: #f1f5f9;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --accent-amber: #f59e0b;
        --accent-rose: #f43f5e;
        --success-bg: rgba(16, 185, 129, 0.08);
        --danger-bg: rgba(244, 63, 94, 0.08);
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --radius-xl: 20px;
        --shadow-card: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
        --shadow-hover: 0 4px 16px rgba(0,0,0,0.08);
        --font-sans: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-mono: 'JetBrains Mono', 'SF Mono', monospace;
        --ease: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ========== 全局 ========== */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        font-family: var(--font-sans) !important;
    }
    .stApp {
        background: linear-gradient(168deg, #f8fafc 0%, #eef2f7 40%, #e8edf5 100%) !important;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    footer { display: none !important; }
    #MainMenu { visibility: hidden; }

    /* ========== 侧边栏 ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--navy-900) 0%, var(--navy-800) 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    
    /* 修复 1：移除暴力的通配符 *，改为精准定位文本，避免覆盖原生输入框内部结构 */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] { 
        color: var(--slate-300) !important; 
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5 {
        color: #fff !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 1.2rem 0 !important;
    }

    /* 修复 2：使用 data-baseweb 精准穿透输入框外层容器，设置暗色半透明背景 */
    [data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: var(--radius-md) !important;
        transition: all var(--ease);
    }
    
    [data-testid="stSidebar"] div[data-baseweb="input"]:focus-within {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important;
    }
    
    /* 修复 3：针对真实的 input 标签，强制设为白字，并把背景设为透明以露出外层颜色 */
    [data-testid="stSidebar"] div[data-baseweb="input"] input {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important; /* 强制白字，防止浏览器暗黑模式干扰 */
        background-color: transparent !important; 
        font-family: var(--font-mono) !important;
        font-size: 0.85rem !important;
        padding: 0.55rem 0.75rem !important;
    }

    /* 侧边栏按钮保持玻璃态质感 */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.07) !important;
        color: var(--slate-300) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: var(--radius-md) !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 0.5rem 1rem !important;
        transition: all var(--ease) !important;
        backdrop-filter: blur(4px);
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.12) !important;
        border-color: rgba(255,255,255,0.2) !important;
        color: #fff !important;
        transform: translateY(-1px);
    }
    
    /* 侧边栏下拉框和单选框 */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(255,255,255,0.04) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ========== 主标题栏 ========== */
    .hero-banner {
        background: linear-gradient(135deg, var(--navy-900), var(--navy-700));
        border-radius: var(--radius-xl);
        padding: 2rem 2.5rem;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%; right: -15%;
        width: 420px; height: 420px;
        background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: -60%; left: 8%;
        width: 320px; height: 320px;
        background: radial-gradient(circle, rgba(6,182,212,0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-banner h1 {
        color: #fff; font-size: 1.75rem; font-weight: 700;
        letter-spacing: -0.02em; margin: 0 0 0.3rem 0;
        position: relative; z-index: 1;
    }
    .hero-banner p {
        color: var(--slate-400); font-size: 0.88rem; margin: 0;
        position: relative; z-index: 1;
    }

    /* ========== 区域标题 ========== */
    .section-hd {
        display: flex; align-items: center; gap: 0.6rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.7rem;
        border-bottom: 2px solid var(--accent-blue);
    }
    .section-hd .badge {
        width: 32px; height: 32px;
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
        border-radius: var(--radius-sm);
        font-size: 0.95rem; flex-shrink: 0;
    }
    .section-hd h3 {
        color: var(--navy-900); font-size: 1.05rem; font-weight: 600;
        letter-spacing: -0.01em; margin: 0;
    }
    .section-hd .sub {
        color: var(--slate-500); font-size: 0.78rem; font-weight: 400;
        margin-left: auto;
    }

    /* ========== KPI 卡片 ========== */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1rem 0 0.5rem 0;
    }
    .kpi {
        background: #fff;
        border: 1px solid rgba(0,0,0,0.04);
        border-radius: var(--radius-lg);
        padding: 1.3rem 1.5rem;
        box-shadow: var(--shadow-card);
        transition: all var(--ease);
        position: relative; overflow: hidden;
    }
    .kpi:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }
    .kpi .lab {
        font-size: 0.72rem; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.06em;
        color: var(--slate-500); margin-bottom: 0.5rem;
    }
    .kpi .val {
        font-size: 2rem; font-weight: 700;
        line-height: 1.1; font-family: var(--font-mono);
    }
    .kpi .dlt {
        font-size: 0.78rem; font-weight: 600; margin-top: 0.4rem;
        display: inline-flex; align-items: center; gap: 0.25rem;
        padding: 0.15rem 0.55rem; border-radius: 20px;
    }
    .kpi.kpi-t { border-top: 3px solid var(--accent-blue); }
    .kpi.kpi-t .val { color: var(--accent-blue); }
    .kpi.kpi-d { border-top: 3px solid var(--accent-emerald); }
    .kpi.kpi-d .val { color: var(--accent-emerald); }
    .kpi.kpi-d .dlt { background: var(--success-bg); color: var(--accent-emerald); }
    .kpi.kpi-g { border-top: 3px solid var(--accent-rose); }
    .kpi.kpi-g .val { color: var(--accent-rose); }
    .kpi.kpi-g .dlt { background: var(--danger-bg); color: var(--accent-rose); }

    /* ========== 进度条 ========== */
    .prog-wrap { margin: 0.5rem 0 1.5rem 0; }
    .prog-track {
        width: 100%; height: 10px;
        background: #e2e8f0; border-radius: 99px;
        overflow: hidden;
    }
    .prog-fill {
        height: 100%; border-radius: 99px;
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan), var(--accent-emerald));
        background-size: 200% 100%;
        animation: shimmer 2.5s ease-in-out infinite;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }
    @keyframes shimmer {
        0%,100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    .prog-info {
        display: flex; justify-content: space-between;
        font-size: 0.75rem; color: var(--slate-500);
        margin-top: 0.4rem; font-weight: 500;
    }

    /* ========== 主区按钮 ========== */
    .stMainBlockContainer .stButton > button {
        border-radius: var(--radius-md) !important;
        font-weight: 500 !important; font-size: 0.85rem !important;
        padding: 0.55rem 1.2rem !important;
        transition: all var(--ease) !important;
        border: 1px solid #e2e8f0 !important;
    }
    .stMainBlockContainer .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    }
    .stMainBlockContainer .stButton > button[kind="primary"],
    .stMainBlockContainer .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, var(--accent-blue), #2563eb) !important;
        border: none !important; color: #fff !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(59,130,246,0.25) !important;
    }
    .stMainBlockContainer .stButton > button[kind="primary"]:hover,
    .stMainBlockContainer .stButton > button[data-testid="stBaseButton-primary"]:hover {
        box-shadow: 0 6px 20px rgba(59,130,246,0.35) !important;
        transform: translateY(-2px) !important;
    }

    /* ========== 表格 ========== */
    [data-testid="stDataFrame"] {
        border-radius: var(--radius-lg) !important;
        overflow: hidden;
        box-shadow: var(--shadow-card) !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
    }

    /* ========== 上传区 ========== */
    [data-testid="stFileUploader"] > div:first-child {
        border-radius: var(--radius-lg) !important;
        border: 2px dashed #cbd5e1 !important;
        background: rgba(248,250,252,0.5) !important;
        transition: all var(--ease) !important;
    }
    [data-testid="stFileUploader"] > div:first-child:hover {
        border-color: var(--accent-blue) !important;
        background: rgba(59,130,246,0.03) !important;
    }

    /* ========== Multiselect 标签 ========== */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan)) !important;
        color: #fff !important; border: none !important;
        border-radius: 6px !important; font-size: 0.78rem !important;
        font-weight: 500 !important;
    }

    /* ========== 分割线 ========== */
    hr {
        border: none !important; height: 1px !important;
        background: linear-gradient(90deg, transparent, #cbd5e1, transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* ========== 代码块 ========== */
    .stCodeBlock {
        border-radius: var(--radius-md) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
    }

    /* ========== 侧栏项目徽章 ========== */
    .proj-badge {
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(6,182,212,0.1));
        border: 1px solid rgba(59,130,246,0.2);
        padding: 0.35rem 0.8rem; border-radius: var(--radius-md);
        font-size: 0.82rem; font-weight: 600;
        color: var(--accent-cyan) !important;
        margin: 0.5rem 0; letter-spacing: 0.01em;
    }

    /* ========== 已上传文件条目 ========== */
    .file-rec {
        display: flex; align-items: center; gap: 0.4rem;
        padding: 0.35rem 0.6rem;
        background: rgba(255,255,255,0.04);
        border-radius: var(--radius-sm);
        margin-bottom: 0.3rem;
        font-size: 0.78rem; color: var(--slate-400);
        border-left: 2px solid var(--accent-blue);
    }

    /* ========== 维护卡片 ========== */
    .mt-card {
        background: #fff; border-radius: var(--radius-lg);
        padding: 1.2rem 1.4rem; box-shadow: var(--shadow-card);
        border: 1px solid rgba(0,0,0,0.04);
    }
    .mt-card h4 {
        font-size: 0.95rem; font-weight: 600;
        color: var(--navy-900); margin: 0 0 0.3rem 0;
        display: flex; align-items: center; gap: 0.4rem;
    }
    .mt-card .desc {
        font-size: 0.78rem; color: var(--slate-500); margin: 0;
    }

    /* ========== 空状态 ========== */
    .empty-st {
        text-align: center; padding: 3rem 2rem; color: var(--slate-400);
    }
    .empty-st .ic { font-size: 2.5rem; margin-bottom: 0.8rem; opacity: 0.6; }
    .empty-st p { font-size: 0.9rem; margin: 0; }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 🧩 UI 组件库
# ============================================================

def ui_hero():
    now = datetime.now().strftime("%Y年%m月%d日 %A")
    st.markdown(f"""
    <div class="hero-banner">
        <h1>穿行底稿核查管理</h1>
        <p>Audit Walk-Through Evidence Management · {now}</p>
    </div>""", unsafe_allow_html=True)

def ui_section(icon, title, sub=""):
    s = f'<span class="sub">{sub}</span>' if sub else ""
    st.markdown(f"""
    <div class="section-hd">
        <div class="badge">{icon}</div>
        <h3>{title}</h3>{s}
    </div>""", unsafe_allow_html=True)

def ui_kpis(total, done, gap, pct):
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi kpi-t">
            <div class="lab">筛选总数 / Total Samples</div>
            <div class="val">{total}</div>
        </div>
        <div class="kpi kpi-d">
            <div class="lab">已归档 / Archived</div>
            <div class="val">{done}</div>
            <div class="dlt">▲ {pct:.1f}%</div>
        </div>
        <div class="kpi kpi-g">
            <div class="lab">待补缺口 / Pending</div>
            <div class="val">{gap}</div>
            <div class="dlt">▼ {100-pct:.1f}%</div>
        </div>
    </div>""", unsafe_allow_html=True)

def ui_progress(pct, done, total):
    st.markdown(f"""
    <div class="prog-wrap">
        <div class="prog-track">
            <div class="prog-fill" style="width:{pct:.1f}%"></div>
        </div>
        <div class="prog-info">
            <span>归档进度 Archive Progress</span>
            <span>{done} / {total} ({pct:.1f}%)</span>
        </div>
    </div>""", unsafe_allow_html=True)

def ui_empty(icon, msg):
    st.markdown(f"""
    <div class="empty-st">
        <div class="ic">{icon}</div>
        <p>{msg}</p>
    </div>""", unsafe_allow_html=True)


# ============================================================
# 第一层：配置管理
# ============================================================

CONFIG_FILE = "settings.json"

@dataclass
class AppConfig:
    last_root: str = "未选择"
    last_project: str = "项目A"
    ref_file: str = "无"
    up_time: str = "无"
    imported_files_list: list = field(default_factory=list)

    @classmethod
    def load(cls) -> "AppConfig":
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return cls(**{k: v for k, v in json.load(f).items() if k in cls.__dataclass_fields__})
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()

    def save(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)


# ============================================================
# 第二层：核心解析引擎
# ============================================================

RE_DATE_PREFIX = re.compile(r"^\d{4}\.\d{1,2}[-－—]")
RE_YEAR_FULL = re.compile(r"(\d{4})")
RE_YEAR_SHORT = re.compile(r"(\d{2})年")
RE_SUB_INDEX = re.compile(r"[-－—(（](\d+)[)）]?(?:\.[^.]+)?$")
RE_VOUCHER = re.compile(r"(?:^|[\u4e00-\u9fa5]|[-－—]|\d{4}\.\d{1,2}-)(?:记)?(\d+(?:[-－—]\d+)*)")
RE_STRICT = re.compile(r"^(\d+)[.、_](.*?)[-－—](.*?)(\d{4})")
RE_FUZZY = re.compile(r"(.*?)[-－—](.*?)(\d{4})")
RE_LEADING_DIGITS = re.compile(r"^\d+")
RE_SORT_INDEX = re.compile(r"^(\d+)")


def normalize_voucher(voucher) -> str:
    if pd.isna(voucher) or str(voucher).strip() in ("无", "", "nan"):
        return "无"
    v = str(voucher).replace("记", "").replace(" ", "").strip()
    v = RE_DATE_PREFIX.sub("", v)
    return f"记{v}" if v else "无"

def normalize_voucher_core(voucher) -> str:
    v = normalize_voucher(voucher)
    if v == "无": return v
    core = re.sub(r"[-－—]\d+$", "", v.replace("记", ""))
    return f"记{core}" if core else "无"


@dataclass
class ParsedInfo:
    mode: str = "none"
    idx: int = 0
    subject: str = "未分类"
    entity: str = "未知主体"
    year: str = "0"
    voucher_raw: str = "无"
    sub_idx: Optional[str] = None


def extract_info(text) -> Optional[ParsedInfo]:
    if pd.isna(text): return None
    t = str(text).strip()
    if not t: return None

    year = "0"
    m = RE_YEAR_FULL.search(t)
    if m: year = m.group(1)
    else:
        m = RE_YEAR_SHORT.search(t)
        if m: year = f"20{m.group(1)}"

    sub_m = RE_SUB_INDEX.search(t)
    sub_idx = sub_m.group(1) if sub_m else None

    voucher_raw = "无"
    vm = RE_VOUCHER.search(t)
    if vm:
        c = vm.group(1)
        if not (len(c) == 4 and c.startswith("20")):
            voucher_raw = c

    m = RE_STRICT.search(t)
    if m:
        return ParsedInfo(mode="strict", idx=int(m.group(1)),
            subject=RE_LEADING_DIGITS.sub("", m.group(2).strip()).strip(),
            entity=m.group(3).strip(), year=year, voucher_raw=voucher_raw, sub_idx=sub_idx)

    m = RE_FUZZY.search(t)
    if m:
        return ParsedInfo(mode="fuzzy", idx=0,
            subject=RE_LEADING_DIGITS.sub("", m.group(1).strip()).strip(),
            entity=m.group(2).strip(), year=year, voucher_raw=voucher_raw, sub_idx=sub_idx)

    return ParsedInfo(year=year, voucher_raw=voucher_raw)


def get_sort_key(name) -> int:
    m = RE_SORT_INDEX.match(str(name))
    return int(m.group(1)) if m else 999999


# ============================================================
# 第三层：文件操作
# ============================================================

def open_folder(path):
    if not os.path.exists(path):
        st.warning(f"目录不存在: {path}"); return
    try:
        s = platform.system()
        if s == "Windows": os.startfile(path)
        elif s == "Darwin": subprocess.Popen(["open", path])
        else: subprocess.Popen(["xdg-open", path])
    except Exception as e:
        st.error(f"无法打开: {e}")

def _walk_filter(base, yf, sf, ef):
    if not os.path.exists(base): return
    for root, dirs, files in os.walk(base, topdown=False):
        for fn in files:
            info = extract_info(fn)
            if not info: continue
            if yf and info.year not in yf: continue
            if sf and info.subject not in sf: continue
            if ef and info.entity not in ef: continue
            yield os.path.join(root, fn), fn
        for d in dirs:
            dp = os.path.join(root, d)
            try:
                if not os.listdir(dp): os.rmdir(dp)
            except OSError: pass

def delete_archived(base, yf, sf, ef):
    deleted, log = 0, []
    if not os.path.exists(base): return 0, ["目录不存在"]
    for fp, fn in _walk_filter(base, yf, sf, ef):
        try: os.remove(fp); deleted += 1; log.append(f"🗑️ 已删除: {fn}")
        except OSError as e: log.append(f"❌ 失败: {fn} ({e})")
    return deleted, log

def move_back(base, inbox, yf, sf, ef):
    moved, log = 0, []
    if not os.path.exists(base): return 0, ["目录不存在"]
    os.makedirs(inbox, exist_ok=True)
    for fp, fn in _walk_filter(base, yf, sf, ef):
        try: shutil.move(fp, os.path.join(inbox, fn)); moved += 1; log.append(f"↩️ 已撤回: {fn}")
        except Exception as e: log.append(f"❌ 失败: {fn} ({e})")
    return moved, log


# ============================================================
# 第四层：归档索引 O(N+M)
# ============================================================

def build_index(base):
    idx = {}
    if not os.path.exists(base): return idx
    for root, dirs, files in os.walk(base):
        parts = os.path.relpath(root, base).split(os.sep)
        if len(parts) < 2: continue
        key = (parts[0].replace("年",""), parts[1])
        if key not in idx: idx[key] = set()
        for f in files + dirs:
            idx[key].add(f.split(".")[0])
    return idx

def check_status(fdf, base):
    ci = build_index(base)
    st_list = []
    for _, r in fdf.iterrows():
        y, cat = str(r["年份_提取"]), str(r["所属分类"])
        bn = str(r["样本文件命名"]).split(".")[0]
        names = ci.get((y, cat), set())
        st_list.append("✅ 已收到" if any(bn in n for n in names) else "❌ 缺失")
    fdf["状态"] = st_list
    return fdf


# ============================================================
# 第五层：Excel 导入
# ============================================================

def parse_excel(ups):
    rows, errs = [], []
    for f in ups:
        try:
            xls = pd.ExcelFile(f)
            for s in xls.sheet_names: rows.extend(_parse_sheet(xls, s))
        except Exception as e: errs.append(f"解析 {f.name} 失败: {e}")
    return rows, errs

def _parse_sheet(xls, sheet):
    rows = []
    dp = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=50)
    hi = None
    for i, r in dp.iterrows():
        vs = [str(v) for v in r.values if pd.notna(v)]
        if any("日期" in v for v in vs) and any("样本" in v for v in vs):
            hi = i; break
    if hi is None: return rows
    df = pd.read_excel(xls, sheet_name=sheet, header=hi)
    dc = next((c for c in df.columns if "日期" in str(c)), None)
    nc = next((c for c in df.columns if "样本" in str(c)), None)
    if not (dc and nc): return rows
    for _, r in df.dropna(subset=[dc, nc]).iterrows():
        info = extract_info(r[nc])
        if not info: continue
        uid = f"{info.year}_{info.entity}_{sheet}_{normalize_voucher_core(info.voucher_raw)}_{info.idx}"
        rows.append({"业务日期": r[dc], "样本文件命名": r[nc], "主体": info.entity,
            "年份_提取": info.year, "UID": uid,
            "凭证号": normalize_voucher(info.voucher_raw), "所属分类": sheet})
    return rows


# ============================================================
# 第六层：归档引擎
# ============================================================

@dataclass
class Stats:
    success: int = 0
    log: list = field(default_factory=list)

def run_archive(inbox, base, fdf, dup) -> Stats:
    stats = Stats()
    if not os.path.exists(inbox):
        stats.log.append("❌ 待整理目录不存在"); return stats
    for root, dirs, files in os.walk(inbox, topdown=True):
        items = [(d, True) for d in list(dirs)] + [(f, False) for f in files]
        for name, is_dir in items:
            src = os.path.join(root, name)
            info = extract_info(name)
            if not info or info.mode == "none":
                stats.log.append(f"❌ 跳过 (不规范): {name}"); continue
            match = _find_match(fdf, info)
            if match is None:
                if not is_dir: stats.log.append(f"❌ 匹配失败: {name}")
                continue
            std = str(match["样本文件命名"])
            cp = os.path.join(base, f"{info.year}年", match["所属分类"])
            if info.sub_idx or is_dir:
                td = os.path.join(cp, std)
                tn = f"{std}-{info.sub_idx}{os.path.splitext(name)[1]}" if info.sub_idx else name
            else:
                td = cp; tn = std + os.path.splitext(name)[1]
            os.makedirs(td, exist_ok=True)
            dest = os.path.join(td, tn)
            if os.path.exists(dest) and "跳过" in dup:
                stats.log.append(f"⏭️ 跳过: {name}"); continue
            try:
                shutil.move(src, dest)
                if is_dir and name in dirs: dirs.remove(name)
                tag = "📁 建包" if (info.sub_idx or is_dir) else "📄 标准"
                stats.success += 1
                stats.log.append(f"✅ [{tag}] {name} → {match['所属分类']}/{tn}")
            except Exception as e:
                stats.log.append(f"❌ 移动失败: {name} ({e})")
    return stats

def _find_match(fdf, info):
    mask = (
        fdf["所属分类"].str.contains(info.subject, regex=False, na=False)
        & (fdf["年份_提取"] == info.year) & (fdf["主体"] == info.entity)
        & (fdf["凭证号"] == normalize_voucher(info.voucher_raw))
    )
    matched = fdf[mask]
    if matched.empty: return None
    if info.idx > 0:
        im = matched[matched["样本文件命名"].astype(str).str.match(f"^{info.idx}[.、_]")]
        return im.iloc[0] if not im.empty else None
    return matched.iloc[0]


# ============================================================
# 第七层：Streamlit UI
# ============================================================

def main():
    st.set_page_config(page_title="穿行底稿核查管理", page_icon="🛡️",
                       layout="wide", initial_sidebar_state="expanded")
    inject_custom_css()

    cfg = AppConfig.load()
    if "root_path" not in st.session_state: st.session_state.root_path = cfg.last_root
    if "imported_files" not in st.session_state: st.session_state.imported_files = list(cfg.imported_files_list)
    if "master_df" not in st.session_state: st.session_state.master_df = pd.DataFrame()

    db = _sidebar(cfg)
    ui_hero()
    _load_db(db)
    _import_ui(db, cfg)

    if not st.session_state.master_df.empty:
        _workspace(db, cfg)
    else:
        ui_empty("📋", "请先导入 Excel 抽样清单开始工作")


def _sidebar(cfg):
    db = None
    with st.sidebar:
        st.markdown("### ⚙️ 项目环境")
        pn = st.text_input("项目名称", cfg.last_project, placeholder="输入项目名称...")
        # 替换原有的 np = st.text_input(...) 这一行
        st.markdown("<p style='font-size: 0.88rem; margin-bottom: 0.2rem;'>存储根目录</p>", unsafe_allow_html=True)
        c_input, c_btn = st.columns([4, 1])
        
        with c_input:
            # 你代码里原本极具前瞻性的写法：
            np = st.text_input("存储根目录", value=st.session_state.root_path,
                   placeholder="输入路径...", help="项目文件根目录")
        if np != st.session_state.root_path:
            st.session_state.root_path = np
            cfg.last_root = np; cfg.last_project = pn; cfg.save()

        if st.session_state.root_path != "未选择":
            pr = os.path.join(st.session_state.root_path, pn)
            bd = os.path.join(pr, "归档"); ib = os.path.join(pr, "待整理")
            db = os.path.join(pr, "master_db.csv")
            st.session_state.update(base_dir=bd, inbox_dir=ib, p_name=pn)

            st.markdown(f'<div class="proj-badge">📂 {pn}</div>', unsafe_allow_html=True)
            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

            if st.button("🏗️ 初始化目录", use_container_width=True):
                os.makedirs(bd, exist_ok=True); os.makedirs(ib, exist_ok=True)
                st.toast("目录已就绪 ✅")

            st.divider()
            st.markdown("##### 快捷访问")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📂 待整理", use_container_width=True): open_folder(ib)
            with c2:
                if st.button("🗄️ 归档库", use_container_width=True): open_folder(bd)

            st.divider()
            st.markdown("##### 重复策略")
            st.session_state.dup_strategy = st.radio("策略", ["跳过", "覆盖", "保留两者"],
                                                      label_visibility="collapsed")
        else:
            st.info("💡 请先设置存储根目录")
    return db


def _load_db(db):
    if not db: return
    if "current_db_path" in st.session_state and st.session_state.current_db_path == db: return
    if os.path.exists(db):
        df = pd.read_csv(db)
        for c, d in [("主体","未知主体"),("凭证号","无"),("年份_提取","无")]:
            if c not in df.columns: df[c] = d
        df["年份_提取"] = df["年份_提取"].astype(str)
        st.session_state.master_df = df
    else:
        st.session_state.master_df = pd.DataFrame()
    st.session_state.current_db_path = db


def _import_ui(db, cfg):
    ui_section("📥", "任务清单导入", "Import & Manage")
    c1, c2 = st.columns([3, 1])
    with c1:
        up = st.file_uploader("导入 Excel 抽样清单", type=["xlsx"],
                              accept_multiple_files=True, label_visibility="collapsed")
        if st.button("🚀 开始解析并导入", use_container_width=True, type="primary") and up:
            rows, errs = parse_excel(up)
            for e in errs: st.error(e)
            if rows:
                comb = pd.DataFrame(rows)
                st.session_state.master_df = pd.concat(
                    [st.session_state.master_df, comb]).drop_duplicates(subset=["UID"], keep="last")
                if db:
                    os.makedirs(os.path.dirname(db), exist_ok=True)
                    st.session_state.master_df.to_csv(db, index=False, encoding="utf-8-sig")
                for f in up:
                    if f.name not in st.session_state.imported_files:
                        st.session_state.imported_files.append(f.name)
                cfg.imported_files_list = st.session_state.imported_files
                cfg.last_root = st.session_state.root_path; cfg.save(); st.rerun()

    with c2:
        with st.expander("📊 已上传记录", expanded=True):
            if st.session_state.imported_files:
                for fn in st.session_state.imported_files:
                    st.markdown(f'<div class="file-rec">📄 {fn}</div>', unsafe_allow_html=True)
            else:
                st.caption("暂无记录")
            if st.button("🗑️ 清空数据", use_container_width=True):
                if db and os.path.exists(db): os.remove(db)
                st.session_state.master_df = pd.DataFrame()
                st.session_state.imported_files = []
                cfg.imported_files_list = []; cfg.save(); st.rerun()


def _workspace(db, cfg):
    bd = st.session_state.get("base_dir", "")
    ib = st.session_state.get("inbox_dir", "")
    pn = st.session_state.get("p_name", "")
    dup = st.session_state.get("dup_strategy", "跳过")
    master = st.session_state.master_df

    # 筛选器
    ui_section("🔍", "筛选与实时进度", "Filter & Live Progress")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        sy = st.multiselect("📅 年份", sorted(master["年份_提取"].unique()),
                             default=sorted(master["年份_提取"].unique()))
    with fc2:
        se = st.multiselect("🏢 主体", sorted(master["主体"].unique()),
                             default=sorted(master["主体"].unique()))
    with fc3:
        sc = st.multiselect("🗂️ 科目", sorted(master["所属分类"].unique()),
                             default=sorted(master["所属分类"].unique()))

    fdf = master[master["年份_提取"].isin(sy) & master["主体"].isin(se) & master["所属分类"].isin(sc)].copy()
    fdf = check_status(fdf, bd)

    t = len(fdf); d = (fdf["状态"]=="✅ 已收到").sum(); g = t-d
    pct = d/t*100 if t else 0

    ui_kpis(t, d, g, pct)
    ui_progress(pct, d, t)

    # 归档
    if st.button("🚀 开始智能归档", use_container_width=True, type="primary"):
        with st.status("正在执行深度匹配与归档…", expanded=True):
            stats = run_archive(ib, bd, fdf, dup)
        st.session_state.last_stats = {"success": stats.success, "log": stats.log}
        st.rerun()

    if "last_stats" in st.session_state:
        log = st.session_state.last_stats.get("log", [])
        if log:
            with st.expander(f"📝 归档日志 — 成功 {st.session_state.last_stats['success']} 项", expanded=True):
                st.code("\n".join(log))

    # 明细清单
    ui_section("📋", "核查明细清单", "Detail Checklist")
    fdf["sort_idx"] = fdf["样本文件命名"].apply(get_sort_key)
    fdf = fdf.sort_values(by=["年份_提取","所属分类","sort_idx"])
    cols = ["状态","主体","凭证号","业务日期","所属分类","样本文件命名"]

    ct, ca = st.columns([4, 1])
    with ct:
        try:
            sel = st.dataframe(fdf[cols], use_container_width=True, hide_index=True,
                               on_select="rerun", selection_mode="multi-row")
        except TypeError:
            st.dataframe(fdf[cols], use_container_width=True, hide_index=True); sel = None

    with ca:
        st.markdown("**勾选操作**")
        if sel and sel.selection.rows:
            n = len(sel.selection.rows)
            st.info(f"已选中 **{n}** 项")
            row = fdf.iloc[sel.selection.rows[0]]
            tf = os.path.join(bd, f"{row['年份_提取']}年", row["所属分类"])
            if st.button("📂 打开目录", use_container_width=True, type="primary"):
                open_folder(tf)
            if st.button("🗑️ 移除选中", use_container_width=True):
                uids = fdf.iloc[sel.selection.rows]["UID"].tolist()
                st.session_state.master_df = st.session_state.master_df[
                    ~st.session_state.master_df["UID"].isin(uids)]
                if db: st.session_state.master_df.to_csv(db, index=False, encoding="utf-8-sig")
                st.rerun()
        else:
            st.caption("💡 勾选行可操作")

    # 维护
    ui_section("⚙️", "归档库批量维护", "Batch Maintenance")
    bc1, bc2 = st.columns(2)
    with bc1:
        st.markdown("""<div class="mt-card">
            <h4>🗑️ 物理文件清理</h4>
            <p class="desc">按条件永久删除归档库中的物理文件</p>
        </div>""", unsafe_allow_html=True)
        with st.expander("设置删除范围"):
            dy = st.multiselect("年份", sy, key="dy")
            de = st.multiselect("主体", se, key="de")
            ds = st.multiselect("科目", sc, key="ds")
            if st.button("🚨 确认删除", type="primary", use_container_width=True):
                cnt, log = delete_archived(bd, dy, ds, de)
                st.session_state.last_batch_log = log
                st.success(f"已清理 {cnt} 份文件"); st.rerun()

    with bc2:
        st.markdown("""<div class="mt-card">
            <h4>↩️ 归档撤销</h4>
            <p class="desc">将归档文件撤回至待整理目录重新处理</p>
        </div>""", unsafe_allow_html=True)
        with st.expander("设置撤销范围"):
            uy = st.multiselect("年份", sy, key="uy")
            ue = st.multiselect("主体", se, key="ue")
            us = st.multiselect("科目", sc, key="us")
            if st.button("↩️ 批量撤回", use_container_width=True):
                cnt, log = move_back(bd, ib, uy, us, ue)
                st.session_state.last_batch_log = log
                st.success(f"已撤回 {cnt} 份底稿"); st.rerun()

    if "last_batch_log" in st.session_state:
        with st.expander("📋 操作历史"):
            st.code("\n".join(st.session_state.last_batch_log))

    # 导出
    ui_section("📥", "报表导出", "Export Report")
    if st.button("📥 导出筛选汇总 (Excel)", use_container_width=True):
        out = f"核查进度_{pn}_{datetime.now().strftime('%m%d_%H%M')}.xlsx"
        buf = io.BytesIO()
        fdf[cols].to_excel(buf, index=False, engine="openpyxl")
        st.download_button("🚀 点击下载", data=buf.getvalue(), file_name=out, use_container_width=True)

if __name__ == "__main__":
    main()