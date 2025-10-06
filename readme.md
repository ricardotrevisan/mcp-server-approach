# NPL-MCP

Proof-of-concept MCP server implementing a mock NPL strategy for LLM agent engagement in a containerized environment

>["Enterprises should be thinking about building “MCP services” which are remotely-accessible, multi-tenant, highly governed/versioned and tightly secured context services."](https://www.solo.io/blog/enterprise-challenges-with-mcp-adoption)

## Overview

- Instantiates containers and seeds a database to simulate a fictitious CRM
- Migrations managed with Prisma
- MCP Server implemented in Python using FastMCP
- PgAdmin provided for convenience

## Prerequisites

- Docker & Docker Compose
- Node.js (>=18)
- npm
- Python (>=3.10)

## Docker Compose
Ensure that all required environment variables are defined in `docker-compose.yml`.  

To build and start all services:
```bash
docker-compose up -d --build
```

Create DATABASE_URL (.env file):
```bash
cd prisma
vi .env
DATABASE_URL="postgres://admin:admin123@localhost:5432/mydb" 
```

Create initial migration
```bash
npx prisma migrate dev --name init
```

If not a new database/volume, then a new migration
```bash
npx prisma migrate reset 
```

Seed the database (package.json configured) - Already on docker-composer.yml, but manually:
```bash
npx prisma db seed
```

Prisma Studio: 
```bash
npx run prisma:studio
```

## MCPFast Inspector
```bash
npx @modelcontextprotocol/inspector connect http://localhost:8000/mcp
```
Use URL and Token provided by the Inspector's stdout to maintain authentication. 

![MCP Inspector](resources/screen.png "Tools")


## Claude Desktop configuration
```json
{
  "mcpServers": {
    "server1": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```

