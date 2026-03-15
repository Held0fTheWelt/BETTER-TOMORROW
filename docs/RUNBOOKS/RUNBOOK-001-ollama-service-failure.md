# RUNBOOK-001: Ollama Service Failure Recovery

**Severity**: High
**Impact**: L1-L2 tasks (code drafting, architecture) degrade to Claude API with increased costs
**MTTR Target**: <5 minutes
**Escalation**: On-call Engineer → Backend Lead → DevOps

---

## Detection

### Automated Alerts
- [ ] Alert: "Ollama Service Unavailable"
- [ ] Metric: Ollama health check failing (HTTP 500/timeout)
- [ ] Dashboard: Red indicator in Ollama status widget

### Manual Detection
- [ ] Code drafting takes unusually long (>10s)
- [ ] Architecture briefs trigger Claude instead of Ollama
- [ ] Cost tracking shows unexpected Claude charges
- [ ] User reports: "Feature working but very slow"

---

## Diagnosis (Immediate - 1-2 minutes)

### Step 1: Verify Ollama Status
```bash
# Check from application server
curl -s http://localhost:11434/api/tags | jq '.models | length'

# Expected: Returns number >0
# Failure: Connection refused, timeout, or error
```

### Step 2: Check Ollama Logs
```bash
# If Ollama runs as system service
journalctl -u ollama -n 100

# If Docker container
docker logs ollama-container-name

# Look for: Out of memory, GPU errors, connection issues
```

### Step 3: Determine Root Cause
| Symptom | Cause | Next Action |
|---------|-------|------------|
| Connection refused | Service not running | Step 4 (Restart) |
| CUDA out of memory | GPU overloaded | Step 5 (Unload models) |
| Slow response | Service struggling | Step 6 (Monitor) |
| Disk full | Storage exhausted | Step 7 (Cleanup) |

---

## Resolution

### Step 4: Restart Ollama Service (If Not Running)
```bash
# For systemd
sudo systemctl restart ollama
sudo systemctl status ollama

# For Docker
docker restart ollama-container-name
docker ps | grep ollama  # Should show as running

# Wait 30 seconds for service to stabilize
sleep 30

# Verify
curl -s http://localhost:11434/api/tags
```

### Step 5: Unload Large Models (If GPU Memory Exhausted)
```bash
# Check GPU memory
nvidia-smi

# If memory >90%:
# Stop the application temporarily to release locks
systemctl stop app-service

# Unload specific model
curl -s http://localhost:11434/api/generate \
  -d '{"model": "qwen2.5:72b", "keep_alive": 0}'

# Restart application
systemctl start app-service
```

### Step 6: Monitor Recovery
```bash
# Watch metrics
watch -n 2 'curl -s http://localhost:11434/api/tags | jq'

# Check application logs for successful Ollama connections
tail -f /var/log/app/error.log | grep -i ollama

# Verify costs normalize
# (no more unexpected Claude charges)
```

### Step 7: Cleanup (If Disk Full)
```bash
# Check Ollama cache directory
du -sh ~/.ollama/models

# Remove unused models
ollama rm model-name

# If Docker: clear image cache
docker system prune
```

---

## Verification (Post-Resolution)

### Checklist
- [ ] `curl http://localhost:11434/api/tags` returns 200 with models
- [ ] Application logs show "Connected to Ollama"
- [ ] Health check dashboard shows green status
- [ ] Test request: code-draft task completes in <5 seconds
- [ ] Architecture task routes to Ollama (not Claude)
- [ ] Cost tracking shows $0 cost for Ollama tasks

### Test Command
```bash
# Trigger a low-complexity task to verify routing
curl -X POST http://localhost:5000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test-ollama-recovery",
    "escalation_level": 1,
    "inputs": {"prompt": "Hello, world! Respond in one sentence."}
  }'

# Should see:
# "target_worker": "ollama"
# "cost": 0.0000
# "model": "qwen2.5-coder:32b" (or similar)
```

---

## Escalation

### If Ollama Remains Unavailable After 5 Minutes

1. **Notify on-call**:
   - "Ollama unavailable >5 minutes, escalating"
   - All L1-L2 tasks now using Claude (higher cost)

2. **Engage Backend Lead**:
   - Investigate deeper issues (disk corruption, GPU driver)
   - Check system resources (CPU, memory, disk)

3. **Customer Impact**:
   - L1-L2 tasks continue but with:
     - Increased latency (Claude slower than Ollama for some tasks)
     - Increased cost ($0 → $3-15 per task)
   - Consider rate limiting or temporary feature disablement

4. **Mitigation**:
   - If Ollama down >30 min:
     - Disable L1 task routing (force L0 skip or user approval)
     - Send customer notification
     - Activate incident response team

---

## Prevention

### Regular Maintenance
```bash
# Daily (automated)
- Health check Ollama service
- Monitor GPU memory usage
- Check disk space

# Weekly
- Review error logs for patterns
- Unload unused large models
- Clear old cache entries

# Monthly
- Full system restart
- Update Ollama software
- Review and optimize model list
```

### Configuration to Prevent Issues
```yaml
# In .env or config
OLLAMA_KEEP_ALIVE=5m  # Unload unused models after 5 min
OLLAMA_GPU_MEMORY_LIMIT=8000MB  # Reserve memory
OLLAMA_CACHE_DIR=/large/disk/path  # Not system disk
```

---

## Related Documentation

- ADR-004: Ollama-first routing strategy
- RUNBOOK-002: API Key Quota Exceeded
- RUNBOOK-003: Database Connection Exhaustion

---

## Tested By

- [ ] On-call Engineer
- [ ] Backend Lead
- [ ] DevOps Team

**Last Tested**: [Date]
**Next Review**: [Due Date]
