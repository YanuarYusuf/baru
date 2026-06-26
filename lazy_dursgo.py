import argparse
import subprocess
import os
import sys
import re

def update_repo(repo_dir, remote_url, branch="main"):
    print(f"[*] Updating {repo_dir} from {remote_url}...")
    
    repo_path = os.path.abspath(repo_dir)
    
    if not os.path.exists(repo_path):
        print(f"[*] Directory not found, cloning {remote_url} into {repo_path}...")
        try:
            subprocess.run(["git", "clone", remote_url, repo_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to clone {remote_url}: {e}")
        return

    git_dir = os.path.join(repo_path, ".git")
    if not os.path.exists(git_dir):
        print(f"[*] Initializing git in {repo_path}...")
        try:
            subprocess.run(["git", "init"], cwd=repo_path, check=True)
            subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=repo_path, check=True)
            subprocess.run(["git", "fetch", "--all"], cwd=repo_path, check=True)
            subprocess.run(["git", "checkout", "-f", f"origin/{branch}"], cwd=repo_path, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to pull latest for {repo_path}: {e}")
            return
    else:
        try:
            subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=repo_path, check=True)
            subprocess.run(["git", "pull", "origin", branch], cwd=repo_path, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to pull latest for {repo_path}: {e}")

def update_all_tools():
    print("[*] Starting update for all tools...")
    
    # lazyhunter
    update_repo("lazyhunter-main", "https://github.com/YanuarYusuf/lazyhunter.git")
    
    # dursgo
    update_repo("dursgo-main", "https://github.com/YanuarYusuf/DursGo.git")
    
    # xsscanner
    xsscanner_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".", "cloned_repos", "xsscanner")
    update_repo(xsscanner_dir, "https://github.com/YanuarYusuf/xsscanner.git")
    
    # claude-bug-bounty
    cbb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".", "cloned_repos", "claude-bug-bounty")
    update_repo(cbb_dir, "https://github.com/shuvonsec/claude-bug-bounty.git")
    
    # ds_store_exp
    ds_store_exp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".", "cloned_repos", "ds_store_exp")
    update_repo(ds_store_exp_dir, "https://github.com/YanuarYusuf/ds_store_exp.git", branch="master")
    

    
    # nuclei-templates
    nuclei_tpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".", "cloned_repos", "nuclei-templates")
    update_repo(nuclei_tpl_dir, "https://github.com/projectdiscovery/nuclei-templates.git")
    
    print("\n[*] All tools and templates updated successfully! Exiting.")
    sys.exit(0)

def update_dursgo_config(cookie, deepseek_key):
    config_path = os.path.join("dursgo-main", "config.yaml")
    if not os.path.exists(config_path):
        print(f"[!] Warning: {config_path} not found. Cannot update config.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config_content = f.read()

    changed = False

    if cookie:
        # Replace the first uncommented cookie
        new_content = re.sub(r'\n(\s*)cookie:\s*".*?"', f'\n\\1cookie: "{cookie}"', config_content, count=1)
        if new_content == config_content:
            # If no uncommented cookie, replace the first commented one and uncomment it
            new_content = re.sub(r'\n\s*#\s*cookie:\s*".*?"', f'\n  cookie: "{cookie}"', config_content, count=1)
        config_content = new_content
        changed = True

    if deepseek_key:
        # Replace provider, api_key, model for the first occurrence (which is the active one under 'ai:')
        config_content = re.sub(r'\n(\s*)provider:\s*".*?"', r'\n\1provider: "deepseek"', config_content, count=1)
        config_content = re.sub(r'\n(\s*)api_key:\s*".*?"', f'\n\\1api_key: "{deepseek_key}"', config_content, count=1)
        config_content = re.sub(r'\n(\s*)model:\s*".*?"', r'\n\1model: "deepseek-chat"', config_content, count=1)
        changed = True

    if changed:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        print("[*] DursGo config.yaml updated successfully.")

def update_lazyhunter_config(cookie):
    config_path = os.path.join("lazyhunter-main", "config.py")
    if not os.path.exists(config_path):
        return

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    pass

def run_lazyhunter(domain, scan_type, speed, cookie=None):
    print(f"[*] Running LazyHunter on {domain} (Type: {scan_type}, Speed: {speed})")
    
    if not os.path.exists("lazyhunter-main/lazyhunter.py"):
        print("[!] Error: lazyhunter.py not found in lazyhunter-main/")
        sys.exit(1)
        
    scan_choice = "1"
    if scan_type == "dks":
        scan_choice = "2"
    elif scan_type == "dps":
        scan_choice = "3"

    cmd = ["python", "lazyhunter.py"]
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Inject Go bin path for lazyhunter's subprocesses
    go_bin = os.path.join(os.path.expanduser("~"), "go", "bin")
    path_key = 'PATH'
    for k in env.keys():
        if k.upper() == 'PATH':
            path_key = k
            break
            
    if go_bin not in env.get(path_key, ""):
        # Prepend to prioritize Go binaries over other conflicting scripts (e.g. httpx from Python)
        env[path_key] = go_bin + os.pathsep + env.get(path_key, "")

    if cookie:
        env["LAZYHUNTER_COOKIE"] = cookie
        
    env["PYTHONUNBUFFERED"] = "1"

    try:
        speed_choice = "2"
        if speed == "low":
            speed_choice = "1"
        elif speed == "fast":
            speed_choice = "3"
            
        # The target input function gets called multiple times or differently depending on scan_type
        # In lazyhunter.py, the order of prompts is:
        # 1. Feature Menu: e.g. "3" for Deep Scan
        # 2. Target URL: e.g. "vulnweb.com"
        # 3. Scanning speed: e.g. "2" for Standard
        input_data = f"{scan_choice}\n{domain}\n{speed_choice}\n99\n"
        process = subprocess.Popen(
            cmd, 
            cwd="lazyhunter-main", 
            env=env, 
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        process.communicate(input=input_data)
        if process.returncode != 0:
            print(f"[!] LazyHunter encountered an error. Return code {process.returncode}")
    except Exception as e:
        print(f"[!] LazyHunter encountered an exception: {e}")

def run_dursgo(subdomains):
    print(f"[*] Found {len(subdomains)} active subdomains. Running DursGo on each...")
    
    dursgo_dir = "dursgo-main"
    dursgo_bin = "dursgo" if os.name != 'nt' else "dursgo.exe"
    
    if not os.path.exists(os.path.join(dursgo_dir, dursgo_bin)):
        print("[*] Building DursGo...")
        try:
            subprocess.run(["go", "build", "-o", dursgo_bin, "./cmd/dursgo"], cwd=dursgo_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to build DursGo: {e}")
            sys.exit(1)
            
    os.makedirs(os.path.join(dursgo_dir, "reports"), exist_ok=True)
    
    for url in subdomains:
        print(f"\n[>] Scanning {url} with DursGo (AI Enabled)")
        hostname = url.split("://")[-1].split("/")[0]
        report_file = f"reports/dursgo_{hostname}.json"
        
        cmd = [
            f"./{dursgo_bin}" if os.name != 'nt' else dursgo_bin,
            "-u", url,
            "-s", "all",
            "--enable-ai",
            "-output-json", report_file
        ]
        
        try:
            subprocess.run(cmd, cwd=dursgo_dir)
        except Exception as e:
            print(f"[!] Error running DursGo on {url}: {e}")

def run_xsscanner(subdomains, cookie, gemini_api_key):
    print(f"\n[*] Running XSS Scanner on {len(subdomains)} active subdomains...")
    xsscanner_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".", "cloned_repos", "xsscanner"))
    
    if not os.path.exists(os.path.join(xsscanner_dir, "cli.py")):
        print(f"[!] Warning: xsscanner not found at {xsscanner_dir}. Skipping XSS scan.")
        return

    try:
        subprocess.run(["playwright", "install", "chromium"], cwd=xsscanner_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    for url in subdomains:
        print(f"\n[>] XSS Scanning {url}")
        
        cmd = ["python", "cli.py", url, "-m", "quick"]
        
        if cookie:
            cmd.extend(["--cookie", cookie])
            
        if gemini_api_key:
            cmd.extend(["--api-key", gemini_api_key])
            
        try:
            subprocess.run(cmd, cwd=xsscanner_dir)
        except Exception as e:
            print(f"[!] Error running XSS Scanner on {url}: {e}")

def run_ds_store_exp(subdomains, cookie=None):
    print(f"\n[*] Running ds_store_exp on {len(subdomains)} active subdomains...")
    ds_store_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".", "cloned_repos", "ds_store_exp"))
    
    if not os.path.exists(os.path.join(ds_store_dir, "ds_store_exp.py")):
        print(f"[!] Warning: ds_store_exp not found at {ds_store_dir}. Skipping ds_store checks.")
        return

    env = os.environ.copy()
    if cookie:
        env["DS_STORE_COOKIE"] = cookie

    for url in subdomains:
        # ds_store_exp checks for /.DS_Store appended
        ds_url = url.rstrip('/') + "/.DS_Store"
        print(f"\n[>] Checking for .DS_Store exposure on {ds_url}")
        
        cmd = ["python", "ds_store_exp.py", ds_url]
        
        try:
            subprocess.run(cmd, cwd=ds_store_dir, env=env)
        except Exception as e:
            print(f"[!] Error running ds_store_exp on {ds_url}: {e}")

def run_claude_bug_bounty(target, cookie, deepseek_key):
    print(f"\n[*] Starting claude-bug-bounty analysis on {target}...")
    cbb_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".", "cloned_repos", "claude-bug-bounty"))
    if not os.path.exists(cbb_dir):
        print(f"[!] claude-bug-bounty not found at {cbb_dir}")
        return

    env = os.environ.copy()
    if deepseek_key:
        env["DEEPSEEK_API_KEY"] = deepseek_key
        env["BRAIN_PROVIDER"] = "deepseek"
    
    cmd = ["python", "agent.py", "--target", target]
    if cookie:
        cmd.extend(["--cookie", cookie])
        
    print(f"[*] Running command: {' '.join(cmd)} in {cbb_dir}")
    
    process = subprocess.Popen(cmd, cwd=cbb_dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    
    bump_injected = False
    reports_dir = os.path.abspath(os.path.join("dursgo-main", "reports")).replace('\\', '/')
    
    for line in iter(process.stdout.readline, ''):
        sys.stdout.write(line)
        sys.stdout.flush()
        
        if not bump_injected and "[Agent] Bump:" in line and ">" in line:
            parts = line.split(">")
            if len(parts) > 1:
                bump_path = parts[-1].strip()
                bump_path = re.sub(r'\x1b\[[0-9;]*m', '', bump_path)
                
                full_bump_path = os.path.join(cbb_dir, bump_path)
                
                guidance = (
                    f"Tugas Anda:\n"
                    f"1. Selidiki dan identifikasi tech stack, arsitektur sistem, dan teknologi yang digunakan oleh target '{target}'.\n"
                    f"2. Baca laporan keamanan JSON dari DursGo di direktori {reports_dir}.\n"
                    f"3. Analisa setiap kerentanan yang ditemukan agar sesuai dan spesifik dengan konteks sistem/teknologi target tersebut (berikan langkah eksploitasi dan dampak yang akurat sesuai dengan sistem yang diperiksa)."
                )
                try:
                    with open(full_bump_path, "w", encoding="utf-8") as f:
                        f.write(guidance)
                    print(f"\n[*] Successfully injected guidance into {full_bump_path}")
                    bump_injected = True
                except Exception as e:
                    print(f"\n[!] Failed to inject guidance: {e}")
                    
    process.wait()
    print(f"\n[*] claude-bug-bounty completed with code {process.returncode}")

def main():
    parser = argparse.ArgumentParser(description="Run LazyHunter and pipe results to DursGo, XSS Scanner, ds_store_exp, and Claude Bug Bounty")
    parser.add_argument("-t", "--target", help="Target domain (e.g., example.com)")
    parser.add_argument("--scan-type", default="lts", choices=["lts", "dks", "dps"], 
                        help="LazyHunter scan type: lts (Light), dks (Dark), dps (Deep). Default is lts.")
    parser.add_argument("--speed", default="fast", choices=["low", "standard", "fast"],
                        help="LazyHunter scan speed. Default is fast.")
    parser.add_argument("--cookie", help="Cookie to use for tools authentication")
    parser.add_argument("--deepseek-api-key", help="Deepseek API key for DursGo and Claude Bug Bounty AI analysis")
    parser.add_argument("--gemini-api-key", help="Gemini API key specifically for XSS Scanner AI analysis")
    parser.add_argument("--update", action="store_true", help="Update all tools from their respective GitHub repositories")
    
    # Tool selection flags
    parser.add_argument("--dursgo", action="store_true", help="Run DursGo scan")
    parser.add_argument("--xss", action="store_true", help="Run XSS Scanner")
    parser.add_argument("--dsstore", action="store_true", help="Run ds_store_exp")
    parser.add_argument("--cbb", action="store_true", help="Run Claude Bug Bounty")
    parser.add_argument("--all", action="store_true", help="Run all tools (default if no specific tool is selected)")
    
    args = parser.parse_args()
    
    # Determine which tools to run
    run_any_specific = args.dursgo or args.xss or args.dsstore or args.cbb
    if not run_any_specific or args.all:
        args.dursgo = args.xss = args.dsstore = args.cbb = True
    
    if args.update:
        update_all_tools()
        
    if not args.target:
        print("[!] Error: the following arguments are required: -t/--target")
        sys.exit(1)
        
    target = args.target
    
    if args.cookie or args.deepseek_api_key:
        update_dursgo_config(args.cookie, args.deepseek_api_key)
        
    run_lazyhunter(target, args.scan_type, args.speed, args.cookie)
    
    active_file_path = os.path.join("lazyhunter-main", "active", f"active_{target}.txt")
    if not os.path.exists(active_file_path):
        print(f"[!] Active subdomains file not found: {active_file_path}")
        print("[!] Make sure LazyHunter found subdomains and the tool didn't error out.")
        sys.exit(1)
        
    subdomains = []
    with open(active_file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                if not line.startswith("http"):
                    line = "http://" + line
                subdomains.append(line)
                
    if not subdomains:
        print(f"[!] No active subdomains found in {active_file_path}")
        sys.exit(0)
        
    if args.dursgo:
        run_dursgo(subdomains)
        print("\n[*] DursGo scans completed! Check dursgo-main/reports/ for JSON reports.")
    
    if args.xss:
        run_xsscanner(subdomains, args.cookie, args.gemini_api_key)
        print("\n[*] XSS scans completed!")
    

    if args.dsstore:
        run_ds_store_exp(subdomains, args.cookie)
        print("\n[*] .DS_Store scans completed!")
    
    if args.cbb:
        run_claude_bug_bounty(target, args.cookie, args.deepseek_api_key)
        print("\n[*] Claude Bug Bounty analysis completed!")

if __name__ == "__main__":
    main()

