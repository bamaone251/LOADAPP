import os, json, sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import urlopen
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
TZ = ZoneInfo(os.getenv('APP_TIMEZONE', 'America/Chicago'))
SOURCE = os.getenv('LOADMAP_URL', 'https://loadmap.loxload.com').rstrip('/')
DB = os.getenv('DB_PATH', 'data/dashboard.sqlite3')
os.makedirs(os.path.dirname(os.path.abspath(DB)), exist_ok=True)
with sqlite3.connect(DB) as db:
    db.execute('CREATE TABLE IF NOT EXISTS daily_totals (day TEXT PRIMARY KEY, total INTEGER NOT NULL)')

def today():
    return datetime.now(TZ).date().isoformat()

def map_day(row):
    if row.get('map_date'):
        return row['map_date'][:10]
    stamp = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=ZoneInfo('UTC'))
    return stamp.astimezone(TZ).date().isoformat()

@app.get('/')
def home():
    return render_template('index.html')

@app.get('/api/status')
def status():
    day = today()
    with sqlite3.connect(DB) as db:
        row = db.execute('SELECT total FROM daily_totals WHERE day=?', (day,)).fetchone()
    result = dict(day=day, total=row[0] if row else None, timezone=str(TZ), source=SOURCE)
    try:
        with urlopen(SOURCE + '/api/loadmaps', timeout=8) as response:
            maps = json.load(response)
        if not isinstance(maps, list):
            raise ValueError('Expected load map list')
        daily_maps = [m for m in maps if map_day(m) == day]
        metrics = {
            'plbs_created': 'plbs_created',
            'consolidations': 'dpr_consolidations',
            'rebuilds': 'dpr_rebuilds',
            'rewraps': 'dpr_rewraps',
        }
        totals = {key: sum(int(m.get(field) or 0) for m in daily_maps)
                  for key, field in metrics.items()}
        result.update(completed=len(daily_maps), connected=True, **totals)
    except Exception:
        result.update(completed=None, plbs_created=None, consolidations=None, rebuilds=None, rewraps=None, connected=False, error='Unable to read load maps. Check LOADMAP_URL and the source app.')
    response = jsonify(result)
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.post('/api/total')
def total():
    body = request.get_json(silent=True) or {}
    value = body.get('total')
    if type(value) is not int or not 0 <= value <= 100000:
        return jsonify(error='Enter a whole number from 0 to 100000.'), 400
    if body.get('day') != today():
        return jsonify(error='The day changed. Refresh and enter today’s total.'), 409
    with sqlite3.connect(DB) as db:
        if body.get('replace') is True:
            db.execute('INSERT INTO daily_totals VALUES (?,?) ON CONFLICT(day) DO UPDATE SET total=excluded.total', (today(), value))
        else:
            db.execute('INSERT OR IGNORE INTO daily_totals VALUES (?,?)', (today(), value))
    return jsonify(ok=True)
