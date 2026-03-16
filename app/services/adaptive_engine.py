def adjust_difficulty(current_difficulty: str, correct: bool) -> str:
    """Adjusts difficulty level based on correctness of the user's answer."""
    levels = ["easy", "medium", "hard"]
    
    # ensure it falls back gracefully
    try:
        index = levels.index(str(current_difficulty).lower())
    except ValueError:
        index = 1 # default medium fallback
        
    if correct and index < 2:
        index += 1
    elif not correct and index > 0:
        index -= 1
        
    return levels[index]
