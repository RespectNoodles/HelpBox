<!-- Banner -->
<h1 align="center">
HelpBox by Perish
</h1>


<!-- Banner Image --> 
![](/images/helpbox-banner.png)


<!-- Catch Phrase -->  
<h4 align="center">A portable, project-local tool registry and installer with a friendly CLI</h4>


<!-- Links For Badges -->  
<p align="center">
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-_red.svg"></a>
<a href="https://github.com/RespectNoodles/issues"><img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"></a>
<a href="https://goreportcard.com/badge/github.com/RespectNoodles"><img src="https://goreportcard.com/badge/github.com/RespectNoodles/interactsh"></a>
<a href="https://twitter.com/egman23"><img src="https://img.shields.io/twitter/follow/egman23.svg?logo=twitter"></a>
<a href="https://discord.com/users/perish5514"><img src="https://img.shields.io/discord/695645237418131507.svg?logo=discord"></a>
</p>


<!-- Social Links -->  
<p align="center">
  <a href="#features">Features</a>
  <a href="#usage">Usage</a>
  <a href="#toolbox-integration">Toolbox Integration</a>
</p> <br>

--- 

<p>
<h3> This Tool Was Made By: </h3>
</p>
  
![](/images/perish-logo-ss.png)

### <h1> Perish </h1> <br>
<p>
<h3>
- <a href="https://github.com/RespectNoodles">**GitHub**</a> <br>
- <a href="https://www.instagram.com/cj_egg/">**Instagram**</a> <br>
- <a href="https://www.facebook.com/c.j.egan.738639/">**Facebook**</a> <br>
- <a href="https://steamcommunity.com/id/Perishexe/">**Steam**</a> <br>
- <a href="https://discord.com/users/perish5514">Discord</a>
</h3>
</p>

---


## Overview

HelpBox is a portable, project-local tool registry and installer with a friendly CLI. <br>
It lets you list, install, update, and verify tools from a JSON registry while keeping installs
inside a configurable prefix (default: \`./.tools\`) so projects stay self-contained.

### Key Features

- Registry-driven tool definitions with install/update/verify commands.
- Portable prefix for project-local installations.
- Safety knobs: \`--verbose\`, \`--dry-run\`, and \`--explain\`.
- Network diagnostics under \`net\` with guided confirmations for disruptive actions.

### Requirements

- Python 3.8+
- A package manager or tools referenced by your registry entries (e.g., \`apt-get\`)


---


## Index

1.  [Quick Start](#quick-start)
2.  [Download & Installation](#download--installation)
3.  [Concepts](#concepts)
4.  [Project Layout](#project-layout)
5.  [Registry Format](#registry-format)
6.  [Configuration](#configuration)
7.  [Commands](#commands)
8.  [Flags](#flags)
9.  [Package Manager Backends](#package-manager-backends)
1.  [Quick Start](#quick-start)
2.  [Download & Installation](#download--installation)
3.  [Concepts](#concepts)
4.  [Project Layout](#project-layout)
5.  [Registry Format](#registry-format)
6.  [Configuration](#configuration)
7.  [Commands](#commands)
8.  [Flags](#flags)
9.  [Package Manager Backends](#package-manager-backends)
10. [Portable Prefix & PATH](#portable-prefix--path)
11. [Verification & Doctor](#verification--doctor)
12. [Import & Export](#import--export)
13. [Interactive TUI](#interactive-tui)
14. [Usage Notes](#usage-notes)
15. [Examples](#examples)
16. [Troubleshooting](#troubleshooting)
17. [Helpful Tips](#helpful-tips)
17. [Helpful Tips](#helpful-tips)


---


## Quick Start

1. **List tools**
   \`\`\` <br>
   python tools/toolbox.py list <br>
   \`\`\`


2. **Get info about a tool**
   \`\`\` <br>
   python tools/toolbox.py info nmap <br>
   \`\`\`


3. **Install a tool into your portable prefix**
   \`\`\` <br>
   python tools/toolbox.py install jq <br>
   \`\`\`


4. **Verify a tool**
   \`\`\` <br>
   python tools/toolbox.py verify jq <br>
   \`\`\`


---


## Download & Installation

I have written the following instructions taking into account that there are **beginners** out there. <br>
Anyone *old*, *bald*, *small* or *big* should be able to follow along! Even **YOU!**

### Step 1: Get the project folder

1. Open a **terminal** window (**Win** + **R** -> Type: **cmd** -> **Shift** + **Enter** Key).
1. Open a **terminal** window (**Win** + **R** -> Type: **cmd** -> **Shift** + **Enter** Key).
2. Go to the folder where you keep projects.
3. If someone shared this folder with you, open it. If not, type: 
   \`\`\` <br>
   git clone <project-url> <br>
   \`\`\` <br>
   Then move into the folder: <br>
   \`\`\` <br>
   cd <project-folder> <br>
   \`\`\`


### Step 2: Look inside the folder

1. Type this to see the files:
   \`\`\` <br>
   ls <br>
   \`\`\`
2. You should see a **tools** folder and a **README.js** file.


### Step 3: Run the toolbox

1. Type this to list the tools:
   \`\`\` <br>
   python tools/toolbox.py list <br>
   \`\`\`
2. If you see a list, it worked! 🎉


### Step 4: Install a tool

1. Pick a tool name from the list, like **jq**.
2. Type:
   \`\`\` <br>
   python tools/toolbox.py install jq <br>
   \`\`\`
3. Wait for it to finish.


### Step 5: Check the tool

1. Type:
   \`\`\` <br>
   python tools/toolbox.py verify jq <br>
   \`\`\`
2. If you see a version number, the tool is ready.


### Step 6: Keep it portable (like a backpack)

You can put the tools in a special folder inside this project so they travel with you.

1. Type:
   \`\`\` <br>
   python tools/toolbox.py --prefix ./.portable install jq <br>
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

\`\`\` <br>
./ <br>
├── .config/
│   └── toolbox.json         # Local configuration (prefix, colour) <br>
├── tools/ <br>
│   ├── registry.json        # Tool registry <br>
│   └── toolbox.py           # CLI entrypoint <br>
└── README.js                # This manual 
│   └── toolbox.json         # Local configuration (prefix, colour) <br>
├── tools/ <br>
│   ├── registry.json        # Tool registry <br>
│   └── toolbox.py           # CLI entrypoint <br>
└── README.js                # This manual <br>
\`\`\`


---


## Registry Format

The registry is a JSON file located at \`tools/registry.json\`. <br>
The registry is a JSON file located at \`tools/registry.json\`. <br>
Each tool entry looks like this:


\`\`\` <br>
json <br>
{ <br>
  "name": "jq", <br>
  "category": "data", <br>
  "description": "Command-line JSON processor.", <br>
  "install": "apt-get install -y jq", <br>
  "update": "apt-get update -y && apt-get install -y jq", <br>
  "verify": "jq --version", <br>
  "docs": "<https://jqlang.github.io/jq/>", <br>
  "requires_root": true, <br>
  "source": "apt" <br>
\`\`\`json <br>
{ <br>
  "name": "jq", <br>
  "category": "data", <br>
  "description": "Command-line JSON processor.", <br>
  "install": "apt-get install -y jq", <br>
  "update": "apt-get update -y && apt-get install -y jq", <br>
  "verify": "jq --version", <br>
  "docs": "<https://jqlang.github.io/jq/>", <br>
  "requires_root": true, <br>
  "source": "apt" <br>
} <br>
\`\`\`


---


## Fields:

## Fields:

- **name**: Command name (also used for \`command -v\` checks).
- **category**: A descriptive grouping (e.g., security, web, utilities).
- **description**: Human-friendly summary.
- **install** / **update** / **verify**: Shell commands to run.
- **docs**: URL to official docs.
- **requires_root**: Boolean hint for sudo/root needs.
- **source**: One of \`apt\`, \`pip\`, \`go\`, \`cargo\`, \`git\`, or anything else you want to label.


---


## Configuration

Local configuration lives at \`.config/toolbox.json\`: <br>

\`\`\` <br>
json <br>
{ <br>
  "prefix": "./.tools", <br>
  "colour": true <br>
} <br>
\`\`\` 
\`\`\`json <br>
{ <br>
  "prefix": "./.tools", <br>
  "colour": true <br>
} <br>
\`\`\` 

- **prefix**: Where portable installs land.
- **colour**: Toggle ANSI colours on output.
- **colour**: Toggle ANSI colours on output.


You can override \`prefix\` per command using \`--prefix\`.


---


## Commands

All commands are sub-commands on \`tools/toolbox.py\`:

- **list**: Show all tools and their status.
- **search <query>**: Fuzzy search across name/category/description.
- **info <tool>**: Detailed view of a tool entry.
- **install <tool>**: Run the tool's install command.
- **update <tool>**: Run the tool's update command.
- **verify <tool>**: Run the tool's verify command.
- **doctor**: Check that required system commands exist.
- **setup --theme <name>**: Install shell integration with prompt themes (`minimal`, `vivid`, `high-contrast`, `dark-contrast`).
- **export**: Print registry JSON (or save to file).
- **import**: Replace registry JSON from a file.
- **tui**: Interactive selector (requires \`fzf\`).
- **net ping <host> --count --size --interval**: Ping a host with custom parameters.
- **net trace <host>**: Trace network path using mtr/traceroute/tracepath.
- **net dns-test <host>**: Run DNS resolution checks with dig/nslookup/getent.
- **net speed**: Run a bandwidth test (if speedtest/fast is installed).
- **net flush-dns**: Flush DNS caches (requires explicit confirmation).
- **net restart-network**: Restart networking services (requires explicit confirmation).
- **net mtu-test [host]**: Probe path MTU safely with DF pings (requires confirmation).


---


## Flags

Global flags (work with all commands):

- **--verbose**: Print commands before execution.
- **--dry-run**: Print commands without running them.
- **--explain**: Add human-readable reasoning for each step.
- **--no-colour**: Disable ANSI colours.
- **--no-colour**: Disable ANSI colours.
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


The toolbox prepends \`<prefix>/bin\` to \`PATH\` during command execution 
so that tools installed into the local prefix can be found immediately.


Example:

\`\`\` <br>
python tools/toolbox.py --prefix ./.portable install bat <br>
python tools/toolbox.py --prefix ./.portable verify bat <br>
\`\`\` <br>
python tools/toolbox.py --prefix ./.portable install bat <br>
python tools/toolbox.py --prefix ./.portable verify bat <br>
\`\`\`


---


## Verification & Doctor

- **verify** runs the registry's verify command (often \`<tool> --version\`).
- **doctor** checks if system dependencies (apt, pip, go, cargo, git, curl, fzf) are available.


---


## Import & Export

Export the registry to a file:

\`\`\` <br>
python tools/toolbox.py export --output backup.json <br>
\`\`\`

Import a registry file:

\`\`\` <br>
python tools/toolbox.py import backup.json <br>
\`\`\`


---


## Interactive TUI

If \`fzf\` is installed, you can run:

\`\`\` <br>
python tools/toolbox.py tui <br>
\`\`\`

- You’ll get a **searchable picker**. <br>
- Selecting a *tool* shows its **info panel**.


---


## Usage Notes

- Use \`--dry-run\` to preview commands without running them.
- Use \`--explain\` to see intent for each step.
- Network diagnostics are available under \`net\`:

\`\`\` <br>
python tools/toolbox.py net ping example.com --count 4 --size 56 --interval 1 <br>
python tools/toolbox.py net trace example.com <br>
python tools/toolbox.py net dns-test example.com <br>
python tools/toolbox.py net speed <br>
python tools/toolbox.py net ping example.com --count 4 --size 56 --interval 1 <br>
python tools/toolbox.py net trace example.com <br>
python tools/toolbox.py net dns-test example.com <br>
python tools/toolbox.py net speed <br>
\`\`\`

Guided actions require explicit confirmation:

\`\`\` <br>
python tools/toolbox.py net flush-dns <br>
python tools/toolbox.py net restart-network <br>
python tools/toolbox.py net mtu-test 1.1.1.1 <br>
python tools/toolbox.py net flush-dns <br>
python tools/toolbox.py net restart-network <br>
python tools/toolbox.py net mtu-test 1.1.1.1 <br>
\`\`\`

---


## Examples

List tools: <br>
List tools: <br>
\`\`\` <br>
python tools/toolbox.py list <br>
\`\`\`


Search for security tools: <br>
Search for security tools: <br>
\`\`\` <br>
python tools/toolbox.py search security <br>
\`\`\`


Install and verify a tool with verbose output: <br>
Install and verify a tool with verbose output: <br>
\`\`\` <br>
python tools/toolbox.py --verbose install jq <br>
python tools/toolbox.py --verbose install jq <br>
python tools/toolbox.py --verbose verify jq <br>
\`\`\`


Dry-run a command to preview actions: <br>
Dry-run a command to preview actions: <br>
\`\`\` <br>
python tools/toolbox.py --dry-run install nmap <br>
\`\`\`


Explain what’s happening: <br>
Explain what’s happening: <br>
\`\`\` <br>
python tools/toolbox.py --explain update httpx <br>
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


## Helpful Tips

- **Tip #1:** \`--dry-run\` is your “break-glass” button—use it before you unleash anything scary.
- **Tip #2:** Keep your \`prefix\` on a USB stick and you’ve got a travel-ready toolbox.
- **Tip #3:** If a tool isn’t in the registry yet, you’re officially allowed to add it (and brag).
- **Tip #4:** If \`tui\` feels slow, you probably just discovered that you need more coffee.


---


Happy hacking. <br>
I hope this tool assists you in your future tasks!! 
