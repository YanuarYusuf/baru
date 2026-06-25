import argparse
import subprocess
import os
import sys

def run_lazyhunter(domain, scan_type, speed):
    print(f"[*] Running LazyHunter on {domain} (Type: {scan_type}, Speed: {speed})")
    
    # Check if lazyhunter is available
    if not os.path.exists("lazyhunter-main/lazyhunter.py"):
        print("[!] Error: lazyhunter.py not found in lazyhunter-main/")
        sys.exit(1)
        
    cmd = ["python", "lazyhunter.py", scan_type, "-t", domain, "-s", speed]
    
    try:
        # Run in lazyhunter-main directory
        subprocess.run(cmd, cwd="lazyhunter-main", check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] LazyHunter encountered an error: {e}")
        # Proceeding anyway as some results might have been generated
    
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
            
    # Make sure reports directory exists
    os.makedirs(os.path.join(dursgo_dir, "reports"), exist_ok=True)
    
    for url in subdomains:
        print(f"\n[>] Scanning {url} with DursGo (AI Enabled)")
        # Extract subdomain name for JSON output filename
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

def main():
    parser = argparse.ArgumentParser(description="Run LazyHunter and pipe results to DursGo with AI analysis")
    parser.add_argument("-t", "--target", required=True, help="Target domain (e.g., example.com)")
    parser.add_argument("--scan-type", default="-lts", choices=["-lts", "-dks", "-dps"], 
                        help="LazyHunter scan type: -lts (Light), -dks (Dark), -dps (Deep). Default is -lts.")
    parser.add_argument("--speed", default="fast", choices=["low", "standard", "fast"],
                        help="LazyHunter scan speed. Default is fast.")
    
    args = parser.parse_args()
    
    target = args.target
    run_lazyhunter(target, args.scan_type, args.speed)
    
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
                # Ensure the url has http:// or https://
                if not line.startswith("http"):
                    line = "http://" + line
                subdomains.append(line)
                
    if not subdomains:
        print(f"[!] No active subdomains found in {active_file_path}")
        sys.exit(0)
        
    run_dursgo(subdomains)
    print("\n[*] All scans completed! Check dursgo-main/reports/ for JSON reports.")

if __name__ == "__main__":
    main()
