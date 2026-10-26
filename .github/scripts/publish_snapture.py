#!/usr/bin/env python3
"""Verify an immutable native AU payload before activating its update channel."""
import hashlib, json, pathlib, plistlib, re, subprocess, tempfile, zipfile
folder = pathlib.Path("r-91f27ac004f8")
candidates = []
for path in folder.glob("p-91f27ac004f8-*.zip"):
    match = re.fullmatch(r"p-91f27ac004f8-(\d+)\.(\d+)\.(\d+)\.zip", path.name)
    if match: candidates.append((tuple(map(int, match.groups())), path))
version_tuple, archive = max(candidates)
version = ".".join(map(str, version_tuple))
# Versions before 0.3.4 use a different bundle spelling and helper protocol.
assert version_tuple >= (0, 3, 4)
manifest_path = folder / "latest-snapture.json"
if manifest_path.exists():
    previous = json.loads(manifest_path.read_text())
    if previous.get("version"):
        assert version_tuple >= tuple(map(int, previous["version"].split("."))), "Refusing downgrade"
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
if manifest_path.exists() and previous.get("version") == version:
    assert previous["sha256"] == digest, "Published payloads are immutable"
with tempfile.TemporaryDirectory() as temp:
    with zipfile.ZipFile(archive) as z:
        assert all(n.startswith("Snapture.component/") and ".." not in n.split("/") for n in z.namelist())
    subprocess.run(["ditto", "-x", "-k", str(archive), temp], check=True)
    bundle = pathlib.Path(temp) / "Snapture.component"
    info = plistlib.loads((bundle / "Contents/Info.plist").read_bytes())
    assert info["CFBundleIdentifier"] == "audio.nytro.snapture"
    assert info["CFBundleShortVersionString"] == version
    assert info["CFBundleExecutable"] == "Snapture"
    components = info["AudioComponents"]
    assert any(c["type"] == "aufx" and c["subtype"] == "Snpt" and c["manufacturer"] == "Nytr" and c["name"] == ("Nytro Audio: Capture" if version_tuple >= (1, 0, 0) else "Nytro Audio: Snapture") for c in components)
    subprocess.run(["codesign", "--verify", "--deep", "--strict", str(bundle)], check=True)
    binary = bundle / "Contents/MacOS/Snapture"
    assert "arm64" in subprocess.check_output(["lipo", "-archs", str(binary)], text=True).split()
    helper = bundle / "Contents/Helpers/SnaptureUpdater"
    assert helper.is_file()
    assert "arm64" in subprocess.check_output(["lipo", "-archs", str(helper)], text=True).split()
manifest = {"version": version, "download_url": "https://raw.githubusercontent.com/gambans/nytro-audio-capture-releases/main/" + str(archive), "sha256": digest}
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
print("Verified Snapture update", version, digest)
