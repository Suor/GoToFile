import os
import re
import time
import sublime
import sublime_plugin


# LICENSE FindWordUpCommand
# "Reform/Default (Linux).sublime-keymap"
class GotoFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = self.view.window()

        path, line = _extract_path_at_cursor(self.view)
        # print("gtf extract", path, line)
        if not path:
            return self._fallback(window)

        matches = _resolve(path)
        # print("gtf matches", matches)
        if not matches:
            return self._fallback(window)
        elif len(matches) == 1:
            self._open(window, matches[0], line)
        else:
            folders = window.folders()
            items = [os.path.relpath(m, f) for m in matches
                     for f in folders if m.startswith(f + '/')]
            window.show_quick_panel(
                items or matches,
                lambda i: i >= 0 and self._open(window, matches[i], line))

    def _open(self, window, path, line):
        if line is not None:
            window.open_file('{}:{}'.format(path, line), sublime.ENCODED_POSITION)
        else:
            window.open_file(path)

    def _fallback(self, window):
        settings = _settings()
        window.run_command(settings.get('fallback_command', 'goto_definition'),
                           settings.get('fallback_args', {}))


_PATH_RE = re.compile(
    r'(["\'])([^"\']+)\1|(?:[a-zA-Z0-9_.\-]+/)*[a-zA-Z0-9_.\-]+(?:\.[a-zA-Z0-9]+)?(?::(\d+))?')


def _extract_path_at_cursor(view):
    pos = view.sel()[0].b
    line_region = view.line(pos)
    line = view.substr(line_region)
    col = pos - line_region.a

    for m in _PATH_RE.finditer(line):
        if m.start() <= col <= m.end():
            if m.group(2):  # quoted
                return m.group(2), None
            return m.group(0).split(':')[0], int(m.group(3)) if m.group(3) else None

    return None, None


def _settings():
    return sublime.load_settings('GoToFile.sublime-settings')


def _resolve(path):
    if not path:
        return []

    # Absolute
    if os.path.isabs(path) and os.path.isfile(path):
        return [path]

    # Direct match under project folders
    for folder in sublime.active_window().folders():
        full = os.path.join(folder, path)
        if os.path.isfile(full):
            return [full]

    # Partial match across all project files
    suffix = '/' + path
    return [fp for fp in _project_files() if fp.endswith(suffix)]


def _project_files():
    return [fp for folder in sublime.active_window().folders() for fp in _walk(folder)]


_file_cache = {}  # folder -> (time, files)


def _walk(folder):
    cached = _file_cache.get(folder)
    if cached and time.monotonic() - cached[0] < 300:
        return cached[1]

    excluded = _settings().get('excluded_dirs', [])
    files = []
    for root, dirs, names in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in excluded]
        files += [os.path.join(root, name) for name in names]
    _file_cache[folder] = (time.monotonic(), files)
    return files
