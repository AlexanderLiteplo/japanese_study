#!/usr/bin/env python3
"""
Script to add IDs to flashcards and create separate progress tracking file.
This separates the static flashcard data from the dynamic spaced repetition progress.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

def load_flashcards(filepath: str) -> List[Dict[str, Any]]:
    """Load flashcards from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: Any, filepath: str) -> None:
    """Save data to JSON file with proper formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_progress_entry(card_id: int) -> Dict[str, Any]:
    """Create initial progress entry for a flashcard."""
    return {
        "id": card_id,
        "date_last_studied": None,
        "num_times_studied": 0,
        "ease_factor": 2.5,  # Initial ease factor
        "interval": 1,       # Initial interval (days)
        "repetitions": 0,    # Number of successful reviews in a row
        "total_correct": 0,
        "total_incorrect": 0,
        "total_studied": 0,
        "total_correct_streak": 0,
        "total_incorrect_streak": 0
    }

def main():
    # File paths
    flashcards_path = "flashcard_generation/flashcards.json"
    flashcards_with_ids_path = "flashcard_generation/flashcards_with_ids.json"
    progress_path = "flashcard_generation/flashcard_progress.json"

    # Load existing flashcards
    print("Loading flashcards...")
    flashcards = load_flashcards(flashcards_path)

    # Add IDs to flashcards and create progress entries
    flashcards_with_ids = []
    progress_data = []

    print(f"Processing {len(flashcards)} flashcards...")
    for i, card in enumerate(flashcards, 1):
        # Add ID to flashcard
        card_with_id = {"id": i, **card}
        flashcards_with_ids.append(card_with_id)

        # Create corresponding progress entry
        progress_entry = create_progress_entry(i)
        progress_data.append(progress_entry)

        if i % 1000 == 0:
            print(f"Processed {i} flashcards...")

    # Save updated flashcards
    print("Saving flashcards with IDs...")
    save_json(flashcards_with_ids, flashcards_with_ids_path)

    # Save progress data
    print("Saving progress data...")
    save_json(progress_data, progress_path)

    # Create backup of original
    backup_path = f"{flashcards_path}.backup"
    if not os.path.exists(backup_path):
        print("Creating backup of original flashcards...")
        save_json(flashcards, backup_path)

    print("Done!")
    print(f"Original flashcards: {flashcards_path}")
    print(f"Flashcards with IDs: {flashcards_with_ids_path}")
    print(f"Progress data: {progress_path}")
    print(f"Backup: {backup_path}")

if __name__ == "__main__":
    main()
