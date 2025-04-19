"""Command-line interface for the Python Code Tools MCP server."""

import argparse
import sys
from typing import List, Optional

from python_code_tools.server import create_mcp_server


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Python Code Tools MCP Server")
    parser.add_argument(
        "transport",
        choices=["stdio", "sse"],
        help="Transport protocol to use (stdio or sse)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE server (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3001,
        help="Port for SSE server (default: 3001)",
    )

    args = parser.parse_args(argv)

    try:
        # Create the MCP server with the specified settings
        mcp = create_mcp_server(host=args.host, port=args.port)

        # Run the server with the appropriate transport
        print(f"Starting Python Code Tools MCP server with {args.transport} transport")
        if args.transport == "sse":
            print(f"Server URL: http://{args.host}:{args.port}/sse")

        mcp.run(transport=args.transport)
        return 0
    except KeyboardInterrupt:
        print("Server stopped", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def stdio_main() -> int:
    """Convenience entry point for stdio transport.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    return main(["stdio"])


def sse_main() -> int:
    """Convenience entry point for SSE transport.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Get any command-line arguments after the script name
    argv = sys.argv[1:]

    # Pre-populate the 'transport' argument
    all_args = ["sse"] + argv

    return main(all_args)


if __name__ == "__main__":
    sys.exit(main())
