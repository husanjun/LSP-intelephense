from .plugin import LspIntelephensePlugin
from LSP.plugin.core.typing import Optional, TypeVar
import os
import shutil
import sublime
import sublime_plugin

T = TypeVar("T")


def expand_variables(var: T, window: Optional[sublime.Window] = None) -> T:
    if not window:
        window = sublime.active_window()

    variables = window.extract_variables()
    variables.update(LspIntelephensePlugin.additional_variables() or {})

    return sublime.expand_variables(var, variables)


class LspIntelephenseClearCacheCommand(sublime_plugin.WindowCommand):
    """ Clear the cache generated by intelephense. """

    def run(self) -> None:
        settings = sublime.load_settings("LSP-intelephense.sublime-settings")

        cache_path = settings.get("initializationOptions", {}).get("storagePath", "")  # type: str
        cache_path = os.path.realpath(os.path.abspath(expand_variables(cache_path)))

        if not cache_path:
            return

        # delete all workspace caches since we don't know which one is for the current workspace
        #
        # the name of the current one can be obtained from the server message:
        #     window/logMessage: {'type': 3, 'message': 'Writing state to /tmp/intelephense/aedb86.'}
        #
        # but there seems no way to intercept that in LSP-intelephense
        for path in os.listdir(cache_path):
            full_path = os.path.join(cache_path, path)

            if os.path.isdir(full_path):
                shutil.rmtree(full_path, ignore_errors=True)


class LspIntelephenseReindexWorkspaceCommand(sublime_plugin.WindowCommand):
    """ Re-index the workspace. """

    def run(self) -> None:
        self.window.run_command("lsp_intelephense_clear_cache")
        # this will restart all servers but there is no arg to specify a certain server :shrug:
        self.window.run_command("lsp_restart_client")
