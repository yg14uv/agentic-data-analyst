import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from backend.evaluation.judge import evaluate_agent_run
from backend.logs.logger import log_agent_run
from backend.memory.store import (
    add_message,
    get_recent_history
)
from backend.metadata.search import (
    format_metadata_for_prompt,
    search_metadata
)
from backend.tools.sql_tool import execute_sql

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def format_conversation_history(history):
    if not history:
        return "No previous conversation."

    lines = []

    for message in history:
        role = message["role"]
        content = message["content"]

        lines.append(
            f"{role.capitalize()}: {content}"
        )

    return "\n".join(lines)


def build_metadata_search_query(
    user_message: str,
    history
):
    previous_user_messages = [
        message["content"]
        for message in history
        if message["role"] == "user"
    ]

    context = " ".join(
        previous_user_messages[-2:]
    )

    if context:
        return f"{context} {user_message}"

    return user_message


def run_data_analyst(
    user_message: str,
    session_id: str
):
    start_time = time.perf_counter()

    max_attempts = 3

    history = get_recent_history(
        session_id=session_id,
        limit=6
    )

    conversation_context = (
        format_conversation_history(history)
    )

    metadata_search_query = (
        build_metadata_search_query(
            user_message=user_message,
            history=history
        )
    )

    relevant_metadata = search_metadata(
        query=metadata_search_query,
        top_k=3
    )

    database_schema = (
        format_metadata_for_prompt(
            relevant_metadata
        )
    )

    tools = [
        {
            "type": "function",
            "name": "execute_sql",
            "description": (
                "Execute a read-only SQLite "
                "SELECT query against the "
                "analytics database."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "A valid SQLite "
                            "SELECT query."
                        )
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    ]

    instructions = f"""
You are an AI Data Analyst Assistant.

You are participating in a multi-turn conversation.

Conversation history:

{conversation_context}

The metadata search system selected this database schema:

{database_schema}

You have access to an execute_sql tool.

Rules:
- Use conversation history to resolve follow-up questions.
- Understand references such as "what about that", "what about the US", or "compare it".
- Use execute_sql whenever database data is required.
- Only use tables and columns listed in the provided schema.
- Do not invent tables or columns.
- Only generate read-only SELECT queries.
- Use SQLite syntax.
- If a tool call returns an SQL error, analyze the error and correct the query.
- Never claim you queried the database unless execute_sql was actually used.
- Base data answers only on successful tool results.
- Keep the final answer concise and clear.
"""

    input_text = f"""
Conversation history:

{conversation_context}

Current user message:

{user_message}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input=input_text,
        tools=tools
    )

    attempt_history = []
    current_response = response

    for attempt in range(max_attempts):
        tool_call = None

        for item in current_response.output:
            if (
                item.type == "function_call"
                and item.name == "execute_sql"
            ):
                tool_call = item
                break

        # No tool was needed
        if tool_call is None:
            answer = current_response.output_text

            add_message(
                session_id,
                "user",
                user_message
            )

            add_message(
                session_id,
                "assistant",
                answer
            )

            latency_ms = round(
                (
                    time.perf_counter()
                    - start_time
                )
                * 1000,
                2
            )

            evaluation = None

            log_agent_run({
                "session_id": session_id,
                "user_message": user_message,
                "success": True,
                "tool_used": False,
                "metadata": relevant_metadata,
                "sql": None,
                "result": None,
                "attempts": len(
                    attempt_history
                ),
                "attempt_history": (
                    attempt_history
                ),
                "answer": answer,
                "evaluation": evaluation,
                "latency_ms": latency_ms
            })

            return {
                "success": True,
                "answer": answer,
                "tool_used": False,
                "session_id": session_id,
                "metadata": relevant_metadata,
                "attempts": len(
                    attempt_history
                ),
                "attempt_history": (
                    attempt_history
                ),
                "evaluation": evaluation,
                "latency_ms": latency_ms
            }

        arguments = json.loads(
            tool_call.arguments
        )

        sql_query = arguments["query"]

        sql_result = execute_sql(
            sql_query
        )

        attempt_history.append({
            "attempt": attempt + 1,
            "sql": sql_query,
            "result": sql_result
        })

        tool_output = {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": json.dumps(
                sql_result
            )
        }

        current_response = (
            client.responses.create(
                model="gpt-5-mini",
                instructions=instructions,
                previous_response_id=(
                    current_response.id
                ),
                input=[tool_output],
                tools=tools
            )
        )

        # Successful SQL query
        if sql_result.get("success"):
            answer = (
                current_response.output_text
            )

            add_message(
                session_id,
                "user",
                user_message
            )

            add_message(
                session_id,
                "assistant",
                answer
            )

            # LLM-as-a-Judge
            evaluation = evaluate_agent_run(
                user_message=user_message,
                sql=sql_query,
                result=sql_result,
                answer=answer
            )

            latency_ms = round(
                (
                    time.perf_counter()
                    - start_time
                )
                * 1000,
                2
            )

            log_agent_run({
                "session_id": session_id,
                "user_message": user_message,
                "success": True,
                "tool_used": True,
                "metadata": relevant_metadata,
                "sql": sql_query,
                "result": sql_result,
                "attempts": len(
                    attempt_history
                ),
                "attempt_history": (
                    attempt_history
                ),
                "answer": answer,
                "evaluation": evaluation,
                "latency_ms": latency_ms
            })

            return {
                "success": True,
                "answer": answer,
                "tool_used": True,
                "session_id": session_id,
                "metadata": relevant_metadata,
                "sql": sql_query,
                "result": sql_result,
                "attempts": len(
                    attempt_history
                ),
                "attempt_history": (
                    attempt_history
                ),
                "evaluation": evaluation,
                "latency_ms": latency_ms
            }

    # All retry attempts failed
    last_attempt = (
        attempt_history[-1]
        if attempt_history
        else None
    )

    answer = (
        "I could not complete the "
        "database query successfully."
    )

    add_message(
        session_id,
        "user",
        user_message
    )

    add_message(
        session_id,
        "assistant",
        answer
    )

    latency_ms = round(
        (
            time.perf_counter()
            - start_time
        )
        * 1000,
        2
    )

    evaluation = None

    log_agent_run({
        "session_id": session_id,
        "user_message": user_message,
        "success": False,
        "tool_used": (
            len(attempt_history) > 0
        ),
        "metadata": relevant_metadata,
        "sql": (
            last_attempt["sql"]
            if last_attempt
            else None
        ),
        "result": (
            last_attempt["result"]
            if last_attempt
            else None
        ),
        "attempts": len(
            attempt_history
        ),
        "attempt_history": (
            attempt_history
        ),
        "answer": answer,
        "evaluation": evaluation,
        "latency_ms": latency_ms
    })

    return {
        "success": False,
        "answer": answer,
        "tool_used": (
            len(attempt_history) > 0
        ),
        "session_id": session_id,
        "metadata": relevant_metadata,
        "sql": (
            last_attempt["sql"]
            if last_attempt
            else None
        ),
        "result": (
            last_attempt["result"]
            if last_attempt
            else None
        ),
        "attempts": len(
            attempt_history
        ),
        "attempt_history": (
            attempt_history
        ),
        "evaluation": evaluation,
        "latency_ms": latency_ms
    }