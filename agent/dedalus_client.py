import os, requests

def call_dedalus(messages, tools):
    base = os.getenv("DEDALUS_API_BASE")
    key = os.getenv("DEDALUS_API_KEY")
    headers = {"Authorization": f"Bearer {key}"}
    data = {"model": os.getenv("ANTHROPIC_MODEL"), "messages": messages, "tools": tools}
    r = requests.post(f"{base}/v1/chat/completions", headers=headers, json=data)
    return r.json()


