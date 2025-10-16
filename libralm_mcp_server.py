#!/usr/bin/env python3
"""
Libralm MCP Server - Book Information Lookup Service

This MCP server provides tools to search and retrieve information about books
from the LibraLM API service.
"""

import json
import os
from typing import List, Optional
import contextvars

import requests
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from middleware import SmitheryConfigMiddleware

# Initialize the MCP server
mcp = FastMCP("Libralm Book Server")

# API Configuration - Global defaults for STDIO mode
API_BASE_URL = os.environ.get(
    "LIBRALM_API_URL", "https://yjv5auah93.execute-api.us-east-1.amazonaws.com/prod"
)
API_KEY = os.environ.get("LIBRALM_API_KEY", "")

# Store config for STDIO mode (backwards compatibility)
_stdio_config = {}


def handle_config(config: dict):
    """Handle configuration from Smithery - for backwards compatibility with stdio mode."""
    global _stdio_config
    _stdio_config = config


def get_request_config() -> dict:
    """Get full config from current request context."""
    try:
        # Try to get from request context if available (HTTP mode)
        import contextvars

        request = contextvars.copy_context().get('request')
        if hasattr(request, 'scope') and request.scope:
            return request.scope.get('smithery_config', {})
    except:
        pass

    # Fall back to STDIO config
    return _stdio_config


def get_config_value(key: str, default=None):
    """Get a specific config value from current request."""
    config = get_request_config()
    return config.get(key, default)


def get_api_key() -> str:
    """Get API key from request config or environment."""
    # Try to get from request config first (HTTP mode)
    api_key = get_config_value("apiKey")
    if api_key:
        return api_key

    # Fall back to environment variable (STDIO mode)
    return API_KEY


def get_api_base_url() -> str:
    """Get API base URL from request config or environment."""
    # Try to get from request config first (HTTP mode)
    api_url = get_config_value("apiUrl")
    if api_url:
        return api_url

    # Fall back to environment variable or default
    return API_BASE_URL


class BookInfo(BaseModel):
    """Book information structure"""

    book_id: str
    title: str
    author: Optional[str] = None
    category: Optional[str] = None
    subtitle: Optional[str] = None
    summary: Optional[str] = None
    length: Optional[str] = None
    release_date: Optional[str] = None
    tier: Optional[str] = None
    has_summary: bool
    has_chapter_summaries: bool
    has_table_of_contents: bool


def _make_api_request(endpoint: str) -> dict:
    """Make an authenticated request to the LibraLM API"""
    # Get API key and base URL from request context or environment
    api_key = get_api_key()
    base_url = get_api_base_url()

    headers = {"x-api-key": api_key, "Content-Type": "application/json"}

    url = f"{base_url}{endpoint}"
    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        raise ValueError("Invalid API key. Please check your LibraLM API key.")
    elif response.status_code == 404:
        raise ValueError(f"Resource not found: {endpoint}")
    elif response.status_code != 200:
        raise ValueError(
            f"API request failed with status {response.status_code}: {response.text}"
        )

    # Handle wrapped response format from Lambda
    result = response.json()
    if isinstance(result, dict) and "data" in result:
        return result["data"]
    return result


@mcp.tool()
def list_books() -> List[BookInfo]:
    """List all available books with their basic information"""
    try:
        data = _make_api_request("/books")
        books = []

        for book_data in data.get("books", []):
            books.append(BookInfo(**book_data))

        return sorted(books, key=lambda x: x.title)
    except Exception as e:
        print(f"Error listing books: {str(e)}")
        return []


@mcp.tool()
def get_book_summary(book_id: str) -> str:
    """Get the main summary for a book"""
    try:
        data = _make_api_request(f"/books/{book_id}/summary")
        return data.get("summary", "")
    except Exception as e:
        raise ValueError(f"Error getting summary for book '{book_id}': {str(e)}")


@mcp.tool()
def get_book_details(book_id: str) -> BookInfo:
    """Get detailed information about a specific book"""
    try:
        data = _make_api_request(f"/books/{book_id}")
        return BookInfo(**data)
    except Exception as e:
        raise ValueError(f"Error getting details for book '{book_id}': {str(e)}")


@mcp.tool()
def get_table_of_contents(book_id: str) -> str:
    """Get the table of contents for a book with chapter descriptions"""
    try:
        data = _make_api_request(f"/books/{book_id}/table_of_contents")
        return data.get("table_of_contents", "")
    except Exception as e:
        raise ValueError(
            f"Error getting table of contents for book '{book_id}': {str(e)}"
        )


@mcp.tool()
def get_chapter_summary(book_id: str, chapter_number: int) -> str:
    """Get the summary for a specific chapter of a book"""
    try:
        data = _make_api_request(f"/books/{book_id}/chapters/{chapter_number}")
        return data.get("summary", "")
    except Exception as e:
        raise ValueError(
            f"Error getting chapter {chapter_number} summary for book '{book_id}': {str(e)}"
        )


@mcp.resource("book://metadata/{book_id}")
def get_book_info_resource(book_id: str) -> str:
    """Get comprehensive information about a book including metadata and summary"""
    try:
        # Get book details
        book_info = get_book_details(book_id)

        # Try to get summary from API
        book_summary = None
        try:
            book_summary = get_book_summary(book_id)
        except:
            pass

        # Format as readable text
        info = f"# {book_info.title}\n\n"
        if book_info.subtitle:
            info += f"*{book_info.subtitle}*\n\n"
        info += f"**Author:** {book_info.author or 'Unknown'}\n"
        info += f"**Book ID:** {book_info.book_id}\n"
        info += f"**Category:** {book_info.category or 'Unknown'}\n"
        info += f"**Length:** {book_info.length or 'Unknown'}\n"
        info += f"**Release Date:** {book_info.release_date or 'Unknown'}\n"
        info += f"**Tier:** {book_info.tier or 'Unknown'}\n\n"

        if book_summary:
            info += "## Book Summary\n\n"
            info += book_summary + "\n\n"
        elif book_info.summary:
            info += "## Book Description\n\n"
            info += book_info.summary + "\n\n"
            # Add note if description appears truncated
            if book_info.summary.endswith("...") or book_info.summary.endswith("...</p>"):
                info += "*Note: This is the complete description available. For the full book summary, use the get_book_summary tool.*\n\n"

        if (
            book_info.has_summary
            or book_info.has_chapter_summaries
            or book_info.has_table_of_contents
        ):
            info += "## Available Resources\n\n"
            if book_info.has_table_of_contents:
                info += "- Table of contents with chapter descriptions (use get_table_of_contents tool)\n"
            if book_info.has_summary:
                info += "- Full book summary (use get_book_summary tool)\n"
            if book_info.has_chapter_summaries:
                info += "- Individual chapter summaries (use get_chapter_summary tool)\n"

        return info
    except Exception as e:
        return f"Error retrieving book information: {str(e)}"


@mcp.prompt()
def analyze_book(book_id: str) -> str:
    """Generate a prompt to analyze a book's themes and content"""
    return f"""Please analyze the book with ID '{book_id}'. 

First, retrieve the book's details and summary using the available tools. Then provide:

1. A brief overview of the book's main thesis
2. The key themes and concepts covered
3. Notable insights or takeaways
4. Who would benefit most from reading this book
5. How the book relates to its category and target audience

If chapter summaries are available, use them to provide specific examples that support your analysis."""


@mcp.prompt()
def compare_books(book_id1: str, book_id2: str) -> str:
    """Generate a prompt to compare two books"""
    return f"""Please compare the books with IDs '{book_id1}' and '{book_id2}'.

Using the available tools, analyze both books and provide:

1. Main themes and topics of each book
2. Key similarities between the books
3. Important differences in approach or content
4. Which book might be better for different types of readers
5. How the books complement each other

Consider the books' categories, authors, and publication dates in your analysis."""


def main():
    """Main entry point for the LibraLM MCP server"""
    transport_mode = os.getenv("TRANSPORT", "stdio")

    if transport_mode == "http":
        # HTTP mode with config extraction from URL parameters
        print("LibraLM MCP Server starting in HTTP mode...")

        # Setup Starlette app with CORS for cross-origin requests
        app = mcp.streamable_http_app()

        # IMPORTANT: add CORS middleware for browser based clients
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id", "mcp-protocol-version"],
            max_age=86400,
        )

        # Apply custom middleware for config extraction (per-request API key handling)
        app = SmitheryConfigMiddleware(app)

        # Use Smithery-required PORT environment variable
        port = int(os.environ.get("PORT", 8081))
        print(f"Listening on port {port}")

        uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")

    else:
        # STDIO mode for backwards compatibility
        print("LibraLM MCP Server starting in STDIO mode...")

        # Load config from environment for STDIO mode
        api_key = os.getenv("LIBRALM_API_KEY", "")
        api_url = os.getenv("LIBRALM_API_URL")

        if not api_key:
            print("Warning: LIBRALM_API_KEY environment variable not set")
            print("Please set your API key: export LIBRALM_API_KEY=your-key-here")

        # Set the config for stdio mode
        config = {"apiKey": api_key}
        if api_url:
            config["apiUrl"] = api_url
        handle_config(config)

        # Run with stdio transport (default)
        mcp.run()


if __name__ == "__main__":
    main()
