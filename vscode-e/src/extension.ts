import * as vscode from "vscode";

function quoteIfNeeded(s: string): string {
    if (s.includes(" ")) {
        return `"${s}"`;
    }
    return s;
}

function resolveScriptPath(configured: string, workspacePath: string | undefined): string {
    if (configured.includes(":") || configured.startsWith("/") || configured.startsWith("\\")) {
        return configured;
    }
    if (workspacePath) {
        const sep = workspacePath.includes("\\") ? "\\" : "/";
        return `${workspacePath}${sep}${configured.replace(/[\/\\]/g, sep)}`;
    }
    return configured;
}

export function activate(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand("e.runFile", () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage("E: No active editor. Open a .e file first.");
            return;
        }
        if (editor.document.languageId !== "e") {
            vscode.window.showErrorMessage(
                `E: Active file is '${editor.document.languageId}', not 'e'. Open a .e file.`
            );
            return;
        }

        const config = vscode.workspace.getConfiguration("e");
        const pythonPath = config.get<string>("pythonPath", "python");
        const scriptPathConfig = config.get<string>("scriptPath", "./e.py");
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        const scriptPath = resolveScriptPath(scriptPathConfig, workspaceFolder);
        const filePath = editor.document.uri.fsPath;

        const cmd = `${quoteIfNeeded(pythonPath)} ${quoteIfNeeded(scriptPath)} ${quoteIfNeeded(filePath)}`;

        const terminal = vscode.window.createTerminal({ name: "E" });
        terminal.show();
        terminal.sendText(cmd, true);
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
