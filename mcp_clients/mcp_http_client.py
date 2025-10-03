import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def call_tool():
    async with client:
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"\n- {tool} \n")

        result = await client.call_tool("get_user_by_cpf", {"cpf":"12345678901"})
        print(result)

asyncio.run(call_tool())