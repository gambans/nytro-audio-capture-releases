# SNAPTURE protected release channel

This directory is consumed only by the SNAPTURE plugin's pinned HTTPS update client. `latest.json` starts in `pending` mode. To publish a valid update, upload the signed and tested `p-91f27ac004f8-VERSION.zip` containing exactly `SNAPTURE.component/` and replace `latest.json` with `version`, `download_url`, and lowercase `sha256`. The plugin validates version, the exact allowed GitHub directory and file naming, SHA-256, macOS bundle identity, signature, and arm64 before staging. The isolated helper installs only after Logic exits.

Do not publish an update until a native Logic AU smoke test has passed. Do not place signing keys, tokens or private source here.
