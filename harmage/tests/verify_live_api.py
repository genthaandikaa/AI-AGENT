"""Test live FastAPI endpoints for dynamic NPC brain."""

import urllib.request
import json

def test_api(url, method="GET", body=None):
    data = json.dumps(body).encode("utf-8") if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    print("=== 1. NPC BRAIN STATE ===")
    state = test_api("http://127.0.0.1:9200/api/npc/brain/state")
    print("Schedule:", state["schedule"]["period"], "| WIB:", state["schedule"]["wib_time"])
    print("NPC count:", len(state["npcs"]))
    for n in state["npcs"][:5]:
        print(f"  {n['name']} ({n['role'][:25]}): {n['emotion']} | Morale: {n['morale']} | Energy: {n['energy']}")
        print(f"    Thought: \"{n['current_thought']}\"")

    print("\n=== 2. TRIGGER DYNAMIC INTERACTION ===")
    dialogue = test_api("http://127.0.0.1:9200/api/npc/brain/interact", method="POST", body={"initiator_id": "creator_pm", "recipient_id": "yt_shorts_specialist"})
    print(f"Topic: {dialogue['topic']}")
    print(f"  {dialogue['initiator']['name']}: \"{dialogue['initiator']['speech']}\"")
    print(f"  {dialogue['recipient']['name']}: \"{dialogue['recipient']['speech']}\"")

    print("\n=== 3. PERSISTENT MEMORIES ===")
    memories = test_api("http://127.0.0.1:9200/api/npc/brain/memories?limit=4")
    print("Recent memories count:", len(memories))
    for m in memories:
        print(f"  [{m['agent_id']}] ({m['emotion']}) -> \"{m['content']}\"")

    print("\n=== 4. PERSISTENT INTERACTION HISTORY ===")
    history = test_api("http://127.0.0.1:9200/api/npc/brain/history?limit=3")
    print("Recent history count:", len(history))
    for h in history:
        print(f"  {h['initiator_name']} -> {h['recipient_name']} ({h['topic']}): \"{h['initiator_speech']}\"")

    assert len(state["npcs"]) >= 10
    assert len(memories) > 0
    assert len(history) > 0
    print("\nALL LIVE API VERIFICATIONS PASSED 100%!")

if __name__ == "__main__":
    main()
