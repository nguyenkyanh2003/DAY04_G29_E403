import os
from pathlib import Path

def save_note(topic: str, content: str) -> dict:
    """
    Saves a note to the local saved_notes.txt file.
    
    Args:
        topic: Tiêu đề hoặc chủ đề của ghi chú.
        content: Nội dung chi tiết cần ghi chú.
    """
    try:
        notes_file = Path(os.getcwd()) / "saved_notes.txt"
        with open(notes_file, "a", encoding="utf-8") as f:
            f.write(f"--- {topic} ---\n{content}\n\n")
        
        return {
            "error": None,
            "message": f"Successfully saved note for topic '{topic}'.",
            "topic": topic
        }
    except Exception as e:
        return {
            "error": f"Failed to save note: {str(e)}"
        }
