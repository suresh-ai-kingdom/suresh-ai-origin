# PostgreSQL Migration Guide - SURESH AI ORIGIN

## Why Migrate to PostgreSQL?

**Current (SQLite):**
- ✅ Simple, file-based, zero config
- ❌ Single-writer limitation (locks under concurrent writes)
- ❌ No connection pooling
- ❌ Limited for > 100 concurrent users

**Target (PostgreSQL):**
- ✅ Multi-user concurrent writes
- ✅ Connection pooling (pgBouncer)
- ✅ Better performance at scale
- ✅ Advanced features (JSONB, full-text search, replication)

---

## Migration Strategy

### Phase 1: Preparation (No Downtime)

1. **Create PostgreSQL Database on Render**
   - Go to Render Dashboard → New → PostgreSQL
   - Plan: Free (256 MB) or Starter ($7/month, 1 GB)
   - Name: `suresh-ai-origin-db`
   - User: `suresh_user` (auto-generated)
   - Copy **Internal Database URL** (starts with `postgresql://`)

2. **Install PostgreSQL Driver**
   ```bash
   pip install psycopg2-binary
   # Update requirements.txt
   echo "psycopg2-binary==2.9.9" >> requirements.txt
   ```

3. **Test Connection Locally**
   ```python
   import psycopg2
   conn = psycopg2.connect("postgresql://user:pass@host:5432/dbname")
   print("✅ Connected!")
   conn.close()
   ```

### Phase 2: Data Migration (< 5 min downtime)

**Method 1: Full Export/Import (Recommended for small DBs < 100 MB)**

```bash
# 1. Export SQLite to SQL dump
sqlite3 data.db .dump > data_export.sql

# 2. Convert SQLite syntax to PostgreSQL
# - Remove SQLite-specific pragmas
# - Fix AUTOINCREMENT → SERIAL
# - Fix DATETIME → TIMESTAMP

# 3. Import to PostgreSQL
psql $DATABASE_URL < data_export_pg.sql
```

**Method 2: Python Migration Script** (see `scripts/migrate_to_postgresql.py` below)

### Phase 3: Update Application (< 1 min downtime)

1. **Update `utils.py`**
   ```python
   def _get_db_url():
       # Prefer PostgreSQL, fall back to SQLite
       pg_url = os.getenv('DATABASE_URL')
       if pg_url:
           # Render uses 'postgres://', SQLAlchemy needs 'postgresql://'
           if pg_url.startswith('postgres://'):
               pg_url = pg_url.replace('postgres://', 'postgresql://', 1)
           return pg_url
       return os.getenv('DATA_DB', 'sqlite:///data.db')
   ```

2. **Add to Render Environment**
   ```
   DATABASE_URL=<Internal Database URL from Render PostgreSQL>
   ```

3. **Deploy**
   ```bash
   git add .
   git commit -m "feat: PostgreSQL migration"
   git push
   ```
   - Render auto-deploys
   - Application automatically uses PostgreSQL (DATABASE_URL detected)

### Phase 4: Verification (Post-Deploy)

1. **Health Check**
   ```bash
   curl https://suresh-ai-origin.onrender.com/health
   # Should return: "database": "ok"
   ```

2. **Test Core Flows**
   - Create order
   - View admin dashboard
   - Run automation workflows

3. **Monitor Logs**
   - Check Render logs for database errors
   - Verify no SQLite references

### Phase 5: Cleanup (After 24 hrs)

1. **Backup SQLite (one last time)**
   ```bash
   python scripts/backup_db.py create
   ```

2. **Remove SQLite File from Repo** (optional)
   ```bash
   # Keep data.db in .gitignore but remove from Render
   # Render will use PostgreSQL only
   ```

---

## Connection Pooling (Advanced)

After successful migration, add connection pooling for better performance:

**Option 1: SQLAlchemy Pooling (Built-in)**
```python
# In utils.py get_engine()
engine = create_engine(
    url,
    poolclass=QueuePool,
    pool_size=5,          # Max connections
    max_overflow=10,      # Extra connections on demand
    pool_pre_ping=True,   # Verify connection before use
    pool_recycle=3600,    # Recycle connections every hour
)
```

**Option 2: pgBouncer (Production-Grade)**
- Add pgBouncer service on Render (requires paid plan)
- Connection pooling at database proxy level
- Handles thousands of connections efficiently

---

## Rollback Plan (If Things Go Wrong)

1. **Emergency Rollback**
   - Remove `DATABASE_URL` from Render environment
   - Redeploy (will fall back to SQLite)
   - Restore from latest backup: `python scripts/backup_db.py restore`

2. **Data Loss Prevention**
   - Always backup before migration
   - Test migration on staging first
   - Keep SQLite backup for 7 days

---

## Cost Comparison

| Tier | SQLite (Free) | PostgreSQL (Free) | PostgreSQL (Paid) |
|------|--------------|-------------------|-------------------|
| Storage | Render disk (512 MB) | 256 MB | 1 GB - 256 GB |
| Concurrent Users | ~10-20 | ~100 | ~500+ |
| Backups | Manual | Daily (7 day retention) | Daily + point-in-time |
| Cost | $0 | $0 | $7-$95/month |

**Recommendation:** Start with PostgreSQL Free, upgrade to Starter ($7/month) when:
- Active users > 50
- Database size > 200 MB
- Need better backup retention

---

## Migration Script

See `scripts/migrate_to_postgresql.py` for automated migration tool.

**Usage:**
```bash
# Dry-run (test only, no changes)
python scripts/migrate_to_postgresql.py --dry-run

# Full migration
python scripts/migrate_to_postgresql.py --source sqlite:///data.db --target $DATABASE_URL

# Verify
python scripts/migrate_to_postgresql.py --verify
```

---

## Post-Migration Performance Gains

**Expected Improvements:**
- **Concurrent writes:** 10x faster (no file locks)
- **Analytics queries:** 2-3x faster (better query optimizer)
- **Scalability:** 10-20 users → 100+ users
- **Reliability:** No more "database is locked" errors

**Monitoring:**
- Use `/api/admin/slow-queries` to track performance
- Set `SLOW_QUERY_THRESHOLD=0.5` (500ms) for PostgreSQL
- Add pgAdmin or DataGrip for database monitoring

---

*Migration tested on: Render Free Tier → PostgreSQL Free Tier*
*Estimated downtime: < 5 minutes for databases under 100 MB*
