import requests
import re
from datetime import datetime

# Sources
zee_m3u_url = "https://raw.githubusercontent.com/alex8875/m3u/refs/heads/main/z5.m3u"

# Playlist file
m3u_file = "z4.m3u"


def get_zee_token():
    """Fetch latest Zee5 hdntl token from remote m3u source."""
    try:
        resp = requests.get(zee_m3u_url, timeout=5)
        resp.raise_for_status()
        text = resp.text
        match = re.search(r"\?hdntl=[^\s\"']+", text)
        if match:
            token_part = match.group(0).lstrip("?")
            return token_part
        else:
            print("⚠️ No hdntl token found in Zee m3u source.")
            return None
    except Exception as e:
        print("⚠️ Zee token fetch failed:", e)
        return None


def extract_old_zee():
    """Extract old Zee5 token from backend.m3u (for status line)."""
    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            content = f.read()
        zee_old = re.search(r"hdntl=[^\s\"']+", content)
        return zee_old.group(0) if zee_old else None
    except FileNotFoundError:
        return None


def update_backend_status(old_zee5, new_zee5):
    """Update status line at top of backend.m3u."""
    zee5_status = f"{old_zee5[-4:] if old_zee5 else '----'} → {new_zee5[-4:] if new_zee5 else '----'}"
    status_line = f"# Zee5 Token: {zee5_status} | Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"

    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    if lines and lines[0].startswith("# Zee5 Token:"):
        lines[0] = status_line
    else:
        lines.insert(0, status_line)

    with open(m3u_file, "w", encoding="utf-8") as f:
        f.writelines(lines)


def update_playlist(zee_token):
    """Replace old Zee5 token in backend.m3u with new one."""
    with open(m3u_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove old Zee token
    content = re.sub(r"\?hdntl=[^\s\"]+", "", content)

    # Add new Zee token
    if zee_token:
        content = re.sub(
            r"(https://z5ak-cmaflive\.zee5\.com[^\s\"']+?\.m3u8)",
            rf"\1?{zee_token}",
            content
        )

    with open(m3u_file, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Zee5 Playlist updated.")


def main():
    old_zee = extract_old_zee()

    # Fetch Zee token
    zee_token = get_zee_token()
    if not zee_token:
        raise Exception("❌ Could not fetch Zee token")

    # Update playlist
    update_playlist(zee_token)

    # Update backend status line
    update_backend_status(old_zee, zee_token)


if __name__ == "__main__":
    main()
