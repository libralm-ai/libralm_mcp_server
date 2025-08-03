# LibraLM MCP Server

Access 50+ book summaries and chapter breakdowns directly in Claude Desktop through the Model Context Protocol (MCP).

<img width="1000" alt="LibraLM Demo" src="https://github.com/user-attachments/assets/demo-placeholder">

## Overview

LibraLM MCP Server brings a library of AI-generated book summaries to your Claude Desktop conversations. Search for books, read comprehensive summaries, explore chapter-by-chapter breakdowns, and get instant access to key insights from business, self-help, and educational books.

## Features

- 📚 **500+ Book Summaries** - Access a growing library of professionally summarized books
- 🔍 **Smart Search** - Find books by title, author, or ISBN
- 📖 **Chapter Breakdowns** - Get detailed summaries of individual chapters
- 📋 **Table of Contents** - View complete book structure with chapter descriptions
- 🎯 **Key Insights** - Extract main themes, frameworks, and actionable takeaways
- 🔐 **Secure API** - Protected access with API key authentication

## Installation

### Prerequisites

- Claude Desktop installed
- Python 3.10 or higher
- LibraLM API key (get one at [libralm.com](https://libralm.com))

### Quick Install

1. **Clone the repository**:
```bash
git clone https://github.com/libralm-ai/libralm_mcp_server.git
cd libralm_mcp_server
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Get your API key**:
   - Visit [libralm.com](https://libralm.com)
   - Sign in with Google or GitHub
   - Copy your API key from the dashboard

4. **Configure Claude Desktop**:

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
    "mcpServers": {
      "libralm": {
        "command": "uvx",
        "args": ["--from", "libralm-mcp-server", "libralm-mcp-server"],
        "env": {
            "LIBRALM_API_KEY": "your_api_key_here"
        }
      }
    }
  }
```

5. **Restart Claude Desktop**

## Available Tools

### 🔍 `search_books`
Search for books by title, author, or ISBN.
```
Search for "Atomic Habits"
Find books by James Clear
Look up ISBN 0735211299
```

### 📖 `get_book_info`
Get detailed information about a specific book.
```
Get details for book ID 0735211299
Show me information about this book
```

### 📝 `get_book_summary`
Get the comprehensive AI-generated summary of a book.
```
Summarize "Atomic Habits"
Give me the main points of this book
```

### 📋 `get_table_of_contents`
View the complete chapter list with descriptions.
```
Show me the chapters in "Atomic Habits"
What topics does this book cover?
```

### 📄 `get_chapter_summary`
Get a detailed summary of a specific chapter.
```
Summarize chapter 3 of "Atomic Habits"
What's in the first chapter?
```

## Example Usage

Here are some example prompts you can use with Claude:

- "Search LibraLM for books about habits"
- "What books do you have on leadership?"
- "Give me a summary of 'Outlive'"
- "Show me chapter 5 of 'The Wealth Ladder'"
- "Find books by Adam Grant"

## Configuration

### Environment Variables

- `LIBRALM_API_KEY` (required): Your LibraLM API key



## API Limits

- Free tier: 50 API calls per month
- Pro tier: Unlimited API calls
- Rate limiting: 10 requests per minute

## Troubleshooting

### "Invalid API key" error
- Verify your API key is correct in the configuration
- Check that you've copied the entire key including the prefix

### "Resource not found" error
- Ensure you're using a valid book ID
- The book may not be in the library yet

### No books showing up
- Check your internet connection
- Verify the API endpoint is accessible
- Ensure your API key has not exceeded its usage limit

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@libralm.com
- 🐛 Issues: [GitHub Issues](https://github.com/libralm-ai/libralm_mcp_server/issues)
<!-- - 💬 Discord: [Join our community](https://discord.gg/libralm) -->

## Related Projects

- [LibraLM Web](https://libralm.com) - Web dashboard and API key management
<!-- - [LibraLM API Docs](https://docs.libralm.com) - Full API documentation -->
- [MCP Specification](https://modelcontextprotocol.io) - Learn more about MCP

---

Built with ❤️ by the LibraLM team