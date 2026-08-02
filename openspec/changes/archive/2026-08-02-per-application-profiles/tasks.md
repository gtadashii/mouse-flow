## 1. Domain Model Updates

- [x] 1.1 Add `GLOBAL_PROFILE_NAME` constant to domain.py (e.g., `"global"`)
- [x] 1.2 Update `Configuration.get_profile()` to support retrieving global profile
- [x] 1.3 Add `Configuration.get_global_profile()` method to explicitly retrieve global profile
- [x] 1.4 Write tests for Configuration global profile retrieval

## 2. Profile Resolver Component

- [x] 2.1 Create `ProfileResolver` protocol in domain.py or new module
- [x] 2.2 Implement `DefaultProfileResolver` class with resolve method
- [x] 2.3 Write tests for application-specific profile selection
- [x] 2.4 Write tests for global profile fallback when no app-specific profile exists
- [x] 2.5 Write tests for deterministic precedence (app-specific always wins)
- [x] 2.6 Write tests for no profile available case
- [x] 2.7 Write tests for null window info handling

## 3. Configuration Parser Updates

- [x] 3.1 Update YAML parser to recognize `global:` key
- [x] 3.2 Translate `global:` section into Profile with GLOBAL_PROFILE_NAME
- [x] 3.3 Add validation to prevent application name collision with "global"
- [x] 3.4 Write tests for parsing global profile from YAML
- [x] 3.5 Write tests for backward compatibility (configs without global key)
- [x] 3.6 Write tests for global profile name collision validation

## 4. Configuration Loader Updates

- [x] 4.1 Modify `resolve_action()` to accept a Profile instead of Configuration
- [x] 4.2 Update loader to work with selected profile from ProfileResolver
- [x] 4.3 Write tests for action resolution with selected profile
- [x] 4.4 Write tests for action resolution when no profile is selected

## 5. Pipeline Integration

- [x] 5.1 Update `__main__.py` to instantiate ProfileResolver
- [x] 5.2 Integrate ProfileResolver into event processing loop
- [x] 5.3 Update dispatch flow to resolve profile before resolving action
- [x] 5.4 Write integration tests for full pipeline with global fallback
- [x] 5.5 Write integration tests for pipeline with application-specific profile

## 6. User Feedback and Reporting

- [x] 6.1 Update output format to include selected profile name
- [x] 6.2 Add profile selection reporting to dispatch context formatting
- [x] 6.3 Write tests for profile selection reporting

## 7. Documentation and Examples

- [x] 7.1 Update example config.yaml to include global profile example
- [x] 7.2 Update architecture.md with ProfileResolver component
- [x] 7.3 Update pipeline diagram to show profile resolution stage
