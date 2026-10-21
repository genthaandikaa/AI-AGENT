"""Test suite for Dynamic AI NPC Brain & Simulation Engine."""

import sqlite3
from harmage.npc_brain import npc_brain_manager

def test_npc_brain():
    print("=== 1. SCHEDULE ===")
    sched = npc_brain_manager.get_effective_schedule()
    print("Period:", sched["period"], "| Label:", sched["period_label"], "| WIB:", sched["wib_time"])

    print("\n=== 2. UPDATE NPCS WITH LIVE TASKS ===")
    conn = sqlite3.connect("harmage/data/harmage_operations.db")
    conn.row_factory = sqlite3.Row
    tasks = [dict(r) for r in conn.execute("SELECT id, title, assignee, status, priority FROM tasks").fetchall()]
    conn.close()

    states = npc_brain_manager.update_all_npcs(active_tasks=tasks)
    print(f"Total NPC states: {len(states)}")
    for s in states[:6]:
        print(f"  [{s['agent_id']}] {s['name']} ({s['role'][:30]}) | Emotion: {s['emotion']}")
        print(f"     Morale: {s['morale']} | Energy: {s['energy']} | Stress: {s['stress']}")
        print(f"     Thought: \"{s['current_thought']}\"")

    print("\n=== 3. TRIGGER SPECIFIC DYNAMIC INTERACTION ===")
    d1 = npc_brain_manager.trigger_interaction("executive_manager", "treasurer")
    print(f"Topic: {d1.get('topic')}")
    print(f"  {d1['initiator']['name']}: \"{d1['initiator']['speech']}\"")
    print(f"  {d1['recipient']['name']}: \"{d1['recipient']['speech']}\"")

    print("\n=== 4. TRIGGER DIVISION PAIR INTERACTION ===")
    d2 = npc_brain_manager.trigger_interaction("tiktok_specialist", "tiktok_affiliate")
    print(f"Topic: {d2.get('topic')}")
    print(f"  {d2['initiator']['name']}: \"{d2['initiator']['speech']}\"")
    print(f"  {d2['recipient']['name']}: \"{d2['recipient']['speech']}\"")

    print("\n=== 5. CHECK PERSISTENT SQLITE STORAGE ===")
    conn = sqlite3.connect("harmage/data/harmage_operations.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM npc_brain_memories")
    mem_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM npc_brain_interactions")
    int_count = c.fetchone()[0]
    print(f"Total persisted memories: {mem_count}")
    print(f"Total persisted interactions: {int_count}")

    # Inspect the latest memory
    latest_mem = c.execute("SELECT agent_id, memory_type, content, emotion FROM npc_brain_memories ORDER BY id DESC LIMIT 1").fetchone()
    print("Latest persisted memory:", latest_mem)

    # Inspect the latest interaction
    latest_int = c.execute("SELECT initiator_name, recipient_name, topic, initiator_speech, recipient_speech FROM npc_brain_interactions ORDER BY id DESC LIMIT 1").fetchone()
    print("Latest persisted interaction:", latest_int)
    conn.close()

    assert len(states) >= 10, "Should have at least 10 NPC states"
    assert mem_count > 0, "Should have stored memories"
    assert int_count > 0, "Should have stored interactions"
    print("\nALL DYNAMIC NPC BRAIN ASSERTIONS PASSED!")

if __name__ == "__main__":
    test_npc_brain()
