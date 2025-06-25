#!/usr/bin/env python3
"""
Demo script showing how to interact with the random-number-mcp server.

This script demonstrates programmatic usage of the MCP server for testing
and integration purposes.
"""

import asyncio
import json
import sys
from typing import Any


class MCPClient:
    """Simple MCP client for testing the random-number server."""

    def __init__(self):
        self.process = None
        self.request_id = 0

    async def start_server(self):
        """Start the MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "random_number_mcp.server",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("✅ MCP server started")

    async def send_request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Send a JSON-RPC request to the server."""
        if not self.process:
            raise RuntimeError("Server not started")

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }

        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()

        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())

        return response

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        response = await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        if "error" in response:
            raise Exception(f"Tool error: {response['error']}")

        return response.get("result", {}).get("content", [{}])[0].get("text")

    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("🛑 MCP server stopped")


async def demo_random_tools():
    """Demonstrate all the random number tools."""
    client = MCPClient()

    try:
        await client.start_server()

        print("\n🎲 Random Number MCP Demo\n" + "="*50)

        # Demo random_int
        print("\n1. random_int - Generate random integers")
        result = await client.call_tool("random_int", {"low": 1, "high": 100})
        print(f"   Random integer (1-100): {result}")

        result = await client.call_tool("random_int", {"low": -10, "high": 10})
        print(f"   Random integer (-10 to 10): {result}")

        # Demo random_float
        print("\n2. random_float - Generate random floats")
        result = await client.call_tool("random_float", {})
        print(f"   Random float (default 0.0-1.0): {result}")

        result = await client.call_tool("random_float", {"low": 2.5, "high": 7.5})
        print(f"   Random float (2.5-7.5): {result}")

        # Demo random_choices
        print("\n3. random_choices - Choose from population")
        population = ["apple", "banana", "cherry", "date", "elderberry"]
        result = await client.call_tool("random_choices", {
            "population": population,
            "k": 1
        })
        print(f"   Random choice from fruits: {result}")

        result = await client.call_tool("random_choices", {
            "population": population,
            "k": 3,
            "weights": [0.4, 0.3, 0.2, 0.1, 0.0]
        })
        print(f"   3 weighted choices: {result}")

        # Demo random_shuffle
        print("\n4. random_shuffle - Shuffle lists")
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = await client.call_tool("random_shuffle", {"items": numbers})
        print(f"   Original: {numbers}")
        print(f"   Shuffled: {result}")

        # Demo secure_token_hex
        print("\n5. secure_token_hex - Cryptographically secure tokens")
        result = await client.call_tool("secure_token_hex", {"nbytes": 16})
        print(f"   16-byte secure hex token: {result}")

        result = await client.call_tool("secure_token_hex", {})
        print(f"   32-byte secure hex token: {result}")

        # Demo secure_random_int
        print("\n6. secure_random_int - Cryptographically secure integers")
        result = await client.call_tool("secure_random_int", {"upper_bound": 1000})
        print(f"   Secure random int (0-999): {result}")

        result = await client.call_tool("secure_random_int", {"upper_bound": 6})
        print(f"   Secure dice roll (0-5): {result}")

        print("\n" + "="*50)
        print("✅ All tools demonstrated successfully!")

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return 1

    finally:
        await client.stop_server()

    return 0


async def demo_error_handling():
    """Demonstrate error handling in the tools."""
    client = MCPClient()

    try:
        await client.start_server()

        print("\n🚨 Error Handling Demo\n" + "="*40)

        # Test invalid range
        print("\n1. Testing invalid range (low > high)")
        try:
            await client.call_tool("random_int", {"low": 10, "high": 5})
        except Exception as e:
            print(f"   Expected error: {e}")

        # Test empty population
        print("\n2. Testing empty population")
        try:
            await client.call_tool("random_choices", {"population": []})
        except Exception as e:
            print(f"   Expected error: {e}")

        # Test negative secure token bytes
        print("\n3. Testing negative token bytes")
        try:
            await client.call_tool("secure_token_hex", {"nbytes": -1})
        except Exception as e:
            print(f"   Expected error: {e}")

        print("\n" + "="*40)
        print("✅ Error handling working correctly!")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

    finally:
        await client.stop_server()

    return 0


async def main():
    """Run all demos."""
    print("🎯 Random Number MCP Server Demo")
    print("This demo shows the server running and responding to tool calls.\n")

    # Run main demo
    result1 = await demo_random_tools()

    # Run error handling demo
    result2 = await demo_error_handling()

    if result1 == 0 and result2 == 0:
        print("\n🎉 All demos completed successfully!")
        return 0
    else:
        print("\n💥 Some demos failed!")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
