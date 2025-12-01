# Performance Testing Guide

## Overview

This guide covers the comprehensive performance testing suite for Task 14.4 of the API Optimization spec.

## Test Requirements

The performance tests validate the following requirements:

- **Requirement 3.5**: Response time < 500ms for 95% of requests
- **Requirement 5.4**: Compression ratio > 60%
- **Requirement 6.5**: Cache hit rate monitoring
- **Load Testing**: System handles 1000 concurrent users

## Test Files

### 1. Master Test Runner
**File**: `run_performance_tests.py`

Executes all performance tests in sequence and generates a comprehensive report.

```bash
python run_performance_tests.py
```

This is the recommended way to run all tests.

### 2. Comprehensive Performance Tests
**File**: `test_comprehensive_performance.py`

Tests multiple aspects of performance:
- Response time validation (100 iterations per endpoint)
- Compression ratio testing
- Cache hit rate measurement
- Concurrent load testing (100 users)
- API metrics collection verification

```bash
python test_comprehensive_performance.py
```

**Expected Duration**: 2-3 minutes

### 3. Load Test with 1000 Users
**File**: `test_load_1000_users.py`

Simulates 1000 concurrent users making requests to test system scalability.

```bash
python test_load_1000_users.py
```

**Expected Duration**: 5-10 minutes
**Warning**: This is a heavy load test. Ensure the server can handle it.

### 4. Search API Performance
**File**: `test_search_performance.py`

Tests search endpoint performance with various query patterns.

```bash
python test_search_performance.py
```

**Expected Duration**: 30-60 seconds

### 5. CDN Performance Tests
**File**: `test_cdn_performance.py`

Tests CDN integration and cache effectiveness.

```bash
python test_cdn_performance.py
```

**Expected Duration**: 1-2 minutes

## Running the Tests

### Quick Start

1. Ensure Django server is running (if testing via HTTP):
   ```bash
   python manage.py runserver
   ```

2. Run the master test suite:
   ```bash
   python run_performance_tests.py
   ```

### Running Individual Tests

You can run individual test files directly:

```bash
# Response time and compression tests
python test_comprehensive_performance.py

# Heavy load testing
python test_load_1000_users.py

# Search-specific tests
python test_search_performance.py

# CDN tests
python test_cdn_performance.py
```

## Test Results Interpretation

### Response Time Tests

**Target**: < 500ms for 95% of requests

- **P50 (Median)**: Should be well under 500ms (typically 50-200ms)
- **P95**: Should be under 500ms
- **P99**: May exceed 500ms but should be under 1000ms

**Status Indicators**:
- ✓ PASS: ≥95% of requests under 500ms
- ✗ FAIL: <95% of requests under 500ms

### Compression Ratio Tests

**Target**: > 60% compression ratio

Tests gzip compression on JSON responses.

**Typical Results**:
- JSON responses: 70-85% compression
- HTML responses: 60-75% compression
- Already compressed data: 0-20% compression

**Status Indicators**:
- ✓ PASS: Average compression ≥60%
- ✗ FAIL: Average compression <60%

### Cache Hit Rate Tests

**Target**: Measurable and effective (>50% is good, >70% is excellent)

Measures how often requests are served from cache vs database.

**Interpretation**:
- 70-100%: Excellent cache effectiveness
- 50-70%: Good cache effectiveness
- 30-50%: Moderate cache effectiveness
- <30%: Poor cache effectiveness (needs tuning)

### Load Test Results

**Target**: Handle 1000 concurrent users with acceptable performance

**Key Metrics**:
- **Throughput**: Requests per second (target: ≥50 req/s)
- **Error Rate**: Should be <5%
- **Response Time**: P95 should remain under 500ms
- **Stability**: No crashes or timeouts

## Troubleshooting

### Tests Running Slowly

If tests are taking too long:

1. **Reduce iterations**: Edit test files to reduce iteration counts
2. **Run individual tests**: Focus on specific areas
3. **Check database**: Ensure database is optimized with proper indexes

### High Error Rates

If seeing many errors:

1. **Check server logs**: Look for exceptions in Django logs
2. **Verify database**: Ensure database has test data
3. **Check middleware**: Ensure all middleware is properly configured

### Poor Performance Results

If not meeting targets:

1. **Enable caching**: Ensure cache is properly configured
2. **Check database queries**: Look for N+1 queries
3. **Verify indexes**: Ensure database indexes are in place
4. **Review middleware order**: Ensure optimal middleware ordering

### Load Test Failures

If 1000 user test fails:

1. **Try smaller load**: Test with 100, 250, 500 users first
2. **Check system resources**: Monitor CPU, memory, database connections
3. **Increase timeouts**: May need to adjust timeout settings
4. **Scale infrastructure**: May need more resources for 1000 users

## Performance Optimization Tips

### If Response Times Are Slow

1. **Add database indexes**:
   ```python
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Enable query optimization**:
   - Use `select_related()` for ForeignKeys
   - Use `prefetch_related()` for ManyToMany
   - Use `only()` to limit fields

3. **Increase cache timeouts**:
   - Adjust cache TTL in `cache_manager.py`

### If Compression Is Low

1. **Check middleware order**:
   - GZipMiddleware should be near the top
   - Ensure it's before other response-modifying middleware

2. **Verify content types**:
   - Ensure JSON responses have correct Content-Type header

3. **Check minimum size**:
   - Responses must be >1KB to be compressed

### If Cache Hit Rate Is Low

1. **Verify cache configuration**:
   - Check `CACHES` setting in `settings.py`
   - Ensure cache backend is working

2. **Check cache invalidation**:
   - May be invalidating too aggressively
   - Review signal handlers

3. **Increase cache TTL**:
   - Adjust timeout values in cache calls

## Expected Results Summary

When all tests pass, you should see:

```
✓ ALL PERFORMANCE TESTS PASSED

The system meets all performance requirements:
  • Response times < 500ms for 95% of requests
  • Compression ratio > 60%
  • Cache hit rate is measurable and effective
  • System handles 1000 concurrent users
```

## Task Completion Checklist

- [ ] Run comprehensive performance tests
- [ ] Validate response times < 500ms for 95% of requests
- [ ] Verify compression ratio > 60%
- [ ] Measure cache hit rate
- [ ] Execute load test with 1000 concurrent users
- [ ] Review and document results
- [ ] Address any performance issues found
- [ ] Mark task 14.4 as complete

## Additional Resources

- **Django Performance**: https://docs.djangoproject.com/en/stable/topics/performance/
- **DRF Performance**: https://www.django-rest-framework.org/topics/performance/
- **Cache Framework**: https://docs.djangoproject.com/en/stable/topics/cache/
- **Database Optimization**: https://docs.djangoproject.com/en/stable/topics/db/optimization/

## Notes

- Tests use Django's test framework and don't require a running server
- Tests create temporary data and clean up after themselves
- For production testing, use dedicated load testing tools like Locust or JMeter
- Monitor system resources during load tests to identify bottlenecks
