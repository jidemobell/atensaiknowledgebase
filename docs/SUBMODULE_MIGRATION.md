# 🔄 Submodule Migration Guide

## Overview
The project has migrated from using `openwebuibase` (pointing to a fork) to `open-webui-cloned` (pointing to upstream OpenWebUI). This ensures better compatibility and easier updates.

## For Existing Users

### 🚨 Important: Clean Migration Steps

If you already have this repository cloned with the old `openwebuibase` submodule, follow these steps:

#### Option 1: Fresh Clone (Recommended)
```bash
# 1. Backup any custom changes
cd /path/to/your/existing/TOPOLOGYKNOWLEDGE
cp -r logs/ ~/backup-topology-logs/  # backup logs if needed

# 2. Clone fresh repository
cd ..
git clone https://github.com/jidemobell/knowledgebase.git TOPOLOGYKNOWLEDGE-new
cd TOPOLOGYKNOWLEDGE-new

# 3. Run setup
./setup.sh

# 4. Copy back any custom data
cp -r ~/backup-topology-logs/* logs/ 2>/dev/null || true
```

#### Option 2: In-Place Migration
```bash
# 1. Stop any running services
echo "3" | ./start.sh  # Select STATUS CHECK to see what's running
# Then stop services manually if needed

# 2. Clean old submodule
git submodule deinit -f openwebuibase
git rm openwebuibase
rm -rf .git/modules/openwebuibase

# 3. Pull latest changes
git pull origin main

# 4. Initialize new submodule
git submodule update --init --recursive

# 5. Verify setup
./setup.sh
```

## What Changed

### Before (openwebuibase)
- Pointed to: `https://github.com/jidemobell/atensai-open-webui.git`
- Purpose: Custom fork with Knowledge Fusion integration
- Issue: Created dependency on fork, harder to sync with upstream

### After (open-webui-cloned)
- Points to: `https://github.com/open-webui/open-webui.git`
- Purpose: Direct upstream OpenWebUI with runtime Knowledge Fusion integration
- Benefit: Always up-to-date with latest OpenWebUI features

## File Structure Changes

```
Before:
├── openwebuibase/          # Submodule to fork
│   └── knowledge-fusion/   # Pre-integrated
└── start_server_mode.sh    # Uses openwebuibase

After:
├── open-webui-cloned/      # Submodule to upstream
└── start_server_mode.sh    # Uses open-webui-cloned
                            # Knowledge Fusion added at runtime
```

## Verification

After migration, verify everything works:

```bash
# 1. Check submodule status
git submodule status
# Should show: open-webui-cloned (v0.6.28 or later)

# 2. Test startup
./start.sh
# Select option 1: SERVER MODE

# 3. Verify services
curl http://localhost:3000   # OpenWebUI
curl http://localhost:8001   # Core Backend
curl http://localhost:8002   # Knowledge Fusion
```

## Benefits of New Structure

1. **Always Current**: Direct access to latest OpenWebUI features
2. **Simpler Maintenance**: No need to maintain separate fork
3. **Better Compatibility**: Reduced version conflicts
4. **Easier Collaboration**: Standard upstream reference

## Troubleshooting

### Submodule Issues
```bash
# If submodule shows as modified but shouldn't be:
cd open-webui-cloned
git reset --hard HEAD
git clean -fd
cd ..
git submodule update --init --recursive
```

### Knowledge Fusion Missing
- Knowledge Fusion is now installed at runtime during server startup
- No longer pre-integrated in the submodule
- Check `start_server_mode.sh` for installation logic

### Still Seeing openwebuibase References
```bash
# Clean any remaining references
git clean -fd
git reset --hard origin/main
git submodule update --init --recursive
```

## Support

If you encounter issues during migration:

1. Check this migration guide
2. Try the "Fresh Clone" option
3. Review logs in `logs/` directory
4. Check GitHub issues for similar problems

---

*Last updated: September 2025*
