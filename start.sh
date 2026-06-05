#!/bin/bash

FILE="scythez.py"
NAME="scythez"

if [ ! -f "$FILE" ]; then
    echo "[!] File $FILE tidak ditemukan."
    exit 1
fi

if ! head -n1 "$FILE" | grep -q "^#!/usr/bin/env python3"; then
    sed -i '1i#!/usr/bin/env python3' "$FILE"
fi

mv "$FILE" "$NAME"
chmod +x "$NAME"

sudo cp "$NAME" /usr/local/bin/
sudo chmod +x /usr/local/bin/"$NAME"

echo "[+] Selesai."
echo "[+] Jalankan dengan:"
echo "    $NAME"
