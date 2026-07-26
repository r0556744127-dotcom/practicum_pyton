# Kung-Fu Chess (CTD 26)

## Server design (`server/`)

| File | Role |
|------|------|
| `game_server.py` | Entry point: login, message routing, game loop |
| `rooms.py` | Create / Join / Cancel / viewers / spectate |
| `matchmaking.py` | Play: ELO ±100 queue + 1 min timeout |
| `session.py` | Start match, scores, ELO update, disconnect resign |
| `broadcast.py` | Build `state` JSON + activity log + broadcast |
| `constants.py` | Timeouts, board layout, capture points |
| `users_db.py` / `elo.py` | Auth + rating |

## Setup (once)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install opencv-python websockets
```

## Run (two players locally)

**Terminal 1 — server**

```powershell
python -u server/game_server.py
```

**Terminal 2 — player A**

```powershell
python ui/network_client.py
```

Home window → Login or Register → Lobby → Play / Room / Spectate.

**Terminal 3 — player B**

```powershell
python ui/network_client.py
```

### Room

1. Player A: Lobby → Room → Create (code shown on waiting window + on board).
2. Player B: Lobby → Room → Join → enter code.
3. Extra players joining the same code become **viewers**.

### Local offline UI (EventBus sounds / banner)

```powershell
python -m ui.ui_app
```

### Register users (optional shell)

```powershell
python server/home_shell.py
```

### Tests

```powershell
python -m pytest tests -q
```
