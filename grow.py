def calculate_xp_for_level(level: int, base_xp: int = 20, growth_factor: float = 2):
    """Calculate XP requirement for a given level with exponential growth."""
    return int(base_xp * (growth_factor ** (level - 1)))

# Example usage:
for level in range(1, 21):
    xp_for_level = calculate_xp_for_level(level)
    print(f"Level {level} XP required: {xp_for_level}")
