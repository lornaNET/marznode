from typing import Optional, Tuple, Dict, Any
import os
import json
import tempfile
import subprocess
from pathlib import Path
import secrets

import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

# =====================================================
#  مسیر ذخیره تنظیمات نصب
# =====================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
CONFIG_PATH = DATA_DIR / "config.json"

def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text("utf-8"))
        except Exception:
            return {}
    return {}

def save_config(cfg: Dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), "utf-8")

def is_configured() -> bool:
    cfg = load_config()
    needed = ["ui_username", "ui_password", "panel_url", "panel_admin_user", "panel_admin_pass"]
    return all(cfg.get(k) for k in needed)

def get_cfg_value(key: str, default: str = "") -> str:
    cfg = load_config()
    v = (cfg.get(key) or "").strip()
    if v:
        return v
    # اگر config خالی بود، از env هم به عنوان پیش فرض بگیر
    return (os.getenv(key.upper(), default) or default).strip()

# =====================================================
#  FastAPI / Static / Templates
# =====================================================

app = FastAPI()

# سشن برای لاگین UI
SESSION_SECRET = os.getenv("SESSION_SECRET") or secrets.token_hex(32)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# =====================================================
#  مدل SSH فرم قبلی (بدون تغییر)
# =====================================================

class SSHInfo(BaseModel):
    ssh_host: str = ""
    ssh_port: int = 22
    ssh_user: str = "root"
    ssh_password: str = ""
    ssh_node_label: str = ""  # اسم پوشه نود، مثل fr یا TR

# =====================================================
#  تنظیمات پنل مرزنشین (از config خوانده می‌شود)
# =====================================================

MARZ_ADMIN_TOKEN: Optional[str] = None

def panel_url() -> str:
    u = get_cfg_value("panel_url", "https://mypanel.lornanet.ir").rstrip("/")
    return u

def panel_admin_user() -> str:
    return get_cfg_value("panel_admin_user", "")

def panel_admin_pass() -> str:
    return get_cfg_value("panel_admin_pass", "")

# =====================================================
#  Helper: گرفتن توکن ادمین از خود پنل
# =====================================================

def fetch_admin_token() -> str:
    global MARZ_ADMIN_TOKEN

    user = panel_admin_user()
    pw = panel_admin_pass()
    if not user or not pw:
        raise RuntimeError("اطلاعات ادمین پنل داخل Setup ثبت نشده.")

    url = f"{panel_url()}/api/admins/token"

    data = {
        "grant_type": "password",
        "username": user,
        "password": pw,
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    resp = requests.post(url, data=data, headers=headers, timeout=15)
    resp.raise_for_status()
    js = resp.json()
    token = js.get("access_token")
    if not token:
        raise RuntimeError("access_token در پاسخ /api/admins/token پیدا نشد.")

    MARZ_ADMIN_TOKEN = token
    return token

def get_admin_token() -> str:
    global MARZ_ADMIN_TOKEN
    if not MARZ_ADMIN_TOKEN:
        MARZ_ADMIN_TOKEN = fetch_admin_token()
    return MARZ_ADMIN_TOKEN

# =====================================================
#  Helper: تبدیل جواب API به لیست واقعی
# =====================================================

def as_list(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("items", "results", "data"):
            if isinstance(raw.get(key), list):
                return raw[key]
        return []
    return []

# =====================================================
#  توابع درخواست به API مرزنشین
# =====================================================

def _headers() -> dict:
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {get_admin_token()}",
    }

def marz_get(path: str):
    url = f"{panel_url()}{path}"
    resp = requests.get(url, headers=_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()

def marz_post(path: str, data: dict):
    url = f"{panel_url()}{path}"
    resp = requests.post(url, json=data, headers=_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()

def marz_put(path: str, data: dict):
    url = f"{panel_url()}{path}"
    resp = requests.put(url, json=data, headers=_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()

def marz_delete(path: str):
    url = f"{panel_url()}{path}"
    resp = requests.delete(url, headers=_headers(), timeout=15)
    resp.raise_for_status()
    return True

# =====================================================
#  Auth UI (لاگین خود UI)
# =====================================================

def is_logged_in(request: Request) -> bool:
    return bool(request.session.get("ui_logged_in"))

def require_login(request: Request):
    if not is_configured():
        return RedirectResponse("/setup", status_code=303)
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)
    return None

# =====================================================
#  Setup Wizard
# =====================================================

@app.get("/setup", response_class=HTMLResponse)
async def setup_get(request: Request):
    # اگر قبلاً تنظیم شده، برو لاگین
    if is_configured():
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse("setup.html", {
        "request": request,
        "default_panel_url": os.getenv("MARZ_PANEL_URL", "https://mypanel.lornanet.ir")
    })

@app.post("/setup")
async def setup_post(
    request: Request,
    ui_username: str = Form(...),
    ui_password: str = Form(...),
    panel_url_in: str = Form(...),
    panel_admin_user_in: str = Form(...),
    panel_admin_pass_in: str = Form(...),
):
    cfg = {
        "ui_username": ui_username.strip(),
        "ui_password": ui_password.strip(),
        "panel_url": panel_url_in.strip().rstrip("/"),
        "panel_admin_user": panel_admin_user_in.strip(),
        "panel_admin_pass": panel_admin_pass_in.strip(),
    }

    save_config(cfg)
    return RedirectResponse("/login", status_code=303)

# =====================================================
#  Login UI
# =====================================================

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    if not is_configured():
        return RedirectResponse("/setup", status_code=303)
    if is_logged_in(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    cfg = load_config()
    if username.strip() == cfg.get("ui_username") and password.strip() == cfg.get("ui_password"):
        request.session["ui_logged_in"] = True
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("login.html", {"request": request, "error": "یوزرنیم یا پسورد اشتباهه"})

@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

# =====================================================
#  SSH / Xray Helperها (همون قبلی)
# =====================================================

BASE_NODE_DIR = "/opt/marznode"   # /opt/marznode/<label>

def build_paths(label: str) -> Tuple[str, str, str]:
    label_clean = (label or "").strip()
    if not label_clean:
        raise ValueError("label نود خالی است.")

    node_dir = f"{BASE_NODE_DIR}/{label_clean}"
    config_path = f"{node_dir}/xray/config.json"
    docker_compose = f"{node_dir}/docker-compose.yml"
    return node_dir, config_path, docker_compose

def run_ssh_command(host: str, port: int, user: str, password: str, command: str) -> str:
    try:
        cmd = [
            "sshpass", "-p", password,
            "ssh",
            "-p", str(port),
            "-o", "StrictHostKeyChecking=no",
            f"{user}@{host}",
            command,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError("sshpass نصب نیست:\napt install -y sshpass")

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or f"SSH exit code {proc.returncode}")
    return proc.stdout

def scp_write_file(host: str, port: int, user: str, password: str,
                   local_path: str, remote_path: str) -> None:
    try:
        cmd = [
            "sshpass", "-p", password,
            "scp",
            "-P", str(port),
            "-o", "StrictHostKeyChecking=no",
            local_path,
            f"{user}@{host}:{remote_path}",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError("sshpass نصب نیست:\napt install -y sshpass")

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or f"SCP exit code {proc.returncode}")

# =====================================================
#  رندر صفحه اصلی (UI قبلی)
# =====================================================

def render_index(
    request: Request,
    node_id: Optional[str] = None,
    ssh_info: Optional[SSHInfo] = None,
    ssh_json: str = "",
    ssh_error: Optional[str] = None,
):
    if ssh_info is None:
        ssh_info = SSHInfo()

    nodes = []
    hosts = []
    nodes_error = None
    hosts_error = None
    selected_node = None

    # نودها
    try:
        raw_nodes = marz_get("/api/nodes")
        all_nodes = as_list(raw_nodes)

        nodes = []
        for n in all_nodes:
            if not isinstance(n, dict):
                continue
            # ✅ اینجا دیگه دیسبل‌ها رو حذف نمی‌کنیم که تو UI دیده بشن
            nodes.append(n)
    except Exception as e:
        nodes_error = str(e)
        nodes = []

    # هاست‌ها
    try:
        raw_hosts = marz_get("/api/inbounds/hosts")
        hosts = as_list(raw_hosts)
    except Exception as e:
        hosts_error = str(e)
        hosts = []

    # جزییات نود انتخاب‌شده
    if node_id:
        try:
            node_int = int(node_id)
            selected_node = marz_get(f"/api/nodes/{node_int}")
        except Exception:
            selected_node = None

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "server_url": panel_url(),
            "nodes": nodes,
            "hosts": hosts,
            "nodes_error": nodes_error,
            "hosts_error": hosts_error,
            "selected_node": selected_node,
            "ssh_info": ssh_info,
            "ssh_json": ssh_json,
            "ssh_error": ssh_error,
        },
    )

# =====================================================
#  صفحه اصلی
# =====================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, node_id: Optional[str] = None):
    redir = require_login(request)
    if redir:
        return redir
    return render_index(request, node_id=node_id)

# =====================================================
#  نودها: ایجاد / ویرایش / Soft Delete
# =====================================================

@app.post("/nodes/create")
async def create_node(request: Request, name: str = Form(...), address: str = Form(...), port: int = Form(...)):
    redir = require_login(request)
    if redir:
        return redir

    payload = {
        "name": name,
        "address": address,
        "port": port,
        "connection_backend": "grpclib",
        "usage_coefficient": 1,
    }

    try:
        marz_post("/api/nodes", payload)
    except Exception as e:
        print("Error creating node:", e)

    return RedirectResponse(url="/", status_code=303)

@app.post("/nodes/{node_id}/update")
async def update_node(request: Request, node_id: int, name: str = Form(...), address: str = Form(...), port: int = Form(...)):
    redir = require_login(request)
    if redir:
        return redir

    try:
        current = marz_get(f"/api/nodes/{node_id}")
    except Exception as e:
        print("Error fetching node before update:", e)
        current = {}

    if isinstance(current, dict):
        current["name"] = name
        current["address"] = address
        current["port"] = port

        for ro in ["id", "status", "message", "usage", "created_at", "updated_at"]:
            current.pop(ro, None)

        try:
            marz_put(f"/api/nodes/{node_id}", current)
        except Exception as e:
            print("Error updating node:", e)

    return RedirectResponse(url=f"/?node_id={node_id}", status_code=303)

def random_disabled_ip(used: set) -> str:
    # رندوم تو بازه 127.0.0.1 تا 127.0.0.254 که تکراری نشه
    for i in range(1, 255):
        ip = f"127.0.0.{i}"
        if ip not in used:
            return ip
    return "127.0.0.254"

@app.post("/nodes/{node_id}/soft-delete")
async def soft_delete_node(request: Request, node_id: int):
    redir = require_login(request)
    if redir:
        return redir

    # گرفتن همه نودها برای پیدا کردن IP های دیسبل‌شده
    try:
        all_nodes = as_list(marz_get("/api/nodes"))
    except Exception:
        all_nodes = []

    used_ips = set()
    for n in all_nodes:
        if isinstance(n, dict):
            addr = str(n.get("address", ""))
            if addr.startswith("127.0.0."):
                used_ips.add(addr)

    try:
        current = marz_get(f"/api/nodes/{node_id}")
    except Exception as e:
        print("Error fetching node for soft delete:", e)
        return RedirectResponse(url="/", status_code=303)

    if not isinstance(current, dict):
        return RedirectResponse(url="/", status_code=303)

    old_name = str(current.get("name", f"node-{node_id}"))
    if old_name.startswith("[DISABLED]"):
        new_name = old_name
    else:
        new_name = f"[DISABLED] {old_name}"

    backend = current.get("connection_backend", "grpclib")

    payload = {
        "name": new_name,
        "address": random_disabled_ip(used_ips),
        "port": 0,
        "connection_backend": backend,
        "usage_coefficient": 0,
    }

    try:
        marz_put(f"/api/nodes/{node_id}", payload)
    except Exception as e:
        print("Error soft-deleting node:", e)

    return RedirectResponse(url="/", status_code=303)

# =====================================================
#  هاست‌ها: ویرایش / حذف
# =====================================================

@app.post("/hosts/{host_id}/update")
async def update_host(request: Request, host_id: int, address: str = Form(...), port: int = Form(...), weight: int = Form(...)):
    redir = require_login(request)
    if redir:
        return redir

    try:
        current = marz_get(f"/api/inbounds/hosts/{host_id}")
    except Exception as e:
        print("Error fetching host before update:", e)
        current = {}

    if isinstance(current, dict):
        current["address"] = address
        current["port"] = port

        if "weight" in current:
            current["weight"] = weight
        else:
            current["usage_ratio"] = weight

        current.pop("id", None)

        try:
            marz_put(f"/api/inbounds/hosts/{host_id}", current)
        except Exception as e:
            print("Error updating host:", e)

    return RedirectResponse(url="/", status_code=303)

@app.post("/hosts/{host_id}/delete")
async def delete_host(request: Request, host_id: int):
    redir = require_login(request)
    if redir:
        return redir

    try:
        marz_delete(f"/api/inbounds/hosts/{host_id}")
    except Exception as e:
        print("Error deleting host:", e)

    return RedirectResponse(url="/", status_code=303)

# =====================================================
#  SSH / Xray: خواندن / ذخیره / OFF / ON (همون قبلی)
# =====================================================

def sshinfo_from_form(**data) -> SSHInfo:
    return SSHInfo(
        ssh_host=data.get("ssh_host", ""),
        ssh_port=int(data.get("ssh_port", 22) or 22),
        ssh_user=data.get("ssh_user", "root") or "root",
        ssh_password=data.get("ssh_password", ""),
        ssh_node_label=data.get("ssh_node_label", ""),
    )

@app.post("/ssh/load-config")
async def ssh_load_config(
    request: Request,
    ssh_host: str = Form(...),
    ssh_port: int = Form(...),
    ssh_user: str = Form(...),
    ssh_password: str = Form(...),
    ssh_node_label: str = Form(...),
    node_id: Optional[str] = Form(None),
):
    redir = require_login(request)
    if redir:
        return redir

    ssh_info = sshinfo_from_form(
        ssh_host=ssh_host,
        ssh_port=ssh_port,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_node_label=ssh_node_label,
    )

    ssh_json = ""
    ssh_error: Optional[str] = None

    try:
        node_dir, config_path, _ = build_paths(ssh_info.ssh_node_label)
        cmd = f"cat '{config_path}'"
        output = run_ssh_command(
            host=ssh_info.ssh_host,
            port=ssh_info.ssh_port,
            user=ssh_info.ssh_user,
            password=ssh_info.ssh_password,
            command=cmd,
        )
        try:
            parsed = json.loads(output)
            ssh_json = json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception:
            ssh_json = output.strip()
    except Exception as e:
        ssh_error = str(e)

    return render_index(request, node_id=node_id, ssh_info=ssh_info, ssh_json=ssh_json, ssh_error=ssh_error)

@app.post("/ssh/save-config")
async def ssh_save_config(
    request: Request,
    ssh_host: str = Form(...),
    ssh_port: int = Form(...),
    ssh_user: str = Form(...),
    ssh_password: str = Form(...),
    ssh_node_label: str = Form(...),
    ssh_config_json: str = Form(...),
    node_id: Optional[str] = Form(None),
):
    redir = require_login(request)
    if redir:
        return redir

    ssh_info = sshinfo_from_form(
        ssh_host=ssh_host,
        ssh_port=ssh_port,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_node_label=ssh_node_label,
    )

    ssh_error: Optional[str] = None
    ssh_json = ssh_config_json

    try:
        node_dir, config_path, docker_compose = build_paths(ssh_info.ssh_node_label)

        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp.write(ssh_config_json)
            tmp_path = tmp.name

        scp_write_file(
            host=ssh_info.ssh_host,
            port=ssh_info.ssh_port,
            user=ssh_info.ssh_user,
            password=ssh_info.ssh_password,
            local_path=tmp_path,
            remote_path=config_path,
        )

        docker_cmd = (
            f"cd '{node_dir}' && "
            f"docker compose -f '{docker_compose}' down && "
            f"docker compose -f '{docker_compose}' up -d"
        )
        run_ssh_command(
            host=ssh_info.ssh_host,
            port=ssh_info.ssh_port,
            user=ssh_info.ssh_user,
            password=ssh_info.ssh_password,
            command=docker_cmd,
        )

    except Exception as e:
        ssh_error = str(e)

    return render_index(request, node_id=node_id, ssh_info=ssh_info, ssh_json=ssh_json, ssh_error=ssh_error)

@app.post("/ssh/node-off")
async def ssh_node_off(
    request: Request,
    ssh_host: str = Form(...),
    ssh_port: int = Form(...),
    ssh_user: str = Form(...),
    ssh_password: str = Form(...),
    ssh_node_label: str = Form(...),
    node_id: Optional[str] = Form(None),
):
    redir = require_login(request)
    if redir:
        return redir

    ssh_info = sshinfo_from_form(
        ssh_host=ssh_host,
        ssh_port=ssh_port,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_node_label=ssh_node_label,
    )

    ssh_error: Optional[str] = None

    try:
        node_dir, _, docker_compose = build_paths(ssh_info.ssh_node_label)
        docker_cmd = f"cd '{node_dir}' && docker compose -f '{docker_compose}' down"
        run_ssh_command(
            host=ssh_info.ssh_host,
            port=ssh_info.ssh_port,
            user=ssh_info.ssh_user,
            password=ssh_info.ssh_password,
            command=docker_cmd,
        )
    except Exception as e:
        ssh_error = str(e)

    return render_index(request, node_id=node_id, ssh_info=ssh_info, ssh_json="", ssh_error=ssh_error)

@app.post("/ssh/node-on")
async def ssh_node_on(
    request: Request,
    ssh_host: str = Form(...),
    ssh_port: int = Form(...),
    ssh_user: str = Form(...),
    ssh_password: str = Form(...),
    ssh_node_label: str = Form(...),
    node_id: Optional[str] = Form(None),
):
    redir = require_login(request)
    if redir:
        return redir

    ssh_info = sshinfo_from_form(
        ssh_host=ssh_host,
        ssh_port=ssh_port,
        ssh_user=ssh_user,
        ssh_password=ssh_password,
        ssh_node_label=ssh_node_label,
    )

    ssh_error: Optional[str] = None

    try:
        node_dir, _, docker_compose = build_paths(ssh_info.ssh_node_label)
        docker_cmd = f"cd '{node_dir}' && docker compose -f '{docker_compose}' up -d"
        run_ssh_command(
            host=ssh_info.ssh_host,
            port=ssh_info.ssh_port,
            user=ssh_info.ssh_user,
            password=ssh_info.ssh_password,
            command=docker_cmd,
        )
    except Exception as e:
        ssh_error = str(e)

    return render_index(request, node_id=node_id, ssh_info=ssh_info, ssh_json="", ssh_error=ssh_error)