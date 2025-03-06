# PubMedSearch MCP Server

A Model Content Protocol server that provides tools to search and retrieve academic papers from PubMed database.

## Features

- Search PubMed by keywords in title/abstract or author names
- Retrieve detailed information including title, authors, journal, abstract, DOI and more

1. Clone this repository:
   ```
   git clone <repository-url>
   cd pubmed-search-mcp-server
   ```

2. Install dependencies:
   ```
   pip install fastmcp requests python-dotenv
   ```

3. Create a `.env` file in the project root (if needed for configuration)

## Usage

1. Start the server in development mode:
   ```
   mcp dev pubmed_search_mcp_server.py
   ```

2. or add the server to Claude Desktop app *CLAUDE_DIRECTORY/claude_desktop_config.json*. For example if you are using Windows Subsystem for Linux (WSL) it may look like this:

   ```
   "pubmed-search": {
               "command": "wsl.exe",
               "args": [
                   "bash",
                   "-c",
                   "source /home/[user]/anaconda3/etc/profile.d/conda.sh && conda activate mcp && mcp run /home/[user]/pubmed-search-mpc-server/pubmed_search_mcp_server.py"
               ]
           },
   ```

