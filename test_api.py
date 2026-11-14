
import httpx
from ai_client import generate_response

try:
    answer = generate_response(
        "Explain Python in two simple sentences."
    )
    print("\nAI Response:")
    print(answer)

except httpx.HTTPStatusError as error:
    print("Status Code:", error.response.status_code)
    print("API Error Details:")
    print(error.response.text)

except Exception as error:
    print("Error:", error)
