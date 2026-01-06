import os
import sys

import httpx


def main() -> None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY není nastaven.")

    headers = {"Authorization": f"Bearer {key}"}
    try:
        resp = httpx.get("https://api.openai.com/v1/models", headers=headers, timeout=10.0)
        print("status:", resp.status_code)
    except httpx.HTTPError as exc:
        print("OpenAI request failed:", exc, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
