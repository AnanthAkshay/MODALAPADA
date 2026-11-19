/**
 * Unit Tests for ASR Routing Logic
 * Verifies:
 * 1. Native missing -> fallback
 * 2. Native 'network' or 'service-not-allowed' error -> fallback
 * 3. Native available and OK -> no fallback (native primary)
 * 4. Brave browser -> fallback
 * 5. Session force fallback -> fallback
 */

import { determineAsrRoute } from './asrRouter.js';

function runTests() {
  let passed = 0;
  let failed = 0;

  function assert(condition, message) {
    if (condition) {
      console.log(`  [PASS] ${message}`);
      passed++;
    } else {
      console.error(`  [FAIL] ${message}`);
      failed++;
    }
  }

  console.log('--- Running ASR Routing Unit Tests ---');

  // Test 1: Native missing -> fallback
  {
    const res = determineAsrRoute({
      hasNativeSpeech: false,
      isBrave: false,
      sessionForceFallback: false
    });
    assert(res.route === 'fallback', 'Native missing routes to fallback');
    assert(res.reason === 'native_unsupported', 'Reason is native_unsupported');
  }

  // Test 2: Native 'network' error -> fallback with friendly notice
  {
    const res = determineAsrRoute({
      hasNativeSpeech: true,
      isBrave: false,
      sessionForceFallback: false,
      lastNativeError: 'network'
    });
    assert(res.route === 'fallback', 'Native network error routes to fallback');
    assert(res.reason === 'native_network_error', 'Reason is native_network_error');
    assert(
      res.friendlyNotice && res.friendlyNotice.includes("built-in speech service"),
      'Friendly notice is provided for network error'
    );
  }

  // Test 3: Native 'service-not-allowed' error -> fallback
  {
    const res = determineAsrRoute({
      hasNativeSpeech: true,
      isBrave: false,
      sessionForceFallback: false,
      lastNativeError: 'service-not-allowed'
    });
    assert(res.route === 'fallback', 'Native service-not-allowed routes to fallback');
    assert(res.reason === 'native_network_error', 'Reason is native_network_error');
  }

  // Test 4: Native OK -> no fallback (Chrome/Edge primary)
  {
    const res = determineAsrRoute({
      hasNativeSpeech: true,
      isBrave: false,
      sessionForceFallback: false,
      lastNativeError: null
    });
    assert(res.route === 'native', 'Native available routes to native (Chrome/Edge primary)');
    assert(res.reason === 'native_available', 'Reason is native_available');
  }

  // Test 5: Brave browser -> direct fallback
  {
    const res = determineAsrRoute({
      hasNativeSpeech: true,
      isBrave: true,
      sessionForceFallback: false
    });
    assert(res.route === 'fallback', 'Brave browser routes directly to fallback');
    assert(res.reason === 'brave_browser', 'Reason is brave_browser');
  }

  // Test 6: Session force fallback -> fallback remembered
  {
    const res = determineAsrRoute({
      hasNativeSpeech: true,
      isBrave: false,
      sessionForceFallback: true
    });
    assert(res.route === 'fallback', 'Session force fallback remembers fallback');
    assert(res.reason === 'session_forced', 'Reason is session_forced');
  }

  console.log(`--- Results: ${passed} Passed, ${failed} Failed ---`);
  if (failed > 0) process.exit(1);
}

runTests();
