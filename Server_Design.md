# Server Design — Kung-Fu Chess (Scale Week)

Today we have one Python process + SQLite. That works for class. Below is how to scale.

---

## 1) 100 million registered users — which DB? SQLite?

**Use PostgreSQL (or MySQL), not SQLite.**

- SQLite = one file, weak with many writers / many app servers.
- We need many servers logging users in at once → real DB server + replicas.
- Redis can help for sessions/presence, but accounts/ELO stay in Postgres.

---

## 2) 10 million players online at once — one server? How do rooms work?

**One server is not enough.**

Split into Dockers/services:

| Service | Job |
|---------|-----|
| Gateway | Accept WebSockets, send player to the right game node |
| Matchmaking | Find opponent (ELO ±100) |
| Game nodes | Run rooms / live games (many copies) |
| Redis | Remember: player → node, room → node |
| Postgres | Users + ELO |

**Who is where?** Redis map: `room_id → game_node`.  
**Everyone can play / join any room?** Client joins by room code → Gateway looks up Redis → connects them to the **same** game node that owns that room (sticky room).

---

## 3) Move every 2 seconds — how much network?

- **Per player:** small (hundreds of bytes/sec) — fine for home internet.
- **For 10M players together:** huge (Gbit/s scale) — need many servers + regions.
- Do **not** broadcast full board 20 times/sec to everyone. Send moves/deltas only to people in that room.

---

## 4) Games last 30–90 seconds — meaning for Dockers?

- Rooms are **short-lived** → game containers create room, play, free memory.
- High churn → matchmaking/gateway must scale easily.
- Save to DB mainly at **game end** (winner, ELO), not every tick.
- Easy to add more game-node Dockers when more rooms are active.

---

## Learning notes (short)

- **Docker** — package each service in a container.
- **Kubernetes** — run/scale many containers.
- **K3s** — small/simple Kubernetes for learning.

---

