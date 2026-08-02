## Why

MouseFlow currently supports only application-specific profiles, requiring users to duplicate mappings across all applications or miss actions when switching contexts. A global fallback profile is needed to provide default mappings that apply when no application-specific profile exists, reducing configuration duplication and improving the user experience.

## What Changes

- New profile resolution layer that selects the appropriate profile based on the focused application
- Global profile support as a fallback when no application-specific profile matches
- Deterministic precedence rules: application-specific profiles take priority over global profile
- Profile selection reporting in user feedback
- Modified action resolution to consult the selected profile instead of only the application-specific profile

## Capabilities

### New Capabilities
- `profile-resolution`: Selects the appropriate profile (application-specific or global) based on the focused application, applying deterministic precedence rules and providing fallback behavior.

### Modified Capabilities
- `configuration-loader`: Action resolution now uses the selected profile from the profile resolution layer instead of directly looking up application-specific profiles. The loader receives the resolved profile and resolves actions from it.

## Impact

- **New module**: Profile resolution logic (may extend loader.py or create new module)
- **Domain**: Configuration domain object may need to expose global profile separately
- **Configuration format**: YAML structure may need to support a global profile section (e.g., `global:` key)
- **Pipeline**: Profile resolution becomes an explicit step between event dispatch and action resolution
- **Testing**: New tests for profile selection, precedence rules, and fallback behavior
- **Backward compatibility**: Existing application-specific configurations must continue to work unchanged
