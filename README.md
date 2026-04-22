# Go To File

Open file path under cursor in Sublime Text.

If path resolves to a single file in current project, it is opened right away.
If several files match, you get a quick panel to choose one.

Supported forms:

```text
path/to/file.py
path/to/file.py:42
"path/to/file.py"
'/absolute/path/to/file.py'
```

If no path is found or nothing matches, the plugin falls back to Sublime's
`goto_definition` command by default. You can change that in
`GoToFile.sublime-settings`:

```js
{
    "fallback_command": "goto_definition",
    "fallback_args": {},
    "excluded_dirs": [".git", "node_modules", "__pycache__", ".venv"]
}
```

Project files are cached for a few minutes to avoid walking the same folders on
every command run.

