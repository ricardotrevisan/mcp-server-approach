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
            #"id": row[0],
            "cpf": row[1],
            "phone": row[2],
            "email": row[3],
            "full_name": row[4],
            "birth_date": str(row[5]) if row[5] else None,
            #"mother_name": row[6],
            #"verified": row[7],
            #"trust_level": row[8],
            #"score": row[9],
            #"created_at": str(row[10]) if row[10] else None,
        }
    return None

def fetch_debtors(page: int = 1, page_size: int = 10):
    page_size = min(page_size, 25)
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
            #"id": row[0],
            "cpf": row[1],
            "phone": row[2],
            "email": row[3],
            "full_name": row[4],
            "birth_date": str(row[5]) if row[5] else None,
            #"mother_name": row[6],
            #"verified": row[7],
            #"trust_level": row[8],
            #"score": row[9],
            #"created_at": str(row[10]) if row[10] else None,
        }
        for row in rows
    ]


# -----------------------------
# Inicialização do MCP
# -----------------------------
mcp = FastMCP("NPL-MCP")


# -----------------------------
# Prompts do MCP
# -----------------------------
@mcp.prompt("negotiator-prompt")
def negotiation_prompt():
    """
You are Travis, the negotiation assistant for Quant.
 
Guidelines:
One instruction per response.
Always confirm value, deadline, and payment method.
Never show internal IDs or irrelevant info.
Keep all processes tied to Quant’s formal workflow.

    """
    return {
        "description": "Travis – Quant debt negotiation assistant",
        "parameters": {
            "message": "Client message"
        }
    }

# -----------------------------
# Ferramentas do MCP
# -----------------------------
@mcp.tool(
    name="debtor-list",
    description="Returns paginated debtors from CRM",
    tags={"debtor"},
    meta={"version": "1.0", "author": "trevisan"}
)
def get_debtors(page: int = 1, page_size: int = 10):
    return json.dumps(fetch_debtors(page, page_size), ensure_ascii=False)


@mcp.tool(
    name="debtor-get",
    description="Retrives debtor data from CPF",
    tags={"debtor"},
    meta={"version": "1.0", "author": "trevisan"}
)

def get_debtor_by_cpf_tool(cpf: str):
    debtor = fetch_debtor_by_cpf(cpf)
    if not debtor:
        return json.dumps({"error": "Debtor not found"}, ensure_ascii=False)
    return json.dumps(debtor, ensure_ascii=False)

@mcp.tool(
    name="debtor-add",
    description="Persist a new debtor on CRM (input data validated by LLM)", 
    tags={"debtor", "client"},
    meta={"version": "1.0", "author": "trevisan"}
)
def add_debtor_tool(cpf: str, phone: str, email: str, full_name: str, birth_date: str, mother_name: str = None):
    try:
        debtor = insert_debtor(cpf, phone, email, full_name, birth_date, mother_name)
        return json.dumps(debtor, ensure_ascii=False)
    except psycopg2.IntegrityError as e:
        # Pode ocorrer se CPF já existir
        return json.dumps({"error": f"Could not insert debtor: {str(e)}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def fech_negotiation(cpf: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Busca o debtor
            cursor.execute("""
                SELECT id, cpf, phone, email, full_name, score, negotiation_strategy_id
                FROM public."debtor"
                WHERE cpf = %s;
            """, (cpf,))
            debtor_row = cursor.fetchone()
            if not debtor_row:
                return None

            debtor_id = debtor_row[0]
            debtor = {
                #"id": debtor_row[0],
                "cpf": debtor_row[1],
                "phone": debtor_row[2],
                "email": debtor_row[3],
                "full_name": debtor_row[4],
                #"score": debtor_row[5],
                #"negotiation_strategy_id": debtor_row[6],
            }

            cursor.execute("""
                SELECT id, status, age, total_value, original_balance, strategy_id, agreement_id, created_at
                FROM public."engageable_contract"
                WHERE debtor_id = %s AND status = true AND agreement_id IS NULL
                ORDER BY created_at DESC;
            """, (debtor_id,))
            contracts_rows = cursor.fetchall()

            engageable_contracts = []
            strategy_ids = set()
            for index, row in enumerate(contracts_rows):
                engageable_contracts.append({
                        #"id": row[0],
                        #"status": row[1],
                        "age": row[2],
                        "total_value": str(row[3]) if row[3] is not None else None,
                        "original_balance": str(row[4]) if row[4] is not None else None,
                        #"strategy_id": row[5],
                        #"agreement_id": row[6],
                        #"created_at": str(row[7]) if row[7] is not None else None,
                    })
                if row[5]:
                    strategy_ids.add(row[5])

            # Decide qual strategy usar: prioridade para debtor.negotiation_strategy_id
            selected_strategy_id = debtor.get("negotiation_strategy_id")
            if not selected_strategy_id and strategy_ids:
                # pega uma das strategies presentes nos contratos (a primeira)
                selected_strategy_id = next(iter(strategy_ids))

            negotiation_strategy = None
            negotiation_rules = []
            if selected_strategy_id:
                # Busca a strategy
                cursor.execute("""
                    SELECT id, name, description, created_at
                    FROM public."negotiation_strategy"
                    WHERE id = %s;
                """, (selected_strategy_id,))
                strat_row = cursor.fetchone()
                if strat_row:
                    negotiation_strategy = {
                        "id": strat_row[0],
                        "name": strat_row[1],
                        "description": strat_row[2],
                        "created_at": str(strat_row[3]) if strat_row[3] is not None else None,
                    }

                    # Busca rules associadas
                    cursor.execute("""
                        SELECT id, strategy_id, min_value, max_value, max_installments, max_discount_percent, min_downpayment_percent, valid_until, created_at
                        FROM public."negotiation_rule"
                        WHERE strategy_id = %s
                        ORDER BY created_at ASC;
                    """, (selected_strategy_id,))
                    rules_rows = cursor.fetchall()
                    for r in rules_rows:
                        negotiation_rules.append({
                            #"id": r[0],
                            #"strategy_id": r[1],
                            "min_value": str(r[2]) if r[2] is not None else None,
                            "max_value": str(r[3]) if r[3] is not None else None,
                            "max_installments": r[4],
                            "max_discount_percent": r[5],
                            "min_downpayment_percent": r[6],
                            #"valid_until": str(r[7]) if r[7] is not None else None,
                            #"created_at": str(r[8]) if r[8] is not None else None,
                        })

            return {
                "debtor": debtor,
                "engageable_contracts": engageable_contracts,
                #"negotiation_strategy": negotiation_strategy,
                "negotiation_rules": negotiation_rules,
            }
    finally:
        conn.close()


@mcp.tool(
    name="debtor-negotiation",
    description="Debtor, engageable contracts and negotiation strategy/rules",
    tags={"debtor", "negotiation"},
    meta={"version": "1.0", "author": "trevisan"}
)
def get_debtor_negotiation_tool(cpf: str):
    result = fech_negotiation(cpf)
    if result is None:
        return json.dumps({"error": "Debtor not found"}, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False)

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