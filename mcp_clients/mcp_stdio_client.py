import asyncio
from fastmcp import Client

client = Client("mcp_server.py")

async def call_tool():
    async with client:
        tools = await client.list_tools()
        print("Available tools:")
        
        for tool in tools:
            print("\n-", tool)

        result = await client.call_tool("get_user_by_cpf", {"cpf":"12345678901"})

        print(f"\n{result}")

asyncio.run(call_tool())