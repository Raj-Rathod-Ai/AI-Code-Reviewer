
import subprocess
import os
from google import genai


def get_diff():
    try:
        diff = subprocess.check_output(
            ["git", "show", "--format=", "--no-ext-diff"],
            text=True,
            stderr=subprocess.PIPE
        )
        return diff
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"Could not retrieve Git diff: {error.stderr}"
        )


def main():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing")

    diff = get_diff()

    if not diff.strip():
        print("No code changes found.")
        return

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert Python code reviewer.

    Review the following Git diff.

    Identify:
    1. Bugs
    2. Security vulnerabilities
    3. Severity (Critical, High, Medium, Low)
    4. Performance issues
    5. Corrected code
    6. Explanation

    Git diff:
    {diff}
    """

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    print("CODE REVIEW FEEDBACK:")
    print(response.text)


main()
