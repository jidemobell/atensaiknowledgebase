Observer Configuration Issue - Case Study

Problem:
File observer not detecting configuration changes in mounted ConfigMaps.
Topology data becoming stale as configuration updates weren't being processed.

Environment:
- Kubernetes 1.25
- ASM Observer version 1.8.1
- ConfigMap mount path: /etc/asm/config
- File observer polling interval: 30s

Symptoms:
- Configuration changes not reflected in topology
- Observer logs showing "No changes detected"
- Manual restart required to pick up new config
- Inconsistent behavior across different environments

Investigation:
1. Checked file observer configuration - polling interval correct
2. Verified ConfigMap mount permissions - 644 permissions found
3. Analyzed inode changes - ConfigMap symlink updates not detected
4. Tested with different file watching mechanisms

Root Cause:
Kubernetes ConfigMap updates create new symlinks rather than modifying files in-place.
The file observer was monitoring the original file path, not following symlink changes.

Solution:
1. Modified observer to watch the parent directory instead of specific files
2. Implemented symlink resolution in file watcher
3. Added recursive directory monitoring
4. Updated observer restart policy for configuration failures

Code Changes:
```go
// Updated file watcher to handle symlinks
watcher.Add(filepath.Dir(configPath))
// Added symlink resolution
realPath, err := filepath.EvalSymlinks(configPath)
```

Configuration:
```yaml
file-observer:
  watch:
    directories: ["/etc/asm/config"]
    recursive: true
    followSymlinks: true
  polling:
    interval: 10s
```

Results:
- Configuration changes detected within 10 seconds
- No manual restarts required
- Consistent behavior across all environments
- Improved observability with better logging

Related Components: file-observer, kubernetes-observer, config-manager