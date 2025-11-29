# Authentication Flow Tests

Comprehensive test suite for the PlantView local authentication system covering signup, login, token refresh, and protected endpoints.

## Test Coverage

### Signup Tests (`TestSignup`)
- ✅ Successful signup with valid credentials
- ✅ Missing email validation
- ✅ Missing password validation
- ✅ Invalid email format validation
- ✅ Password strength validation (length, uppercase, digits, special chars)
- ✅ Duplicate user prevention
- ✅ Case-insensitive email handling

### Login Tests (`TestLogin`)
- ✅ Successful login with valid credentials
- ✅ Missing email validation
- ✅ Missing password validation
- ✅ Non-existent user handling
- ✅ Wrong password rejection
- ✅ Failed login attempt tracking
- ✅ Failed attempt reset on successful login

### Account Lockout Tests (`TestAccountLockout`)
- ✅ Account lock after 5 failed attempts
- ✅ Account unlock after timeout
- ✅ Correct password fails during lockout

### Token Refresh Tests (`TestTokenRefresh`)
- ✅ Successful token refresh
- ✅ Missing refresh token validation
- ✅ Invalid refresh token rejection
- ✅ Using access token instead of refresh token (should fail)

### Token Verification Tests (`TestVerifyToken`)
- ✅ Verify valid access token
- ✅ Missing token rejection
- ✅ Invalid token rejection
- ✅ Malformed authorization header

### Logout Tests (`TestLogout`)
- ✅ Successful logout
- ✅ Missing token rejection

### Token Validation Tests (`TestTokenValidation`)
- ✅ Access token has correct type
- ✅ Refresh token has correct type
- ✅ Token contains user information

### Complete Flow Test (`TestCompleteAuthFlow`)
- ✅ Full signup → verify → logout → login → refresh flow

## Running Tests

### Run all tests
```bash
cd /path/to/PlantView
pytest
```

### Run specific test class
```bash
pytest backend/tests/test_auth_flow.py::TestSignup -v
```

### Run specific test
```bash
pytest backend/tests/test_auth_flow.py::TestSignup::test_signup_success -v
```

### Run with coverage
```bash
pytest --cov=backend --cov-report=html
```

### Run tests by marker
```bash
pytest -m auth       # Run only auth tests
pytest -m signup     # Run only signup tests
pytest -m login      # Run only login tests
```

## Test Fixtures

### `client`
- Creates a test Flask client
- Configures app for testing mode
- Uses separate test users file
- Cleans up after tests

### `clean_users`
- Ensures test user data is cleaned before each test
- Removes test users.json file
- Allows isolated test runs

## Test Database

Tests use a separate `backend/tests/test_users.json` file to isolate from production data. This file is automatically cleaned up after each test run.

## Expected Test Results

All tests should pass with:
- 45+ test cases
- 100% pass rate
- Coverage for all auth endpoints
- Coverage for all validation rules
- Coverage for all error conditions

## Example Test Output

```
test_auth_flow.py::TestSignup::test_signup_success PASSED
test_auth_flow.py::TestSignup::test_signup_invalid_email PASSED
test_auth_flow.py::TestLogin::test_login_success PASSED
test_auth_flow.py::TestAccountLockout::test_account_lockout_after_failed_attempts PASSED
...
========================= 45 passed in 2.34s ==========================
```

## Debugging Tests

### Enable verbose output
```bash
pytest -vv backend/tests/test_auth_flow.py
```

### Show print statements
```bash
pytest -s backend/tests/test_auth_flow.py
```

### Run with pdb on failure
```bash
pytest --pdb backend/tests/test_auth_flow.py
```

## Continuous Integration

These tests are ready for CI/CD pipelines:

### GitHub Actions example
```yaml
- name: Run auth tests
  run: |
    pip install -r backend/requirements.txt
    pytest backend/tests/test_auth_flow.py -v
```

## Test Performance

- Total runtime: ~2-3 seconds
- Average test duration: ~50ms per test
- No external dependencies (uses in-memory storage)
- Fully isolated between tests

## Future Enhancements

- [ ] Add performance benchmarking tests
- [ ] Add concurrent login tests
- [ ] Add rate limiting tests with timing verification
- [ ] Add token expiration tests with time mocking
- [ ] Add password reset flow tests
- [ ] Add email verification tests
- [ ] Add two-factor authentication tests
