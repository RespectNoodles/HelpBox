<h1 align="center">
  <br>
<img =".vscode/images/egman-toolbox-bg-resized.png" width="200px" alt="title-resized"></a>
  ![title-resized](/images/egman-toolbox-bg-resized.png")   
</h1>
<h4 align="center">A portable, project-local tool registry and installer with a friendly CLI</h4>


<p align="center">
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-_red.svg"></a>
<a href="https://github.com/RespectNoodles/issues"><img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"></a>
<a href="https://goreportcard.com/badge/github.com/RespectNoodles"><img src="https://goreportcard.com/badge/github.com/RespectNoodles/interactsh"></a>
<a href="https://twitter.com/egman23"><img src="https://img.shields.io/twitter/follow/pdiscoveryio.svg?logo=twitter"></a>
<a href="https://discord.com/users/perish5514"><img src="https://img.shields.io/discord/695645237418131507.svg?logo=discord"></a>
</p>


<p align="center">
  <a href="#features">Features</a> •
  <a href="#usage">Usage</a> •
  <a href="#toolbox-integration">Toolbox Integration</a> •
  <a href="https://discord.com/users/perish5514">Add My Discord</a>
</p>


---


# Egman23 Toolbox Manual


---


## Index


1. [Quick Start](#quick-start)
2. [Download & Installation](#download--installation)
3. [Concepts](#concepts)
4. [Project Layout](#project-layout)
5. [Registry Format](#registry-format)
6. [Configuration](#configuration)
7. [Commands](#commands)
8. [Flags](#flags)
9. [Package Manager Backends](#package-manager-backends)
10. [Portable Prefix & PATH](#portable-prefix--path)
11. [Verification & Doctor](#verification--doctor)
12. [Import & Export](#import--export)
13. [Interactive TUI](#interactive-tui)
14. [Examples](#examples)
15. [Troubleshooting](#troubleshooting)
16. [Cheeky Tips](#cheeky-tips)


---


## Quick Start


1. **List tools**
   \`\`\`
   python tools/toolbox.py list
   \`\`\`


2. **Get info about a tool**
   \`\`\`
   python tools/toolbox.py info nmap
   \`\`\`


3. **Install a tool into your portable prefix**
   \`\`\`
   python tools/toolbox.py install jq
   \`\`\`


4. **Verify a tool**
   \`\`\`
   python tools/toolbox.py verify jq
   \`\`\`


---


## Download & Installation


This part is written like a simple guide for younger learners. Slow and steady!


### Step 1: Get the project folder


1. Ask someone to help you open a **terminal** (the black window where you type commands).
2. Go to the folder where you keep projects.
3. If someone shared this folder with you, open it. If not, type:
   \`\`\`
   git clone <project-url>
   \`\`\`
   Then move into the folder:
   \`\`\`
   cd <project-folder>
   \`\`\`


### Step 2: Look inside the folder


1. Type this to see the files:
   \`\`\`
   ls
   \`\`\`
2. You should see a **tools** folder and a **README.js** file.


### Step 3: Run the toolbox


1. Type this to list the tools:
   \`\`\`
   python tools/toolbox.py list
   \`\`\`
2. If you see a list, it worked! 🎉


### Step 4: Install a tool (with help)


1. Pick a tool name from the list, like **jq**.
2. Type:
   \`\`\`
   python tools/toolbox.py install jq
   \`\`\`
3. Wait for it to finish.


### Step 5: Check the tool


1. Type:
   \`\`\`
   python tools/toolbox.py verify jq
   \`\`\`
2. If you see a version number, the tool is ready.


### Step 6: Keep it portable (like a backpack)


You can put the tools in a special folder inside this project so they travel with you.


1. Type:
   \`\`\`
   python tools/toolbox.py --prefix ./.portable install jq
   \`\`\`
2. Now the tool lives inside **.portable**.


---


## Concepts


The toolbox is built on three ideas:


- **Registry-driven**: Tools are described in a JSON registry with install, update, and verify commands.
- **Portable by design**: All installs can target a local prefix (default: \`./.tools\`).
- **Safety knobs**: \`--verbose\`, \`--dry-run\`, and \`--explain\` let you see and understand every step.


---


## Project Layout


\`\`\`
./
├── .config/
│   └── toolbox.json         # Local configuration (prefix, color)
├── tools/
│   ├── registry.json        # Tool registry
│   └── toolbox.py           # CLI entrypoint
└── README.js                # This manual
\`\`\`


---


## Registry Format


The registry is a JSON file located at \`tools/registry.json\`.
Each tool entry looks like this:


\`\`\`json
{
  "name": "jq",
  "category": "data",
  "description": "Command-line JSON processor.",
  "install": "apt-get install -y jq",
  "update": "apt-get update -y && apt-get install -y jq",
  "verify": "jq --version",
  "docs": "<https://jqlang.github.io/jq/>",
  "requires_root": true,
  "source": "apt"
}
\`\`\`


Fields:


- **name**: Command name (also used for \`command -v\` checks).
- **category**: A descriptive grouping (e.g., security, web, utilities).
- **description**: Human-friendly summary.
- **install** / **update** / **verify**: Shell commands to run.
- **docs**: URL to official docs.
- **requires_root**: Boolean hint for sudo/root needs.
- **source**: One of \`apt\`, \`pip\`, \`go\`, \`cargo\`, \`git\`, or anything else you want to label.


---


## Configuration


Local configuration lives at \`.config/toolbox.json\`:


\`\`\`json
{
  "prefix": "./.tools",
  "color": true
}
\`\`\`


- **prefix**: Where portable installs land.
- **color**: Toggle ANSI colors on output.


You can override \`prefix\` per command using \`--prefix\`.


---


## Commands


All commands are subcommands on \`tools/toolbox.py\`:


- **list**: Show all tools and their status.
- **search <query>**: Fuzzy search across name/category/description.
- **info <tool>**: Detailed view of a tool entry.
- **install <tool>**: Run the tool's install command.
- **update <tool>**: Run the tool's update command.
- **verify <tool>**: Run the tool's verify command.
- **doctor**: Check that required system commands exist.
- **export**: Print registry JSON (or save to file).
- **import**: Replace registry JSON from a file.
- **tui**: Interactive selector (requires \`fzf\`).


---


## Flags


Global flags (work with all commands):


- **--verbose**: Print commands before execution.
- **--dry-run**: Print commands without running them.
- **--explain**: Add human-readable reasoning for each step.
- **--no-color**: Disable ANSI colors.
- **--prefix <path>**: Override install prefix.


---


## Package Manager Backends


The registry supports multiple backends via command strings:


- **APT**: \`apt-get install -y <tool>\`
- **PIP**: \`pip install --user <tool>\`
- **Go**: \`go install <module>@latest\`
- **Cargo**: \`cargo install <crate>\`
- **Git release downloads**: Use \`curl\` + \`tar\` + \`cp\` for binaries.


The CLI does not implement package managers directly—it simply runs the commands you specify.


---


## Portable Prefix & PATH


The toolbox prepends \`<prefix>/bin\` to \`PATH\` during command execution so that tools
installed into the local prefix can be found immediately.


Example:


\`\`\`
python tools/toolbox.py --prefix ./.portable install bat
python tools/toolbox.py --prefix ./.portable verify bat
\`\`\`


---


## Verification & Doctor


- **verify** runs the registry's verify command (often \`<tool> --version\`).
- **doctor** checks if system dependencies (apt, pip, go, cargo, git, curl, fzf) are available.


---


## Import & Export


Export the registry to a file:


\`\`\`
python tools/toolbox.py export --output backup.json
\`\`\`


Import a registry file:


\`\`\`
python tools/toolbox.py import backup.json
\`\`\`


---


## Interactive TUI


If \`fzf\` is installed, you can run:


\`\`\`
python tools/toolbox.py tui
\`\`\`


You’ll get a searchable picker. Selecting a tool shows its info panel.


---


## Examples


List tools:
\`\`\`
python tools/toolbox.py list
\`\`\`


Search for security tools:
\`\`\`
python tools/toolbox.py search security
\`\`\`


Install and verify a tool with verbose output:
\`\`\`
python tools/toolbox.py --verbose install jq
python tools/toolbox.py --verbose verify jq
\`\`\`


Dry-run a command to preview actions:
\`\`\`
python tools/toolbox.py --dry-run install nmap
\`\`\`


Explain what’s happening:
\`\`\`
python tools/toolbox.py --explain update httpx
\`\`\`


---


## Troubleshooting


- **Tool not found after install**
  - Confirm the tool is installed into \`<prefix>/bin\` and that your shell is using the right PATH.
  - Try rerunning with \`--verbose\` to see the command output.


- **Missing package manager**
  - Use \`python tools/toolbox.py doctor\` to see what is missing.


- **Registry errors**
  - Make sure the registry JSON is valid and includes a top-level \`registry\` array.


---


## Cheeky Tips


- **Tip #1:** \`--dry-run\` is your “break-glass” button—use it before you unleash anything scary.
- **Tip #2:** Keep your \`prefix\` on a USB stick and you’ve got a travel-ready toolbox.
- **Tip #3:** If a tool isn’t in the registry yet, you’re officially allowed to add it (and brag).
- **Tip #4:** If \`tui\` feels slow, you probably just discovered that you need more coffee.


---


Happy hacking. Be kind to your future self.
`;


if (require.main === module) {
  console.log(manual.trim());
}


module.exports = manual;

