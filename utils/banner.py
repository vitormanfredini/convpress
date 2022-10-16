"""
Function to print a banner
"""

def print_banner(message: str):
    """prints a beautiful banner with the provided message"""
    padding = 3
    full_size = (len(message) + (padding + 1) * 2)
    for _ in range(full_size):
        print("#", end='')
    print()
    for _ in range(padding):
        print("#", end='')
    print(' ', end='')
    print(message, end='')
    print(' ', end='')
    for _ in range(padding):
        print("#", end='')
    print()
    for _ in range(full_size):
        print("#", end='')
    print()
