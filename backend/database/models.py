SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  vendor_name TEXT,
  location TEXT,
  remote_type TEXT,
  employment_type TEXT,
  posted_date TEXT,
  source_url TEXT UNIQUE,
  source_type TEXT,
  job_description TEXT,
  experience_required TEXT,
  required_skills TEXT,
  preferred_skills TEXT,
  cloud_platform TEXT,
  role_type TEXT,
  match_score INTEGER DEFAULT 0,
  missing_keywords TEXT,
  recommendation TEXT,
  status TEXT DEFAULT 'Not Applied',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS manual_jds (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  company TEXT,
  location TEXT,
  jd_text TEXT NOT NULL,
  required_skills TEXT,
  preferred_skills TEXT,
  experience_required TEXT,
  cloud_platform TEXT,
  role_type TEXT,
  match_score INTEGER,
  missing_keywords TEXT,
  recommendation TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resume_versions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER,
  manual_jd_id INTEGER,
  resume_name TEXT NOT NULL,
  docx_path TEXT NOT NULL,
  pdf_path TEXT,
  match_score INTEGER,
  company TEXT,
  role_title TEXT,
  generation_status TEXT DEFAULT 'completed',
  requirement_coverage INTEGER DEFAULT 0,
  truthfulness_score INTEGER DEFAULT 0,
  generation_report TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resume_drafts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER,
  manual_jd_id INTEGER,
  draft_name TEXT NOT NULL,
  draft_path TEXT NOT NULL,
  company TEXT,
  role_title TEXT,
  match_score INTEGER,
  ats_score INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending_approval',
  generation_report TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  approved_at TEXT
);

CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER,
  resume_id INTEGER,
  company TEXT NOT NULL,
  role_title TEXT NOT NULL,
  job_link TEXT,
  status TEXT DEFAULT 'Not Applied',
  applied_date TEXT,
  recruiter_name TEXT,
  follow_up_date TEXT,
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_name TEXT NOT NULL,
  source_url TEXT NOT NULL,
  source_type TEXT NOT NULL,
  active INTEGER DEFAULT 1,
  last_fetched_at TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_fetch_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fetch_date TEXT,
  jobs_found INTEGER,
  jobs_saved INTEGER,
  duplicates_removed INTEGER,
  errors TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER,
  agent_name TEXT NOT NULL,
  status TEXT NOT NULL,
  detail TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category TEXT NOT NULL,
  severity TEXT NOT NULL DEFAULT 'info',
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  job_id INTEGER,
  is_read INTEGER NOT NULL DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fte_approvals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER NOT NULL UNIQUE,
  resume_id INTEGER,
  score INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  reason TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  decided_at TEXT
);
"""
