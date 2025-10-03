import os
import json
import psycopg2
import uuid
from dotenv import load_dotenv
from fastmcp import FastMCP

# -----------------------------
# Configuração do ambiente
# -----------------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
MCP_PROTOCOL = os.getenv("MCP_PROTOCOL", "STDIO").upper()


# -----------------------------
# Conexão com banco de dados
# -----------------------------
def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_client_encoding("UTF8")
    return conn


# -----------------------------
# Funções de acesso ao CRM
# -----------------------------
def insert_debtor(cpf: str, phone: str, email: str, full_name: str, birth_date: str, mother_name: str = None):
    user_id = str(uuid.uuid4())  # gera UUID no Python
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO public."debtor" (id, cpf, phone, email, full_name, birth_date, mother_name, score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, cpf, phone, email, full_name, birth_date, mother_name, verified, trust_level, score, created_at;
    """, (user_id, cpf, phone, email, full_name, birth_date, mother_name, 0))
        row = cursor.fetchone()
        conn.commit()
    conn.close()

    return {
        "id": row[0],
        "cpf": row[1],
        "phone": row[2],
        "email": row[3],
        "full_name": row[4],
        "birth_date": str(row[5]) if row[5] else None,
        "mother_name": row[6],
        "verified": row[7],
        "trust_level": row[8],
        "score": row[9],
        "created_at": str(row[10]) if row[10] else None,
    }

def fetch_debtor_by_cpf(cpf: str):
    """Busca um debtor pelo CPF"""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, cpf, phone, email, full_name, birth_date, mother_name, verified, trust_level, score, created_at
            FROM public."debtor"
            WHERE cpf = %s;
        """, (cpf,))
        row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "cpf": row[1],
            "phone": row[2],
            "email": row[3],
            "full_name": row[4],
            "birth_date": str(row[5]) if row[5] else None,
            "mother_name": row[6],
            "verified": row[7],
            "trust_level": row[8],
            "score": row[9],
            "created_at": str(row[10]) if row[10] else None,
        }
    return None


def fetch_debtors(page: int = 1, page_size: int = 10):
    """Retorna debtors paginados"""
    offset = (page - 1) * page_size
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, cpf, phone, email, full_name, birth_date, mother_name, verified, trust_level, score, created_at
            FROM public."debtor"
            ORDER BY id
            LIMIT %s OFFSET %s;
        """, (page_size, offset))
        rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "cpf": row[1],
            "phone": row[2],
            "email": row[3],
            "full_name": row[4],
            "birth_date": str(row[5]) if row[5] else None,
            "mother_name": row[6],
            "verified": row[7],
            "trust_level": row[8],
            "score": row[9],
            "created_at": str(row[10]) if row[10] else None,
        }
        for row in rows
    ]


# -----------------------------
# Inicialização do MCP
# -----------------------------
mcp = FastMCP("CRM-Bridge")


# -----------------------------
# Ferramentas do MCP
# -----------------------------
@mcp.tool
def get_debtors(page: int = 1, page_size: int = 10):
    """Retorna debtors paginados do CRM"""
    return json.dumps(fetch_debtors(page, page_size), ensure_ascii=False)


@mcp.tool(
    name="get_debtor_by_cpf",
    description="Retorna informações de um debtor a partir do CPF",
    tags={"debtor"},
    meta={"version": "1.0", "author": "product-team"}
)
def get_debtor_by_cpf_tool(cpf: str):
    debtor = fetch_debtor_by_cpf(cpf)
    if not debtor:
        return json.dumps({"error": "Debtor not found"}, ensure_ascii=False)
    return json.dumps(debtor, ensure_ascii=False)

@mcp.tool(
    name="add_debtor",
    description="Adiciona um novo debtor ao CRM (dados validados pela LLM)",
    tags={"debtor", "client"},
    meta={"version": "1.0", "author": "product-team"}
)
def add_debtor_tool(cpf: str, phone: str, email: str, full_name: str, birth_date: str, mother_name: str = None):
    """Tool MCP para criar debtor"""
    try:
        debtor = insert_debtor(cpf, phone, email, full_name, birth_date, mother_name)
        return json.dumps(debtor, ensure_ascii=False)
    except psycopg2.IntegrityError as e:
        # Pode ocorrer se CPF já existir
        return json.dumps({"error": f"Could not insert debtor: {str(e)}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

# -----------------------------
# Execução do servidor
# -----------------------------
if __name__ == "__main__":
    if MCP_PROTOCOL == "HTTP":
        mcp.run(transport="http", host="0.0.0.0", port=8000)
    elif MCP_PROTOCOL == "STREAMABLE-HTTP":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
    else:
        mcp.run()