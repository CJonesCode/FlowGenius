# BugIt MCP Integration with Cursor IDE

**Complete setup guide for using BugIt's MCP server with Cursor IDE**

## Overview

Cursor IDE supports the Model Context Protocol (MCP) for extending AI capabilities with custom tools. This guide shows how to configure Cursor to use BugIt's MCP server, giving you instant access to AI-powered bug tracking directly within your development environment.

**🔄 Updated**: Now using the official MCP Python SDK with `@tool` decorators for maximum compatibility with Cursor IDE and other MCP clients.

**🔌 Communication Method**: MCP uses JSON-RPC 2.0 over **stdio** (stdin/stdout), not HTTP ports. Cursor launches the server as a subprocess and communicates through pipes.

**🌍 Cross-Platform**: BugIt works on Windows, macOS, and Linux with proper file locking, path handling, and platform-specific adaptations.

## Prerequisites

- ✅ Cursor IDE installed and configured
- ✅ BugIt project cloned and set up
- ✅ Python environment with BugIt dependencies installed
- ✅ OpenAI API key configured (see BugIt configuration guide)

## Quick Setup for FlowGenius Project

**For your current Windows setup (`C:\Gauntlet\FlowGenius` with virtual environment):**

1. **Locate Cursor config file:**
   ```
   %APPDATA%\Cursor\User\globalStorage\cursor.mcp\config.json
   ```

2. **Use this cross-platform configuration:**
   
   **Option A: Universal with Virtual Environment (Recommended):**
   
   **For Unix/Linux/macOS:**
   ```json
   {
     "servers": {
       "bugit": {
         "command": "${workspaceFolder}/.venv/bin/python",
         "args": ["-m", "mcp_local.fastmcp_server"],
         "cwd": "${workspaceFolder}",
         "env": {
           "PYTHONPATH": "${workspaceFolder}"
         }
       }
     }
   }
   ```
   
   **For Windows:**
   ```json
   {
     "servers": {
       "bugit": {
         "command": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
         "args": ["-m", "mcp_local.fastmcp_server"],
         "cwd": "${workspaceFolder}",
         "env": {
           "PYTHONPATH": "${workspaceFolder}"
         }
       }
     }
   }
   ```
   
   **Option B: Global Python (Only if venv activated globally):**
   ```json
   {
     "servers": {
       "bugit": {
         "command": "python",
         "args": ["-m", "mcp"],
         "cwd": "${workspaceFolder}",
         "env": {
           "PYTHONPATH": "${workspaceFolder}"
         }
       }
     }
   }
   ```

3. **Open FlowGenius as workspace in Cursor**
   - File → Open Folder → Select your BugIt project directory
   - This ensures `${workspaceFolder}` resolves correctly

4. **Restart Cursor IDE**

5. **Test with:** "Can you help me create a bug report?"

**Why virtual environment paths are essential:**
- ✅ **Isolated Dependencies**: Uses BugIt's specific Python environment with all packages
- ✅ **Cross-Platform**: Platform-specific paths work automatically
- ✅ **No Global Activation**: Doesn't require activating venv system-wide
- ✅ **Team-Friendly**: Same config pattern works for all team members
- ✅ **Reliable**: Guaranteed access to all BugIt modules and dependencies

**Note**: Option B (global python) only works if you've activated the `.venv` environment globally before starting Cursor.

## Relative Path Solutions

### Option 1: Virtual Environment Configuration (Recommended)

**Uses project's virtual environment automatically:**

**Unix/Linux/macOS:**
```json
{
  "servers": {
    "bugit": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "mcp"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

**Windows:**
```json
{
  "servers": {
    "bugit": {
      "command": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

**Requirements:**
- Open your BugIt project as workspace in Cursor
- No need to activate virtual environment globally
- Works on Windows, macOS, Linux

### Option 1b: Platform-Specific Paths

**Automatically uses correct Python executable:**

**Unix/Linux/macOS:**
```json
{
  "servers": {
    "bugit": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "mcp"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

**Windows:**
```json
{
  "servers": {
    "bugit": {
      "command": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

### Option 2: Environment Variable Configuration

**Set environment variables first:**

```bash
# Windows PowerShell
$env:BUGIT_PROJECT_PATH = "C:\Gauntlet\FlowGenius"
$env:BUGIT_PYTHON_PATH = "C:\Gauntlet\FlowGenius\venv\Scripts\python.exe"

# Or add to System Environment Variables permanently
```

**Then use in Cursor config:**

```json
{
  "servers": {
    "bugit": {
      "command": "${BUGIT_PYTHON_PATH}",
      "args": ["-m", "mcp"],
      "cwd": "${BUGIT_PROJECT_PATH}",
      "env": {
        "PYTHONPATH": "${BUGIT_PROJECT_PATH}"
      }
    }
  }
}
```

### Option 3: Multiple Project Setup

**If you have multiple BugIt projects:**

```json
{
  "servers": {
    "bugit-flowgenius": {
      "command": "python",
      "args": ["-m", "mcp"],
      "cwd": "C:\\Gauntlet\\FlowGenius",
      "env": {
        "PYTHONPATH": "C:\\Gauntlet\\FlowGenius"
      }
    },
    "bugit-other-project": {
      "command": "python", 
      "args": ["-m", "mcp"],
      "cwd": "C:\\Projects\\OtherProject",
      "env": {
        "PYTHONPATH": "C:\\Projects\\OtherProject"
      }
    }
  }
}
```

### Option 4: Portable Configuration

**For truly portable setup:**

```json
{
  "servers": {
    "bugit": {
      "command": "python",
      "args": ["-m", "mcp"],
      "cwd": ".",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

**Requirements:**
- Start Cursor from your BugIt project directory
- Python and dependencies available in PATH

## Step 1: Locate Cursor Configuration

Cursor stores MCP server configurations in a JSON file:

**Windows:**
```
%APPDATA%\Cursor\User\globalStorage\cursor.mcp\config.json
```

**macOS:**
```
~/Library/Application Support/Cursor/User/globalStorage/cursor.mcp/config.json
```

**Linux:**
```
~/.config/Cursor/User/globalStorage/cursor.mcp/config.json
```

## Step 2: Configure BugIt MCP Server

Create or edit the `config.json` file with the following configuration:

```json
{
  "servers": {
    "bugit": {
      "command": "python",
      "args": ["-m", "mcp"],
      "cwd": "/path/to/your/bugit/project",
      "env": {
        "PYTHONPATH": "/path/to/your/bugit/project"
      }
    }
  }
}
```

### Configuration Options

**For Windows (PowerShell):**
```json
{
  "servers": {
    "bugit": {
      "command": "python",
      "args": ["-m", "mcp"],
      "cwd": "C:\\Gauntlet\\FlowGenius",
      "env": {
        "PYTHONPATH": "C:\\Gauntlet\\FlowGenius"
      }
    }
  }
}
```

**For Virtual Environment:**
```json
{
  "servers": {
    "bugit": {
      "command": "C:\\Gauntlet\\FlowGenius\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp"],
      "cwd": "C:\\Gauntlet\\FlowGenius",
      "env": {
        "PYTHONPATH": "C:\\Gauntlet\\FlowGenius"
      }
    }
  }
}
```

**For Debug Mode:**
```json
{
  "servers": {
    "bugit": {
      "command": "python",
      "args": ["-m", "mcp", "--debug"],
      "cwd": "/path/to/your/bugit/project",
      "env": {
        "PYTHONPATH": "/path/to/your/bugit/project"
      }
    }
  }
}
```

## Step 3: Restart Cursor

After saving the configuration file, restart Cursor IDE completely to load the new MCP server configuration.

## Step 4: Verify Integration

1. **Open Cursor IDE**
2. **Start a new chat with the AI**
3. **Type a message that would trigger tool usage**

Example verification prompt:
```
"Can you help me create a bug report for an issue I'm experiencing?"
```

If configured correctly, Cursor's AI should now have access to BugIt's tools and can create issues directly.

## Available BugIt Tools in Cursor

Once integrated, Cursor's AI can use these BugIt tools:

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `create_issue` | Create bug reports | "Create a bug report for login issues" |
| `list_issues` | List existing issues | "Show me all critical bugs" |
| `get_issue` | Get specific issue details | "Show me details for issue #1" |
| `update_issue` | Update existing issues | "Mark issue #1 as resolved" |
| `delete_issue` | Delete issues | "Delete issue #2" |
| `get_config` | Get BugIt configuration | "Show BugIt configuration" |
| `set_config` | Update configuration | "Set BugIt model to gpt-4" |
| `get_storage_stats` | Get storage statistics | "Show BugIt storage stats" |

## Example Usage in Cursor

### Creating a Bug Report
```
You: "I found a bug where the login button doesn't work on mobile devices. Can you create a bug report for this?"

Cursor AI: I'll create a bug report for the mobile login issue.

[AI calls create_issue tool]

The bug report has been created successfully:
- ID: a1b2c3d4
- Title: "Mobile login button non-functional"
- Severity: High
- Tags: mobile, login, ui
- Status: Open
```

### Listing Issues
```
You: "Show me all the critical bugs we have"

Cursor AI: I'll check for all critical severity issues.

[AI calls list_issues tool with severity filter]

Here are all critical bugs:
1. [a1b2c3d4] Mobile login button non-functional
2. [e5f6g7h8] Database connection timeout
3. [i9j0k1l2] Payment processing failure
```

### Updating Issues
```
You: "Mark the mobile login bug as resolved - we fixed it in the latest update"

Cursor AI: I'll update the mobile login issue to resolved status.

[AI calls update_issue tool]

Issue a1b2c3d4 has been updated:
- Status changed from "open" to "resolved"
- Updated timestamp: 2024-01-15T14:30:00Z
```

## Transport Details

**🔌 No Network Ports**: MCP uses JSON-RPC 2.0 over stdio (stdin/stdout), not HTTP:

- **Communication**: Process-to-process through pipes
- **Input**: JSON-RPC requests from Cursor → MCP server stdin
- **Output**: JSON-RPC responses from MCP server stdout → Cursor
- **Advantages**: Fast, secure, no network configuration needed

**Example JSON-RPC communication:**
```json
// Request (Cursor → MCP server)
{"jsonrpc": "2.0", "method": "tools/list", "id": 1}

// Response (MCP server → Cursor)  
{"jsonrpc": "2.0", "id": 1, "result": {"tools": [...]}}
```

## Troubleshooting

### Common Issues

**1. Server Not Found**
```
Error: MCP server "bugit" not found
```
**Solution:** Check that the path in `cwd` is correct and BugIt is installed in that location.

**2. Python Command Not Found**
```
Error: 'python' is not recognized as an internal or external command
```
**Solution:** Use full path to Python executable or ensure Python is in PATH.

**3. Import Errors**
```
Error: No module named 'mcp'
```
**Solution:** 
- Verify PYTHONPATH is set correctly
- Ensure you're using the correct Python environment
- Install BugIt dependencies: `pip install -r requirements.txt`

**4. API Key Issues**
```
Error: OpenAI API key not found
```
**Solution:** Configure BugIt API key:
```bash
cd /path/to/bugit
python cli.py config --set-api-key openai YOUR_API_KEY
```

**5. Working Directory Issues**
```
Error: No such file or directory
```
**Solution:** Use absolute paths or ensure `cwd` is set correctly:
```json
{
  "cwd": "C:\\Gauntlet\\FlowGenius",  // Absolute path
  "env": {
    "PYTHONPATH": "C:\\Gauntlet\\FlowGenius"  // Match cwd
  }
}
```

### Debug Mode

Enable debug mode to see detailed MCP communication:

```json
{
  "servers": {
    "bugit": {
      "command": "python",
      "args": ["-m", "mcp", "--debug"],
      "cwd": "/path/to/your/bugit/project"
    }
  }
}
```

Check Cursor's developer console (Help → Toggle Developer Tools) for MCP debug logs.

### Manual Testing

Test BugIt MCP server manually before configuring Cursor:

```bash
# Terminal 1: Start the server
cd /path/to/bugit
python -m mcp --debug

# Terminal 2: Test with curl or manual input
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | python -m mcp
```

## Advanced Configuration

### Multiple BugIt Projects

If you work with multiple BugIt projects, configure separate servers:

```json
{
  "servers": {
    "bugit-project1": {
      "command": "python",
      "args": ["-m", "mcp"],
      "cwd": "/path/to/project1/bugit"
    },
    "bugit-project2": {
      "command": "python",
      "args": ["-m", "mcp"],
      "cwd": "/path/to/project2/bugit"
    }
  }
}
```

### Custom Environment Variables

Add environment variables for different configurations:

```json
{
  "servers": {
    "bugit": {
      "command": "python",
      "args": ["-m", "mcp"],
      "cwd": "/path/to/bugit",
      "env": {
        "PYTHONPATH": "/path/to/bugit",
        "BUGIT_ENV": "development",
        "BUGIT_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Best Practices

### 1. Use Absolute Paths
Always use absolute paths in the configuration to avoid path resolution issues.

### 2. Virtual Environment
If using a virtual environment, point to the specific Python executable:
```json
"command": "/path/to/venv/bin/python"
```

### 3. Test Configuration
Always test the MCP server manually before integrating with Cursor.

### 4. Debug Mode for Development
Use debug mode during development to troubleshoot issues:
```json
"args": ["-m", "mcp", "--debug"]
```

### 5. Environment Separation
Use different configurations for different environments (dev, staging, prod).

## Integration Examples

### Automated Bug Creation from Code Comments
```python
# TODO: This function needs error handling - create bug report
def process_payment(amount):
    # AI can detect this comment and offer to create a bug report
    return charge_card(amount)
```

### Code Review Integration
```
You: "I'm reviewing this code and found several issues. Can you help me create bug reports for them?"

Cursor AI: I'll help you create bug reports for the issues you found. Please describe each issue and I'll create appropriate bug reports using BugIt.
```

### Sprint Planning
```
You: "Show me all open bugs for our next sprint planning"

Cursor AI: I'll get all open issues from BugIt for your sprint planning.

[Lists all open issues with priorities and tags]
```

## Conclusion

With BugIt's MCP server integrated into Cursor, you now have seamless AI-powered bug tracking directly within your development environment. The AI can:

- ✅ Create bug reports from natural language descriptions
- ✅ List and filter existing issues
- ✅ Update issue statuses and details
- ✅ Provide insights from your bug tracking data
- ✅ Automate bug management workflows

This integration transforms BugIt from a standalone CLI tool into a first-class citizen of your AI-powered development workflow!

## Next Steps

1. **Configure the MCP server** following the steps above
2. **Test the integration** with simple bug creation
3. **Explore advanced workflows** like automated issue creation from code comments
4. **Customize the configuration** for your specific development environment

For additional support, check the main BugIt documentation or create an issue in the BugIt repository. 