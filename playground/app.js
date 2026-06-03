// ========== E Playground - Main Application ==========

let editor = null;
let pyodide = null;

// ========== E Language Definition for Monaco ==========
const E_LANG_DEF = {
    keywords: [
        'let', 'be', 'say', 'ask', 'if', 'then', 'else', 'end',
        'while', 'repeat', 'times', 'for', 'each', 'in', 'to',
        'return', 'true', 'false', 'nothing', 'and', 'or', 'not',
        'plus', 'minus', 'mod', 'is', 'divided', 'by',
        'at', 'with', 'added', 'size', 'of',
        'turtle', 'move', 'make', 'goto', 'set',
    ],
    operators: [
        '>', '<', '>=', '<=', '=', '==', '!=', '!==',
        '+', '-', '*', '/',
    ],
    symbols: ['>', '<', '>=', '<=', '=', '==', '!=', '!==', '+', '-', '*', '/', '(', ')', '[', ']'],
    tokenizer: {
        root: [
            [/--.*$/, 'comment'],
            [/"[^"]*"/, 'string'],
            [/'[^']*'/, 'string'],
            [/`[^`]*`/, 'string'],
            [/\d+(\.\d+)?/, 'number'],
            [/[a-zA-Z_]\w*/, {
                cases: {
                    '@keywords': 'keyword',
                    '@default': 'identifier',
                },
            }],
            [/[><=!=+\-*/(),\[\]]/, 'operator'],
            [/\s+/, 'white'],
        ],
    },
};

const E_LANG_CONFIG = {
    comments: { lineComment: '--' },
    brackets: [['(', ')'], ['[', ']']],
    autoClosingPairs: [
        { open: '(', close: ')' },
        { open: '[', close: ']' },
        { open: '"', close: '"' },
        { open: "'", close: "'" },
        { open: '`', close: '`' },
    ],
    surroundingPairs: [
        { open: '(', close: ')' },
        { open: '[', close: ']' },
        { open: '"', close: '"' },
        { open: "'", close: "'" },
        { open: '`', close: '`' },
    ],
};

// ========== Example Programs ==========
const EXAMPLES = {
    'Hello, World': `say "Hello, world!"`,

    'Calculator': `-- Calculator: English keywords OR symbol operators
let a be 12
let b be 4

-- Using English keywords
say "English: " , (a plus b) , " / " , (a minus b) , " / " , (a times b)

-- Using symbol operators
say "Symbols: " , (a + b) , " / " , (a - b) , " / " , (a * b)

-- Mixed
say "Mixed:   " , (a + b * 2) , " = 12 + 4*2"`,

    'Guessing Game': `-- Guessing game (simulated, no input in browser)
let secret be 42
let i be 0
say "The secret number is: " , secret
say ""

repeat 5 times
    let i be i plus 1
    let guess be (i times 10)
    say "Guess #" , i , ": " , guess

    if guess is less than secret then
        say "  Too low!"
    else if guess is greater than secret then
        say "  Too high!"
    else
        say "  You got it!"
    end
end`,

    'Fibonacci': `-- Fibonacci sequence
to fibonacci n
    if n <= 1 then
        return n
    end
    return fibonacci (n minus 1) plus fibonacci (n minus 2)
end

say "First 10 Fibonacci numbers:"
repeat 10 times
    let i be repeat count
    say fibonacci i
end`,

    'Turtle Spiral': `-- Colorful spiral with turtle
let ada be turtle
set ada pen color to "teal"
set ada pen size to 2

repeat 36 times
    move ada forward 20
    move ada right 100
end`,
};

// ========== Theme Definitions ==========
const THEMES = {
    dark: 'vs-dark',
    light: 'vs',
    teal: 'vs-dark',
};

// ========== Initialization ==========
async function init() {
    // Rotating loading messages
    const msgs = [
        'Warming up the E interpreter...',
        'Loading turtle graphics engine...',
        'Teaching the turtle new tricks...',
        'Translating English to Python...',
        'Almost ready to say hello!',
    ];
    const msgEl = document.getElementById('loading-msg');
    let msgIdx = 0;
    const msgTimer = setInterval(() => {
        msgEl.style.opacity = '0';
        setTimeout(() => {
            msgIdx = (msgIdx + 1) % msgs.length;
            msgEl.textContent = msgs[msgIdx];
            msgEl.style.opacity = '1';
        }, 300);
    }, 2200);

    // Initialize Monaco Editor
    await initMonaco();

    // Load Pyodide
    await initPyodide();

    // Set up event listeners
    setupEventListeners();

    // Load default example
    document.getElementById('example-select').value = 'Hello, World';
    loadExample('Hello, World');

    // Hide loading overlay
    clearInterval(msgTimer);
    document.getElementById('loading-overlay').classList.add('hidden');
}

async function initMonaco() {
    return new Promise((resolve) => {
        require.config({
            paths: { vs: 'https://unpkg.com/monaco-editor@0.45.0/min/vs' },
        });
        require(['vs/editor/editor.main'], () => {
            // Register E language
            monaco.languages.register({ id: 'e' });
            monaco.languages.setMonarchTokensProvider('e', E_LANG_DEF);
            monaco.languages.setLanguageConfiguration('e', E_LANG_CONFIG);

            // Create editor
            editor = monaco.editor.create(document.getElementById('editor'), {
                value: '',
                language: 'e',
                theme: THEMES.dark,
                automaticLayout: true,
                fontSize: 14,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                wordWrap: 'on',
                lineNumbers: 'on',
                renderLineHighlight: 'all',
                tabSize: 4,
            });

            // Ctrl+Enter to run
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, runCode);

            resolve();
        });
    });
}

async function initPyodide() {
    // Temporarily disable AMD loader to prevent Monaco/RequireJS from
    // intercepting Pyodide's module loading (fixes stackframe 404).
    const savedAmd = window.define?.amd;
    if (savedAmd) window.define.amd = null;

    pyodide = await loadPyodide();

    if (savedAmd) window.define.amd = savedAmd;

    // Load the E interpreter bundle
    const response = await fetch('e_bundle.py');
    const bundleCode = await response.text();
    pyodide.runPython(bundleCode);
}

function setupEventListeners() {
    // Run button
    document.getElementById('run-btn').addEventListener('click', runCode);

    // Example selector
    const select = document.getElementById('example-select');
    for (const name of Object.keys(EXAMPLES)) {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        select.appendChild(opt);
    }
    select.addEventListener('change', (e) => {
        if (e.target.value) loadExample(e.target.value);
    });

    // Theme selector
    document.getElementById('theme-select').addEventListener('change', (e) => {
        document.documentElement.setAttribute('data-theme', e.target.value);
        monaco.editor.setTheme(THEMES[e.target.value]);
    });

    // Clear buttons
    document.getElementById('clear-output').addEventListener('click', () => {
        document.getElementById('output').innerHTML = '';
    });
    document.getElementById('clear-turtle').addEventListener('click', clearTurtleCanvas);

    // Help modal
    const helpBtn = document.getElementById('help-btn');
    const helpModal = document.getElementById('help-modal');
    const modalBackdrop = helpModal.querySelector('.modal-backdrop');
    const modalClose = helpModal.querySelector('.modal-close');

    function openHelp() { helpModal.classList.remove('hidden'); }
    function closeHelp() { helpModal.classList.add('hidden'); }

    helpBtn.addEventListener('click', openHelp);
    modalClose.addEventListener('click', closeHelp);
    modalBackdrop.addEventListener('click', closeHelp);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !helpModal.classList.contains('hidden')) closeHelp();
    });

    // Resizable dividers
    initDividers();
}

// ========== Resizable Dividers ==========
function initDividers() {
    const dividerV = document.getElementById('divider-v');
    const dividerH = document.getElementById('divider-h');
    const editorPanel = document.querySelector('.editor-panel');
    const rightPanels = document.querySelector('.right-panels');
    const turtlePanel = document.querySelector('.turtle-panel');
    const outputPanel = document.querySelector('.output-panel');

    function startDrag(divider, direction) {
        divider.classList.add('active');
        document.body.classList.add(direction === 'col' ? 'dragging-col' : 'dragging-row');

        function onMove(e) {
            const clientXY = direction === 'col' ? e.clientX : e.clientY;
            const mainRect = document.querySelector('main').getBoundingClientRect();

            if (direction === 'col') {
                const offset = clientXY - mainRect.left;
                const total = mainRect.width;
                const minPx = 200;
                const pct = Math.max(minPx / total * 100, Math.min((total - minPx - 5) / total * 100, offset / total * 100));
                editorPanel.style.flex = '0 0 ' + pct + '%';
                rightPanels.style.flex = '1';
            } else {
                const mainTop = mainRect.top;
                const mainH = mainRect.height;
                const dividerH = divider.offsetHeight;
                const headerH = divider.previousElementSibling.querySelector('.panel-header').offsetHeight;
                const offset = clientXY - mainTop - headerH;
                const minT = 80;
                const minO = 60;
                const tPct = Math.max(minT / mainH * 100, Math.min((mainH - minO - dividerH) / mainH * 100, offset / mainH * 100));
                turtlePanel.style.flex = '0 0 ' + tPct + '%';
                outputPanel.style.flex = '1';
            }

            if (editor && editor.layout) editor.layout();
        }

        function onUp() {
            divider.classList.remove('active');
            document.body.classList.remove('dragging-col', 'dragging-row');
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
            if (editor && editor.layout) editor.layout();
        }

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
    }

    dividerV.addEventListener('mousedown', (e) => { e.preventDefault(); startDrag(dividerV, 'col'); });
    dividerH.addEventListener('mousedown', (e) => { e.preventDefault(); startDrag(dividerH, 'row'); });
}

// ========== Core Functions ==========
function loadExample(name) {
    if (EXAMPLES[name]) {
        editor.setValue(EXAMPLES[name]);
    }
}

async function runCode() {
    const code = editor.getValue();
    const outputEl = document.getElementById('output');
    outputEl.innerHTML = '';

    if (!code.trim()) return;

    try {
        // Run E code via Pyodide
        const result = pyodide.runPython(`
import json
output, turtle_data, error = run_e('''${code.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}''')
json.dumps({"output": output, "turtle": turtle_data, "error": error})
        `);

        const data = JSON.parse(result);

        // Display output
        if (data.output && data.output.length > 0) {
            for (const line of data.output) {
                const div = document.createElement('div');
                div.textContent = line;
                outputEl.appendChild(div);
            }
        }

        // Display error
        if (data.error) {
            const div = document.createElement('div');
            div.className = 'error';
            div.textContent = data.error;
            outputEl.appendChild(div);
        }

        // Render turtle
        if (data.turtle && Object.keys(data.turtle).length > 0) {
            renderTurtle(data.turtle);
        }
    } catch (e) {
        const div = document.createElement('div');
        div.className = 'error';
        div.textContent = 'Runtime error: ' + e.message;
        outputEl.appendChild(div);
    }
}

// ========== SVG Turtle Renderer ==========
function clearTurtleCanvas() {
    const svg = document.getElementById('turtle-canvas');
    svg.innerHTML = '';
}

function renderTurtle(turtleData) {
    clearTurtleCanvas();
    const svg = document.getElementById('turtle-canvas');

    for (const [name, data] of Object.entries(turtleData)) {
        const commands = data.log;
        let x = 0, y = 0, heading = 0;
        let penDown = true;
        let penColor = data.pen_color || 'black';
        let penSize = data.pen_size || 1;

        // Build path segments
        const segments = [];
        let currentSegment = [];

        for (const cmd of commands) {
            const line = cmd.replace(/^>> /, '').trim();
            const parts = line.split(' ');
            const action = parts[0];

            if (action === 'forward') {
                const dist = parseFloat(parts[1]);
                const rad = heading * Math.PI / 180;
                const newX = x + dist * Math.cos(rad);
                const newY = y + dist * Math.sin(rad);
                if (penDown) {
                    currentSegment.push({ x1: x, y1: y, x2: newX, y2: newY, color: penColor, size: penSize });
                }
                x = newX;
                y = newY;
            } else if (action === 'backward') {
                const dist = parseFloat(parts[1]);
                const rad = heading * Math.PI / 180;
                const newX = x - dist * Math.cos(rad);
                const newY = y - dist * Math.sin(rad);
                if (penDown) {
                    currentSegment.push({ x1: x, y1: y, x2: newX, y2: newY, color: penColor, size: penSize });
                }
                x = newX;
                y = newY;
            } else if (action === 'left') {
                heading = (heading + parseFloat(parts[1])) % 360;
            } else if (action === 'right') {
                heading = (heading - parseFloat(parts[1]) + 360) % 360;
            } else if (action === 'pen_up') {
                penDown = false;
            } else if (action === 'pen_down') {
                penDown = true;
            } else if (action === 'pen_color') {
                penColor = parts.slice(1).join(' ');
            } else if (action === 'pen_size') {
                penSize = parseFloat(parts[1]);
            } else if (action === 'go_to') {
                x = parseFloat(parts[1]);
                // y is after "and"
                const andIdx = parts.indexOf('and');
                if (andIdx > -1) {
                    y = parseFloat(parts[andIdx + 1]);
                }
            } else if (action === 'home') {
                x = 0; y = 0; heading = 0;
            } else if (action === 'restart') {
                x = 0; y = 0; heading = 0;
                penDown = true; penColor = 'black'; penSize = 1;
            } else if (action === 'erase_all') {
                segments.length = 0;
                currentSegment = [];
            } else if (action === 'draw_circle') {
                const r = parseFloat(parts[1]);
                const circlePath = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circlePath.setAttribute('cx', x);
                circlePath.setAttribute('cy', -y);
                circlePath.setAttribute('r', Math.abs(r));
                circlePath.setAttribute('fill', 'none');
                circlePath.setAttribute('stroke', penColor);
                circlePath.setAttribute('stroke-width', penSize);
                svg.appendChild(circlePath);
            } else if (action === 'draw_dot') {
                const size = parseFloat(parts[1]);
                const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                dot.setAttribute('cx', x);
                dot.setAttribute('cy', -y);
                dot.setAttribute('r', Math.abs(size) / 2);
                dot.setAttribute('fill', penColor);
                svg.appendChild(dot);
            }

            // End segment on pen_up or color change
            if ((action === 'pen_up' || action === 'pen_color') && currentSegment.length > 0) {
                segments.push([...currentSegment]);
                currentSegment = [];
            }
        }

        // Flush remaining segment
        if (currentSegment.length > 0) {
            segments.push(currentSegment);
        }

        // Draw all segments
        for (const seg of segments) {
            if (seg.length === 0) continue;
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
            const points = [];
            points.push(`${seg[0].x1},${-seg[0].y1}`);
            for (const line of seg) {
                points.push(`${line.x2},${-line.y2}`);
            }
            path.setAttribute('points', points.join(' '));
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke', seg[0].color);
            path.setAttribute('stroke-width', seg[0].size);
            path.setAttribute('stroke-linecap', 'round');
            path.setAttribute('stroke-linejoin', 'round');
            svg.appendChild(path);
        }

        // Draw turtle marker
        if (data.visible) {
            const marker = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
            const size = 10;
            const rad = heading * Math.PI / 180;
            const tipX = x + size * Math.cos(rad);
            const tipY = -(y + size * Math.sin(rad));
            const leftX = x + size * 0.6 * Math.cos(rad + 2.5);
            const leftY = -(y + size * 0.6 * Math.sin(rad + 2.5));
            const rightX = x + size * 0.6 * Math.cos(rad - 2.5);
            const rightY = -(y + size * 0.6 * Math.sin(rad - 2.5));
            marker.setAttribute('points', `${tipX},${tipY} ${leftX},${leftY} ${rightX},${rightY}`);
            marker.setAttribute('fill', penColor);
            svg.appendChild(marker);
        }
    }

    // Auto-fit viewBox
    fitTurtleViewBox();
}

function fitTurtleViewBox() {
    const svg = document.getElementById('turtle-canvas');
    const paths = svg.querySelectorAll('polyline, circle');
    if (paths.length === 0) {
        svg.setAttribute('viewBox', '-300 -300 600 600');
        return;
    }

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const p of paths) {
        if (p.tagName === 'circle') {
            const cx = parseFloat(p.getAttribute('cx'));
            const cy = parseFloat(p.getAttribute('cy'));
            const r = parseFloat(p.getAttribute('r'));
            minX = Math.min(minX, cx - r);
            minY = Math.min(minY, cy - r);
            maxX = Math.max(maxX, cx + r);
            maxY = Math.max(maxY, cy + r);
        } else {
            const pts = p.getAttribute('points').split(' ');
            for (const pt of pts) {
                const [px, py] = pt.split(',').map(Number);
                minX = Math.min(minX, px);
                minY = Math.min(minY, py);
                maxX = Math.max(maxX, px);
                maxY = Math.max(maxY, py);
            }
        }
    }

    const padding = 50;
    const width = maxX - minX + padding * 2;
    const height = maxY - minY + padding * 2;
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    const size = Math.max(width, height, 100);

    svg.setAttribute('viewBox', `${cx - size/2} ${cy - size/2} ${size} ${size}`);
}

// ========== Start ==========
init().catch(console.error);
