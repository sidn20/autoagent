import os

WORKSPACE = os.path.expanduser("~/autoagent/workspace")
os.makedirs(WORKSPACE, exist_ok=True)

def write_file(filename: str, content: str) -> str:
    """Write content to a file in the workspace."""
    # Security — prevent path traversal attacks like ../../etc/passwd
    filename = os.path.basename(filename)
    filepath = os.path.join(WORKSPACE, filename)

    try:
        with open(filepath, "w") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {filename}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def read_file(filename: str) -> str:
    """Read content from a file in the workspace."""
    filename = os.path.basename(filename)
    filepath = os.path.join(WORKSPACE, filename)

    try:
        with open(filepath, "r") as f:
            content = f.read()
        return content if content else "File is empty"
    except FileNotFoundError:
        return f"Error: File '{filename}' not found in workspace"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files() -> str:
    """List all files in the workspace."""
    files = os.listdir(WORKSPACE)
    if not files:
        return "Workspace is empty"
    return "Files in workspace:\n" + "\n".join(f"  - {f}" for f in files)

def delete_file(filename: str) -> str:
    """Delete a file from the workspace."""
    filename = os.path.basename(filename)
    filepath = os.path.join(WORKSPACE, filename)

    try:
        os.remove(filepath)
        return f"Successfully deleted {filename}"
    except FileNotFoundError:
        return f"Error: File '{filename}' not found"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

def run(action_input: str) -> str:
    """
    Parse action input and route to correct function.
    Agent passes input like:
      'write: report.txt: This is the content'
      'read: report.txt'
      'list'
      'delete: report.txt'
    """
    action_input = action_input.strip()
    action_input = action_input.strip("'\"")  # remove quotes LLM adds
    if action_input.startswith("write:"):
        # Format: write: filename: content
        parts = action_input[len("write:"):].strip().split(":", 1)
        if len(parts) != 2:
            return "Error: Format should be 'write: filename: content'"
        filename, content = parts[0].strip(), parts[1].strip()
        return write_file(filename, content)

    elif action_input.startswith("read:"):
        filename = action_input[len("read:"):].strip()
        return read_file(filename)

    elif action_input.strip() == "list":
        return list_files()

    elif action_input.startswith("delete:"):
        filename = action_input[len("delete:"):].strip()
        return delete_file(filename)

    else:
        return f"Error: Unknown file action. Use write/read/list/delete"

if __name__ == "__main__":
    print("File Tool Tests:")
    print("=" * 40)

    print(run("list"))
    print(run("write: report.txt: This is a test report.\nIt has multiple lines."))
    print(run("write: notes.txt: Some quick notes here."))
    print(run("list"))
    print(run("read: report.txt"))
    print(run("delete: notes.txt"))
    print(run("list"))
    print(run("read: missing.txt"))
