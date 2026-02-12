import os
script_dir = os.path.dirname(os.path.abspath(__file__))

import importlib
import subprocess
import sys
from pathlib import Path

def install_deps(exec: str, deps:list[str | tuple[str, str]], params: list[str] = [], force=False):
    import importlib, subprocess

    for dep in deps:
        pip_name, import_name = dep if isinstance(dep, tuple) else (dep, dep)
        import_name = import_name.split("==")[0]

        if not force:
            try:
                subprocess.run(
                    [exec, "show", pip_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
                continue
            except subprocess.CalledProcessError:
                pass

            try:
                importlib.import_module(import_name)
                continue
            except ImportError:
                pass

        subprocess.check_call([exec, "install", *params, pip_name])

def git_install(repo, target_dir):
    if os.path.isdir(target_dir) and os.path.isdir(os.path.join(target_dir, ".git")):
        subprocess.check_call(["git", "-C", target_dir, "fetch", "--all"])
        subprocess.check_call(["git", "-C", target_dir, "pull", "--ff-only"])
    else:
        subprocess.check_call(["git", "clone", repo, target_dir])
    return target_dir

def install_repo(repo: str, folder: str, deps: list[str | tuple[str, str]] = []) -> tuple[str, str, str]:
    repo_dir = os.path.join(script_dir, ".apps", folder)
    venv_dir = os.path.join(repo_dir, ".venv")

    venv_python = os.path.join(venv_dir, "bin", "python")
    venv_pip = os.path.join(venv_dir, "bin", "pip")

    # Ensure repo exists
    from package_installer import git_install
    if not os.path.isdir(repo_dir):
        os.makedirs(os.path.dirname(repo_dir), exist_ok=True)
        git_install(repo, repo_dir)

    # Ensure venv exists
    if not os.path.isfile(venv_python): 
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    # Use the venv's site-packages
    venv_site = subprocess.check_output(
        [venv_python, "-c", "import site; print(site.getsitepackages()[0])"],
        text=True
    ).strip()

    return venv_site, repo_dir, venv_pip

def install_requirements(repo_dir):
    venv_dir = os.path.join(repo_dir, ".venv")
    venv_pip = os.path.join(venv_dir, "bin", "pip")
    req_file = os.path.join(repo_dir, "requirements.txt")
    installed_marker = os.path.join(venv_dir, ".requirements_installed")
    if not os.path.isfile(installed_marker):
        subprocess.check_call([venv_pip, "install", "-r", req_file])
        with open(installed_marker, "w") as f:
            f.write("ok\n")


def install_deps_to_default_venv(deps: list[str | tuple[str, str]] = [], params: list[str] = []) -> str:
    venv_dir = os.path.join(script_dir, ".venv")

    venv_python = os.path.join(venv_dir, "bin", "python")
    venv_pip = os.path.join(venv_dir, "bin", "pip")

    # Ensure venv exists
    if not os.path.isfile(venv_python): 
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    # Install deps
    from package_installer import install_deps
    if deps: install_deps(venv_pip, deps, params)

    # Use the venv's site-packages in THIS process (so imports work here too)
    venv_site = subprocess.check_output(
        [venv_python, "-c", "import site; print(site.getsitepackages()[0])"],
        text=True
    ).strip()

    return venv_site