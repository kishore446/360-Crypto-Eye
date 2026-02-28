# Practical Operations Runbook for the Crypto Signal System

## 1. Overview
This document provides a comprehensive runbook for the operations of the Crypto Signal System.

## 2. Services and Compose Commands
```bash
# Start the services
docker-compose up -d
# Stop the services
docker-compose down
```

## 3. Startup and Restart Procedures
```bash
# Restart all services
docker-compose restart
```

## 4. Database Checks (signals coverage query by market/interval)
```sql
SELECT market, interval, COUNT(*)
FROM signals
WHERE timestamp >= NOW() - INTERVAL '1 DAY'
GROUP BY market, interval;
```

## 5. Publisher Health Checks
### Cycle Start
```bash
curl -X GET http://localhost:8080/cycle/start
```
### Interval Done
```bash
curl -X GET http://localhost:8080/interval/done
```
### Cycle Complete
```bash
curl -X GET http://localhost:8080/cycle/complete
```

## 6. API Validation Curl Examples
### Spot
```bash
curl -X GET "http://localhost:8080/api/spot"
```
### Futures
```bash
curl -X GET "http://localhost:8080/api/futures"
```
### Intervals
```bash
curl -X GET "http://localhost:8080/api/intervals"
```

## 7. Troubleshooting Database Password Authentication Failures for Postgres User
```sql
ALTER USER postgres WITH PASSWORD 'new_password';
# Ensure DATABASE_URL alignment
export DATABASE_URL="postgresql://postgres:new_password@localhost:5432/mydatabase"
```

## 8. Dedupe Verification Query for candle_open_time Duplicates
```sql
SELECT candle_open_time, COUNT(*)
FROM candles
GROUP BY candle_open_time
HAVING COUNT(*) > 1;
```

## 9. Orphan Container Cleanup
```bash
docker-compose rm --remove-orphans
```

## 10. Security Steps to Rotate Exposed Telegram Token
1. Go to BotFather in Telegram.
2. Use the `/revoke` command for your bot to invalidate the current token.
3. Use `/newtoken` to generate a new token.
4. Update your environment configuration with the new token.

## 11. Backup/Restore Notes for Postgres
### Backup
```bash
pg_dump -U postgres -d mydatabase > backup.sql
```
### Restore
```bash
psql -U postgres -d mydatabase < backup.sql
```

## 12. Incident Checklist and Rollback Steps
- Identify the issue
- Rollback to the last stable version using `docker-compose pull` and `docker-compose up -d`
- Monitor for further issues.
