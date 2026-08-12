---
name: scoop-skills
description: Use this skill to manage Windows packages via Scoop. Trigger this skill whenever the user mentions installing software, or whenever you need to execute a CLI tool that is not pre-installed on Windows but might have a Windows version available for discovery or installation via Scoop (e.g., git, curl, neovim, bat, etc.). This skill also helps you discover and execute the "shims" (executables) installed by Scoop, ensuring you know which command-line tools are available for use.
---

# Scoop Skill

This skill enables you to manage Windows software packages using the Scoop command-line installer. It provides a comprehensive reference for all Scoop commands and prioritizes the discovery of installed tools and their shims.

### Installation
If Scoop is not yet installed on the system, use the following PowerShell commands:
1. Set the execution policy:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
2. Run the installation script:
   ```powershell
   irm get.scoop.sh | iex
   ```

## All Scoop Commands Reference

### Package Management
- **Search**: `scoop search <query>` — Find available apps.
- **Install**: `scoop install <app> [options]` — Install apps (e.g., `-g` for global, `-i` to skip dependencies).
  - **After install**: If the installed app provides valuable third-party command-line tools (not a language or built-in tool), append to your global memory file in the `<!-- scoop-shims -->` comment block format: `- cmd: short description (from package)`
- **Uninstall**: `scoop uninstall <app> [options]` — Remove apps (e.g., `-p` to purge persistent data).
- **Update**: `scoop update <app>` — Update apps or Scoop itself (use `*` or `-a` for all).
- **List**: `scoop list [query]` — List all installed apps or those matching a query.
- **Status**: `scoop status` — Check for app updates and environmental issues.
- **Info**: `scoop info <app>` — Display detailed app information and manifests.
- **Home**: `scoop home <app>` — Open the app's homepage.
- **Depends**: `scoop depends <app>` — List dependencies for an app.
- **Download**: `scoop download <app>` — Download apps to the cache folder without installing.
- **Hold/Unhold**: `scoop hold <app>` / `scoop unhold <app>` — Disable/enable updates for an app.

### Backup and Restore
- **Export/Import**: `scoop export` / `scoop import <file>` — Standard JSON-based backup for app lists and buckets.
- **Manual Backup Restore**: If you have a backup of the entire `scoop` directory (e.g., from a previous system installation), follow these steps to restore:
  1. Copy the `scoop` folder to its target location (typically `~\scoop`).
  2. Set the `SCOOP` environment variable to point to this folder if it's not the default.
  3. Add `~\scoop\shims` to your system `PATH`.
  4. Run `scoop reset *` to re-link all applications and regenerate shims.
  5. *Note*: If you encounter "current" version errors, ensure the `current` directories within app folders are symlinks. If they are actual folders, delete the empty ones and run `scoop reset` again.

### Maintenance & Diagnostics
- **Help**: `scoop help [command]` — Show general help or help for a specific command.
- **Checkup**: `scoop checkup` — Identify potential problems in the Scoop environment.
- **Cleanup**: `scoop cleanup <app>` — Remove old versions of apps (use `*` for all).
- **Cache**: `scoop cache show|rm` — Show or clear the download cache.
- **Prefix**: `scoop prefix <app>` — Returns the filesystem path to the specified app.
- **Which**: `scoop which <command>` — Locate the path to a shim/executable (similar to 'which' on Linux).

### Configuration & Customization
- **Config**: `scoop config [rm] name [value]` — Get, set, or remove configuration values.
- **Bucket**: `scoop bucket add|list|known|rm` — Manage Scoop software repositories.
- **Alias**: `scoop alias add|rm|list` — Manage custom Scoop subcommands.

### Development & Advanced
- **Shim**: `scoop shim add|rm|list|info|alter` — Directly manipulate Scoop shims.
- **Reset**: `scoop reset <app>` — Reset an app to resolve conflicts or switch between versions.
- **Virustotal**: `scoop virustotal [*|app]` — Check app hashes or URLs on virustotal.com (requires API key).

#### Working with App Manifests
Scoop uses JSON manifests to define installation logic.
- **Inspect Manifest**: Use `scoop cat <app>` to see the manifest of an installed or available app.
- **Create Manifest**: Use `scoop create <url>` to generate a template or write a JSON file manually.
- **Install from File/URL**: `scoop install <path_to_json>` or `scoop install <url_to_json>`.
- **Basic Structure**:
  ```json
  {
      "version": "1.0",
      "url": "https://example.com/app.zip",
      "extract_dir": "app-folder",
      "bin": "app.exe",
      "description": "Short description",
      "homepage": "https://example.com",
      "license": "MIT"
  }
  ```

#### Manifest Resources & Reference
For detailed specifications, always consult the **local Wiki mirror** in `references/scoop-wiki/`:
- **Core Guide**: `references/scoop-wiki/App-Manifests.md`
- **Autoupdate Logic**: `references/scoop-wiki/App-Manifest-Autoupdate.md`
- **Buckets Reference**: `references/scoop-wiki/Buckets.md`
- **Live Examples**: Always run `scoop cat <app_name>` on a similar app to see its real manifest structure.

#### Manifest Development Tools
Internal scripts in `~\scoop\apps\scoop\current\bin` for testing and updates:
- **Check Version**: `~\scoop\apps\scoop\current\bin\checkver.ps1 <app>` — Check for newer versions via `checkver` logic.
- **Check Hashes**: `~\scoop\apps\scoop\current\bin\checkhashes.ps1 <app>` — Verify/Update hashes (use `-Update`).
- **Check URLs**: `~\scoop\apps\scoop\current\bin\checkurls.ps1 <app>` — Verify download URL availability.
- **Format JSON**: `~\scoop\apps\scoop\current\bin\formatjson.ps1 <file>` — Standardize manifest formatting.
- **Describe**: `~\scoop\apps\scoop\current\bin\describe.ps1 <app>` — Metadata analysis of a manifest.

## Discovering and Using Shims

Scoop uses "shims" to expose executables. If a tool's command is not found or you need to manage custom shims, use these methods:

### 1. List All Shims
- **List Shims**: `scoop shim list [<regex_pattern>]` — List all or matching shims.
- **Direct Directory Discovery**: To see all shim files (executables and scripts) directly:
  ```powershell
  dir $env:USERPROFILE\scoop\shims
  ```

### 2. Locate Paths and Details
- **Find Path**: `scoop which <command>` — Locate the path to a shim/executable (similar to 'which' on Linux).
- **Shim Info**: `scoop shim info <shim_name>` — Show details about a specific shim's target and arguments.

### 3. Shim Management (`scoop shim`)
- **Add Custom Shim**: 
  `scoop shim add <shim_name> <command_path> [<args>...]`
  *Note: Use a quoted `'--'` to separate shim-specific options from arguments you want to pass to the target executable.*
  Example: `scoop shim add myapp 'C:\path\app.exe' '--' --arg1 --arg2`
  - **After add**: If the new shim is a valuable third-party command-line tool (not a language or built-in tool), append to your global memory file in the `<!-- scoop-shims -->` comment block format: `- cmd: short description (from package)`
- **Remove Shim**: `scoop shim rm <shim_name>...` (Caution: can remove manifest-created shims).
- **Alter Shim**: `scoop shim alter <shim_name>` — Alternate a shim's target source.

## Best Practices
- **Environment Refresh**: If a newly installed command isn't recognized, check the shims directory or use the absolute path (e.g., `~\scoop\shims\tool.exe`).
- **Global Installation**: Use `-g` for apps that require administrative privileges or are used by multiple users.
- **Clear Cache**: Run `scoop cache rm *` after installations to free up disk space by removing downloaded installers.
- **Cleanup**: Regularly run `scoop cleanup *` to save disk space by removing old versions.
- **Deep Knowledge**: For any advanced questions, troubleshooting, or general guidance not covered here, consult the local Wiki mirror: `references/scoop-wiki/Home.md`.
