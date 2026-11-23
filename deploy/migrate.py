#!/usr/bin/env python3
"""InfinityLearn 迁移 / 还原工具（macOS 与 Windows 通用，只依赖 Python 3.10+ 标准库）。

用法：
  python migrate.py export  [-o out.zip] [--venv DIR]
      打包「代码 + 配置 + 数据库数据」成一个 zip。

  python migrate.py restore <backup.zip> --target <目录> [选项]
  python migrate.py restore --here --target <目录> [选项]
      在新机器上还原。--here 表示当前目录就是解压后的迁移包。
      选项：--venv DIR  --skip-frontend  --skip-db  --keep-env  --install-service

  python migrate.py verify <backup.zip>     # 检查迁移包内容
  python migrate.py info                    # 显示当前环境信息

还原完成后会自动安装依赖、建库、导入数据，并可配置开机自启。
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

IS_WIN = os.name == "nt"
IS_MAC = sys.platform == "darwin"


def log(msg: str) -> None:
    print(f"[migrate] {msg}", flush=True)


def venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if IS_WIN else "bin/python")


def default_target() -> Path:
    return Path.home() / "Projects" / "InfinityLearn"


def default_venv(target: Path) -> Path:
    # macOS 的 Desktop/Documents 受 TCC 隐私保护，launchd 无法读取其中的 venv，
    # 因此默认放到 ~/.venvs 下；Windows 无此限制，放在项目内。
    if IS_MAC:
        return Path.home() / ".venvs" / "il-backend"
    return target / "backend" / ".venv"


def project_root() -> Path:
    """仓库布局下 migrate.py 位于 deploy/，项目根是其父目录。"""
    here = Path(__file__).resolve().parent
    if (here / "backend").exists():
        return here
    return here.parent


# ---------------------------------------------------------------------------
# 环境准备
# ---------------------------------------------------------------------------
def ensure_venv(venv: Path, requirements: Path) -> Path:
    py = venv_python(venv)
    if not py.exists():
        log(f"创建虚拟环境：{venv}")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv)])
    log("安装后端依赖（首次较慢）…")
    subprocess.check_call([str(py), "-m", "pip", "install", "--upgrade", "pip", "-q"])
    subprocess.check_call([str(py), "-m", "pip", "install", "-q", "-r", str(requirements)])
    return py


def run_internal(py: Path, command: str, extra: list[str]) -> None:
    """用 venv 里的解释器重新执行本脚本的隐藏子命令（此时依赖已就绪）。"""
    subprocess.check_call([str(py), str(Path(__file__).resolve()), command, *extra])


def npm_install(frontend: Path) -> None:
    npm = shutil.which("npm")
    if not npm:
        log("未找到 npm，跳过前端依赖安装；请手动执行 npm install")
        return
    log(f"安装前端依赖：{frontend}")
    subprocess.check_call(
        [npm, "install"], cwd=str(frontend), shell=IS_WIN
    )


# ---------------------------------------------------------------------------
# 导出
# ---------------------------------------------------------------------------
def cmd_export(args) -> int:
    root = project_root()
    backend = root / "backend"
    requirements = backend / "requirements.txt"
    if not requirements.exists():
        log(f"找不到 {requirements}")
        return 1

    venv = Path(args.venv).expanduser() if args.venv else default_venv(root)
    py = ensure_venv(venv, requirements)

    out = Path(
        args.output or f"infinitylearn-migration-{datetime.now():%Y%m%d-%H%M%S}.zip"
    ).expanduser().resolve()

    log("导出数据库并打包…")
    run_internal(py, "_export", ["--out", str(out), "--backend", str(backend)])

    size = out.stat().st_size / 1024 / 1024
    log(f"完成：{out}（{size:.1f} MB）")
    log("把这一个 zip 拷到新机器，解压后运行 restore.sh / restore.bat 即可。")
    return 0


def internal_export(out: str, backend: str) -> int:
    sys.path.insert(0, backend)
    import asyncio

    from app.services.backup import build_migration_zip, dump_database

    payload = asyncio.run(dump_database())
    data = build_migration_zip(payload)
    Path(out).write_bytes(data)
    counts = {k: len(v) for k, v in payload["tables"].items()}
    log(f"数据导出完成：{counts}")
    return 0


# ---------------------------------------------------------------------------
# 还原
# ---------------------------------------------------------------------------
def _load_package(args) -> Path:
    """返回解压后的迁移包目录（--here 直接用当前目录）。"""
    if args.here:
        pkg = Path.cwd()
        if not (pkg / "manifest.json").exists():
            raise SystemExit("当前目录不是迁移包（缺少 manifest.json）")
        return pkg

    zip_path = Path(args.archive).expanduser().resolve()
    if not zip_path.exists():
        raise SystemExit(f"找不到迁移包：{zip_path}")
    tmp = Path(tempfile.mkdtemp(prefix="il-restore-")) / "pkg"
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(tmp)
    if not (tmp / "manifest.json").exists():
        raise SystemExit("迁移包损坏：缺少 manifest.json")
    return tmp


def cmd_restore(args) -> int:
    pkg = _load_package(args)
    manifest = json.loads((pkg / "manifest.json").read_text(encoding="utf-8"))
    log(f"迁移包信息：应用 v{manifest.get('app_version')}，创建于 {manifest.get('created_at')}")
    log(f"包含数据表：{manifest.get('tables')}")

    target = Path(args.target).expanduser().resolve()
    code_src = pkg / "code"

    # 1) 还原代码
    if code_src.exists():
        target.mkdir(parents=True, exist_ok=True)
        log(f"还原代码到：{target}")
        shutil.copytree(code_src, target, dirs_exist_ok=True)
        if not args.keep_env and (target / "backend" / ".env").exists():
            log("已写入 backend/.env（来自迁移包）")
    else:
        log("迁移包内没有 code/ 目录，仅还原数据")

    backend = target / "backend"
    requirements = backend / "requirements.txt"
    if not requirements.exists():
        log(f"找不到 {requirements}，无法继续")
        return 1

    # 2) 数据库
    if not args.skip_db:
        data_file = pkg / "db" / "data.json"
        if not data_file.exists():
            log("迁移包内没有 db/data.json，跳过数据还原")
        else:
            venv = Path(args.venv).expanduser() if args.venv else default_venv(target)
            py = ensure_venv(venv, requirements)
            log("建库并导入数据…")
            run_internal(
                py,
                "_db_import",
                ["--data", str(data_file), "--backend", str(backend)],
            )
            # 3) 前端依赖
            if not args.skip_frontend:
                npm_install(target / "frontend")
            # 4) 开机自启
            if args.install_service:
                _install_service(target, venv)
        return _print_next_steps(target, args)

    # skip_db 分支也需要打印后续步骤
    return _print_next_steps(target, args)


def internal_db_import(data: str, backend: str) -> int:
    sys.path.insert(0, backend)
    import asyncio

    from app.services.backup import ensure_database_exists, restore_database

    payload = json.loads(Path(data).read_text(encoding="utf-8"))
    created = asyncio.run(ensure_database_exists())
    if created:
        log("数据库不存在，已自动创建")
    counts = asyncio.run(restore_database(payload))
    log(f"数据还原完成：{counts}")
    return 0


def _print_next_steps(target: Path, args) -> int:
    log("=" * 60)
    log("还原完成。启动方式：")
    if IS_MAC:
        log(f"  cd {target}/backend && {default_venv(target)}/bin/python3 -m uvicorn app.main:app --port 8010")
        log(f"  cd {target}/frontend && npm run dev")
        if not args.install_service:
            log("  如需开机自启：重新执行并加 --install-service")
    elif IS_WIN:
        log(f'  "{venv_python(default_venv(target))}" -m uvicorn app.main:app --port 8010')
        log("  或双击项目目录下生成的 start_backend.bat / start_frontend.bat")
    else:
        log(f"  cd {target}/backend && python -m uvicorn app.main:app --port 8010")
    log("注意：backend/.env 中的数据库账号密码需与本机一致，必要时修改后重启。")
    log("=" * 60)
    return 0


# ---------------------------------------------------------------------------
# 开机自启
# ---------------------------------------------------------------------------
def _install_service(target: Path, venv: Path) -> None:
    if IS_MAC:
        _install_launchd(target, venv)
    elif IS_WIN:
        _install_windows_startup(target, venv)
    else:
        log("当前系统暂不支持自动配置自启，请手动启动。")


def _install_launchd(target: Path, venv: Path) -> None:
    backend = target / "backend"
    frontend = target / "frontend"
    py = venv_python(venv)

    be_sh = venv / "start_backend.sh"
    be_sh.write_text(
        "#!/bin/bash\n"
        "set -e\n"
        f'cd "{backend}"\n'
        'export PYTHONUNBUFFERED=1\n'
        'export PATH="$(dirname "$0")/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"\n'
        f'exec "{py}" -m uvicorn app.main:app --host 127.0.0.1 --port 8010\n',
        encoding="utf-8",
    )
    fe_sh = venv / "start_frontend.sh"
    fe_sh.write_text(
        "#!/bin/bash\n"
        "set -e\n"
        f'cd "{frontend}"\n'
        'export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"\n'
        'export BACKEND_PORT=8010\n'
        f'exec "{shutil.which("node") or "/usr/local/bin/node"}" node_modules/vite/bin/vite.js --host\n',
        encoding="utf-8",
    )
    for f in (be_sh, fe_sh):
        f.chmod(0o755)

    agents = Path.home() / "Library" / "LaunchAgents"
    agents.mkdir(parents=True, exist_ok=True)

    def plist(label, script, workdir, out_log, err_log):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
    <key>Label</key><string>{label}</string>
    <key>ProgramArguments</key><array>
        <string>/bin/bash</string><string>{script}</string>
    </array>
    <key>WorkingDirectory</key><string>{workdir}</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><dict>
        <key>Crashed</key><true/><key>SuccessfulExit</key><false/>
    </dict>
    <key>ThrottleInterval</key><integer>5</integer>
    <key>EnvironmentVariables</key><dict>
        <key>HOME</key><string>{Path.home()}</string>
        <key>PYTHONUNBUFFERED</key><string>1</string>
    </dict>
    <key>StandardOutPath</key><string>{out_log}</string>
    <key>StandardErrorPath</key><string>{err_log}</string>
</dict></plist>
"""

    pairs = [
        ("com.infinitylearn.backend", be_sh, backend, "/tmp/il-backend.out.log", "/tmp/il-backend.err.log"),
        ("com.infinitylearn.frontend", fe_sh, frontend, "/tmp/il-frontend.out.log", "/tmp/il-frontend.err.log"),
    ]
    uid = os.getuid()
    for label, script, workdir, out_log, err_log in pairs:
        path = agents / f"{label}.plist"
        path.write_text(plist(label, script, workdir, out_log, err_log), encoding="utf-8")
        subprocess.run(["launchctl", "bootout", f"gui/{uid}/{label}"], capture_output=True)
        subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(path)], capture_output=True)
        log(f"已安装开机自启：{label}")


def _install_windows_startup(target: Path, venv: Path) -> None:
    py = venv_python(venv)
    be_bat = target / "start_backend.bat"
    be_bat.write_text(
        "@echo off\r\n"
        f'cd /d "{target / "backend"}"\r\n'
        f'"{py}" -m uvicorn app.main:app --host 127.0.0.1 --port 8010\r\n'
        "pause\r\n",
        encoding="utf-8",
    )
    fe_bat = target / "start_frontend.bat"
    fe_bat.write_text(
        "@echo off\r\n"
        f'cd /d "{target / "frontend"}"\r\n'
        "set BACKEND_PORT=8010\r\n"
        "npm run dev\r\n"
        "pause\r\n",
        encoding="utf-8",
    )
    log("已生成 start_backend.bat / start_frontend.bat")

    for name, bat in (("InfinityLearn-Backend", be_bat), ("InfinityLearn-Frontend", fe_bat)):
        cmd = [
            "schtasks", "/Create", "/F", "/SC", "ONLOGON",
            "/TN", name, "/TR", f'"{bat}"',
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            log(f"已注册开机启动任务：{name}")
        except Exception as e:
            log(f"注册计划任务失败（可稍后手动以管理员运行）：{e}")


# ---------------------------------------------------------------------------
# 校验 / 信息
# ---------------------------------------------------------------------------
def cmd_verify(args) -> int:
    zip_path = Path(args.archive).expanduser().resolve()
    if not zip_path.exists():
        log(f"找不到文件：{zip_path}")
        return 1
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        if "manifest.json" not in names:
            log("无效：缺少 manifest.json")
            return 1
        manifest = json.loads(zf.read("manifest.json"))
        log(f"应用版本：{manifest.get('app_version')}")
        log(f"创建时间：{manifest.get('created_at')}")
        log(f"数据表行数：{manifest.get('tables')}")
        log(f"文件总数：{len(names)}")
        for required in ("db/data.json", "migrate.py", "restore.sh"):
            log(f"  {'OK ' if required in names else '缺失'} {required}")
        code_files = [n for n in names if n.startswith("code/")]
        log(f"代码文件：{len(code_files)} 个")
    return 0


def cmd_info(args) -> int:
    root = project_root()
    target = Path(args.target).expanduser() if args.target else default_target()
    venv = default_venv(target)
    log(f"系统：{platform.system()} {platform.release()} / {platform.machine()}")
    log(f"Python：{sys.version.split()[0]}（{sys.executable}）")
    log(f"项目根：{root}")
    log(f"还原目标：{target}")
    log(f"venv 路径：{venv} → {'已存在' if venv.exists() else '不存在'}")
    log(f"npm：{shutil.which('npm') or '未安装'}")
    return 0


# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        prog="migrate.py", description="InfinityLearn 迁移 / 还原工具"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_exp = sub.add_parser("export", help="打包代码+配置+数据库")
    p_exp.add_argument("-o", "--output", help="输出 zip 路径")
    p_exp.add_argument("--venv", help="使用的虚拟环境目录")
    p_exp.set_defaults(func=cmd_export)

    p_res = sub.add_parser("restore", help="从迁移包还原")
    p_res.add_argument("archive", nargs="?", help="迁移包 zip 路径")
    p_res.add_argument("--here", action="store_true", help="当前目录即解压后的迁移包")
    p_res.add_argument("--target", default=str(default_target()), help="还原目标目录")
    p_res.add_argument("--venv", help="虚拟环境目录")
    p_res.add_argument("--skip-frontend", action="store_true", help="跳过 npm install")
    p_res.add_argument("--skip-db", action="store_true", help="只还原代码，不导入数据")
    p_res.add_argument("--keep-env", action="store_true", help="保留目标已有的 .env")
    p_res.add_argument("--install-service", action="store_true", help="配置开机自启")
    p_res.set_defaults(func=cmd_restore)

    p_ver = sub.add_parser("verify", help="检查迁移包")
    p_ver.add_argument("archive")
    p_ver.set_defaults(func=cmd_verify)

    p_info = sub.add_parser("info", help="显示环境信息")
    p_info.add_argument("--target")
    p_info.set_defaults(func=cmd_info)

    # 隐藏子命令（由 venv 解释器内部调用）
    p_ie = sub.add_parser("_export")
    p_ie.add_argument("--out", required=True)
    p_ie.add_argument("--backend", required=True)
    p_ie.set_defaults(func=lambda a: internal_export(a.out, a.backend))

    p_ii = sub.add_parser("_db_import")
    p_ii.add_argument("--data", required=True)
    p_ii.add_argument("--backend", required=True)
    p_ii.set_defaults(func=lambda a: internal_db_import(a.data, a.backend))

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
