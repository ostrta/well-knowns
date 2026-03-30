# Crawler Script Audit & Recommendations

## Current State Analysis

### crawl.py (Current Production Script)
- **CONCURRENT_LIMIT**: 400 domains concurrently
- **REQUEST_TIMEOUT**: 1.5 seconds
- **BATCH_SIZE**: 1,000 domains (checkpoint frequency)
- **WELL_KNOWN_PATHS**: 7 endpoints per domain
- **Current domains.txt**: 50 domains (needs scaling to 1M)
- **Tech Stack**: Python 3.11+, httpx (async), asyncio semaphore

### crawl_improved.py (Optimized Version)
- **CONCURRENT_LIMIT**: 800 domains concurrently (2x increase)
- **REQUEST_TIMEOUT**: 2.0 seconds (slightly more reliable)
- **BATCH_SIZE**: 5,000 domains (5x less frequent checkpointing)
- **httpx.Limits**: max_connections=400, max_keepalive_connections=200
- **Pacing**: Sleep 0.5s every 1,000 domains (vs 0.3s every 100)

## Audit Findings

### Strengths:
1. **Proper async design** with semaphore-limited concurrency
2. **Checkpoint/resume capability** via crawl-state.json
3. **Output deduplication** to prevent duplicate entries
4. **Comprehensive error handling** (timeouts, connect errors, HTTP status codes)
5. **Proper User-Agent** for identification and reduced blocking
6. **JSONL output format** enables streaming processing
7. **Rate limit respect** (handles 429 responses with retry-after)
8. **Structured logging** to file and stdout

### Areas for Improvement (1M Scale):
1. **Domain list size**: Currently only 50 domains - need 1M for requested scale
2. **Concurrency tuning**: Could be increased further with proper monitoring
3. **Connection pooling**: httpx.Limits could be optimized for higher concurrency
4. **Progress monitoring**: No ETA or rate metrics visible in logs
5. **Adaptive throttling**: No automatic adjustment based on 429 responses
6. **Memory usage**: Large state sets could consume significant RAM at 1M scale

## Recommendations for 1M URL Crawling

### Immediate Actions:
1. **Scale domains.txt** to 1M URLs (Tranco top-1m.csv recommended)
2. **Use crawl_improved.py as base** - already optimized for higher throughput
3. **Monitor initial run** with smaller subset (e.g., 10k domains) to baseline performance

### Configuration Tuning for 1M Scale:
```
# Starting point (crawl_improved.py values)
CONCURRENT_LIMIT = 800
REQUEST_TIMEOUT = 2.0
BATCH_SIZE = 5_000
httpx.Limits(max_connections=400, max_keepalive_connections=200)

# If monitoring shows headroom:
CONCURRENT_LIMIT = 1200-1600
BATCH_SIZE = 10_000-20_000
httpx.Limits(max_connections=CONCURRENT_LIMIT, max_keepalive_connections=CONCURRENT_LIMIT//2)
```

### Performance Projections (1M domains × 7 endpoints = 7M requests):
| Concurrency | Est. Time (2s avg) | Notes |
|-------------|-------------------|-------|
| 400 (current) | ~9.7 hours | Baseline |
| 800 (improved) | ~4.8 hours | Recommended start |
| 1200 | ~3.2 hours | Monitor for errors/rate limits |
| 1600 | ~2.4 hours | Aggressive - watch for blocking |

### Strategic Consideration (from business plan):
> "Why top 100k, not top 1M for GTM: The top 100k domains have the highest density of professionally maintained servers with actual well-known infrastructure. Crawling 1M domains at launch means 85%+ of crawl effort hits domains with zero relevant endpoints. Start at 100k, expand after the pipeline is proven."

**Recommendation**: Start with Tranco top 100k to validate pipeline, then expand to 1M once system is stable.

### Additional Optimizations for 1M Scale:
1. **Domain prioritization**: Process higher-ranked domains first (more likely to have endpoints)
2. **Adaptive concurrency**: Reduce limit when detecting 429 responses
3. **DNS optimization**: Consider local DNS cache or increased DNS timeout
4. **Output compression**: Consider compressing JSONL output as it grows
5. **Metrics collection**: Add requests/sec, error rates, latency percentiles to logs
6. **Circuit breaker**: Temporarily skip domains that consistently fail (timeouts/connect errors)

### Safety Measures:
1. **Checkpoint frequency**: Ensure BATCH_SIZE balanced with restart cost
2. **Memory monitoring**: Watch RAM usage of processed/written sets at scale
3. **Error tracking**: Log and alert on failure rates (>5% may indicate issues)
4. **Rate limit compliance**: Respect 429 responses and implement exponential backoff
5. **Resource limits**: Check ulimit -n (file descriptors) for high concurrency

## Files to Reference:
- `/Users/latentspaceman/Documents/well-knowns/well-knowns-openclaw-plan.md` - Business context and crawling strategy
- `/Users/latentspaceman/Documents/well-knowns/data/domains.txt` - Current domain list (50 entries)
- `/Users/latentspaceman/Documents/well-knowns/data/ranks.txt` - Domain rank data
- `/Users/latentspaceman/Documents/well-knowns/well_knowns/crawl.py` - Current crawler
- `/Users/latentspaceman/Documents/well-knowns/well_knowns/crawl_improved.py` - Optimized crawler

## Next Steps:
1. Obtain Tranco top-1m.csv or similar 1M domain list
2. Replace domains.txt with the 1M domain list
3. Run crawl_improved.py on a 10k subset to validate performance
4. Monitor logs for errors, rate limits, and resource usage
5. Adjust CONCURRENT_LIMIT/BATCH_SIZE based on observations
6. Scale up to full 1M run once baseline established