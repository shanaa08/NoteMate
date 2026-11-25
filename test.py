from backend import generate_summary

text = """
Photosynthesis is the process by which plants use sunlight
to convert carbon dioxide and water into glucose.
"""

print(generate_summary(text))
from backend import generate_flashcards

text = """
Artificial Intelligence (AI) refers to the simulation of human intelligence by computers.

Machine Learning is a branch of AI that enables systems to learn from data.
"""

print(generate_flashcards(text))