# Development

## Build and run docker
```bash
    docker build -t scum_bot .
    docker run --name scum_bot -d -v ".env:/app/.env" -v "db.sqlite3:/app/db.sqlite3" scum_bot
```

## Build language catalog

Extract phrases from source code:
```bash
python setup.py extract_messages --output-file locale/messages.pot --input-dirs ./
```

Prepare/Update template:
```bash
python setup.py update_catalog -l de -i locale/messages.pot -o locale/de/LC_MESSAGES/messages.po
```

Compile catalog:
```bash
cd locale/de/LC_MESSAGES
msgfmt.py messages.po
```
