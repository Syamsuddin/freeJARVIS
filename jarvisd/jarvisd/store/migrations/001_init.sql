-- 001 — skema awal (docs/07_DATA_MODEL.md). Maju saja (docs/12).
CREATE TABLE projects (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE COLLATE NOCASE,
    path            TEXT NOT NULL UNIQUE,
    vocabulary      TEXT,
    last_session_id INTEGER REFERENCES sessions(id) ON DELETE SET NULL,
    created_at      TEXT NOT NULL,
    opened_at       TEXT
);

CREATE TABLE sessions (
    id             INTEGER PRIMARY KEY,
    project_id     INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sdk_session_id TEXT NOT NULL UNIQUE,
    started_at     TEXT NOT NULL,
    last_active_at TEXT NOT NULL
);

CREATE TABLE turns (
    id              INTEGER PRIMARY KEY,
    session_id      INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    speaker         TEXT NOT NULL CHECK (speaker IN ('user', 'jarvis')),
    channel         TEXT NOT NULL CHECK (channel IN ('voice', 'text')),
    text            TEXT NOT NULL,
    screen_text     TEXT,
    heard_until     INTEGER,
    idempotency_key TEXT UNIQUE,
    created_at      TEXT NOT NULL
);

CREATE TABLE jobs (
    id          INTEGER PRIMARY KEY,
    session_id  INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    turn_id     INTEGER NOT NULL REFERENCES turns(id),
    state       TEXT NOT NULL,
    model       TEXT NOT NULL,
    fail_reason TEXT,
    started_at  TEXT NOT NULL,
    ended_at    TEXT
);

CREATE TABLE tool_events (
    id         INTEGER PRIMARY KEY,
    job_id     INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    tool       TEXT NOT NULL,
    summary    TEXT NOT NULL,
    file_path  TEXT,
    tier       TEXT NOT NULL CHECK (tier IN ('auto', 'word', 'phrase', 'code')),
    decision   TEXT NOT NULL CHECK (decision IN ('auto', 'allowed', 'denied', 'expired')),
    created_at TEXT NOT NULL
);

CREATE TABLE pending_prompts (
    id              TEXT PRIMARY KEY,
    job_id          INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    kind            TEXT NOT NULL CHECK (kind IN ('approval', 'question')),
    tier            TEXT CHECK (tier IN ('word', 'phrase', 'code')),
    payload         TEXT NOT NULL,
    expected_phrase TEXT,
    expires_at      TEXT NOT NULL,
    resolution      TEXT CHECK (resolution IN ('allowed', 'denied', 'expired', 'answered')),
    answer          TEXT
);

CREATE TABLE quota_snapshots (
    id                   INTEGER PRIMARY KEY,
    window_remaining_pct REAL,
    credit_remaining_pct REAL,
    raw                  TEXT NOT NULL,
    created_at           TEXT NOT NULL
);

CREATE TABLE settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX idx_turns_session_created ON turns (session_id, created_at);
CREATE INDEX idx_turns_created ON turns (created_at);
CREATE INDEX idx_jobs_session_started ON jobs (session_id, started_at);
CREATE INDEX idx_tool_events_job_created ON tool_events (job_id, created_at);
CREATE INDEX idx_pending_prompts_resolution ON pending_prompts (resolution);
