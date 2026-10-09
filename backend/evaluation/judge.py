import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def evaluate_agent_run(
    user_message: str,
    sql: str,
    result: dict,
    answer: str
):
    response = client.responses.create(
        model="gpt-5-mini",
        instructions="""
You are evaluating an AI Data Analyst.

Judge whether the final answer is correct and supported
by the SQL result.

Evaluation rules:

1. correctness_score
   - 1 means incorrect
   - 5 means fully correct

2. groundedness_score
   - 1 means unsupported by the SQL result
   - 5 means completely supported

3. sql_relevance_score
   - 1 means the SQL does not answer the user's question
   - 5 means the SQL directly answers the question

4. overall_score
   - 1 means poor
   - 5 means excellent

5. passed
   - true if the answer is reliable enough to show to a user
   - false otherwise

Keep the reason short.
""",
        input=f"""
User question:
{user_message}

SQL:
{sql}

SQL result:
{json.dumps(result)}

Agent answer:
{answer}
""",
        text={
            "format": {
                "type": "json_schema",
                "name": "agent_evaluation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "correctness_score": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5
                        },
                        "groundedness_score": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5
                        },
                        "sql_relevance_score": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5
                        },
                        "overall_score": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5
                        },
                        "passed": {
                            "type": "boolean"
                        },
                        "reason": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "correctness_score",
                        "groundedness_score",
                        "sql_relevance_score",
                        "overall_score",
                        "passed",
                        "reason"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(
        response.output_text
    )