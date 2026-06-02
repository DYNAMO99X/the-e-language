# E Language — VSCode Extension

A small VSCode extension that adds **syntax highlighting** and a **Run
File** command for `.e` files (the E programming language).

## Features

### 1. Syntax highlighting

Keywords (`let`, `be`, `say`, `if`, `is greater than or equal to`,
etc.), strings (all 3 quote types — `"`, `'`, `` ` ``), numbers,
turtle commands (`move`, `pen color`, `forward`), and built-in
functions (`ask`, `number`, `random`) are all colored.

Multi-word keywords like `is greater than or equal to` are matched as
a single phrase (longest-match priority), not as six separate
keywords.

### 2. Run File

With a `.e` file open:

- **Press Ctrl+F5** (default keybinding)
- **Or** click the ▶ play icon in the editor toolbar
- **Or** open the Command Palette and run `E: Run File`

The extension opens an integrated terminal and runs
`python e.py <current-file>`. Output appears in the terminal.

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `e.pythonPath` | `python` | The Python executable to use. Change to `python3`, `py`, or an absolute path. |
| `e.scriptPath` | `./e.py` | Path to the E interpreter. Relative to the workspace root, or absolute. |

**Example** — point the extension at a global install of E:

```json
{
  "e.scriptPath": "C:\\E\\e.py"
}
```

## Install

### From a local `.vsix` (this folder)

```bash
cd vscode-e
npm install
npx vsce package
code --install-extension e-lang-0.1.0.vsix
```

Or run the top-level `build-extension.bat`.

## Build

The same `vsce package` command rebuilds the `.vsix` after any
changes. The TypeScript source is in `src/extension.ts`; the grammar
is in `syntaxes/e.tmLanguage.json`.

```bash
cd vscode-e
npm run build     # compile TypeScript
npx vsce package  # build the .vsix
```

## Verify

1. **Install** the extension (above).
2. **Reload** VSCode (`Ctrl+Shift+P` → "Developer: Reload Window").
3. **Open** `examples/hello.e` from the E project — `say`, the string,
   and the trailing newline should all be colored.
4. **Open** `docs/lessons/06_choices.e` — `is greater than or equal
   to` should highlight as a single phrase.
5. **Open** `docs/lessons/05_turtle_basics.e` — `move`, `forward`,
   `pen color` should all be colored.
6. **Press Ctrl+F5** on any of the above — the terminal should run
   the file.

## Files

| File | Purpose |
|------|---------|
| `package.json` | Extension manifest |
| `syntaxes/e.tmLanguage.json` | TextMate grammar (the highlighting rules) |
| `language-configuration.json` | Brackets, comment style, auto-close |
| `src/extension.ts` | The "Run File" command (TypeScript) |
| `tsconfig.json` | TypeScript build config |
| `icon.png` | 128×128 extension icon |

## License

Personal project — use as you wish.
