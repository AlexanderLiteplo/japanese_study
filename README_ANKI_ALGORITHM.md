# Anki SM-2 Algorithm Implementation

This project implements the Anki SM-2 spaced repetition algorithm for Japanese vocabulary learning.

## Overview

The implementation includes:
- **TypeScript Anki Algorithm**: Core SM-2 algorithm with proper types
- **Data Management**: Separate storage for static flashcard data and dynamic progress
- **Python Script**: Tool to add IDs and initialize progress data
- **Example Usage**: Demonstrations of how to use the system

## Files Structure

```
app/ankii-algo/
├── ankii.ts           # Core Anki algorithm implementation
├── data_manager.ts    # Data loading/saving utilities
└── example.ts         # Usage examples

flashcard_generation/
├── add_ids_and_progress.py     # Python script to add IDs
├── flashcard_generation/
│   ├── flashcards.json         # Original flashcard data
│   ├── flashcards_with_ids.json # Cards with IDs added
│   ├── flashcard_progress.json  # Progress tracking data
│   └── flashcards.json.backup   # Backup of original
```

## Algorithm Details

### SM-2 Rules Implemented

**Initial Values:**
- Ease Factor: 2.5
- Minimum Ease Factor: 1.3
- Initial Interval: 1 day
- Graduating Interval: 6 days

**Review Responses:**
- **AGAIN (0)**: Interval = 0, ease_factor = max(1.3, ease_factor - 0.2)
- **HARD (1)**: Interval = min(6, interval * 1.2), ease_factor = max(1.3, ease_factor - 0.15)
- **GOOD (2)**: Interval = interval * ease_factor (or 6 for new cards)
- **EASY (3)**: Interval = interval * ease_factor * 1.3, ease_factor += 0.15

## Usage

### 1. Initialize Flashcards

First, run the Python script to add IDs to your flashcards:

```bash
cd flashcard_generation
python3 add_ids_and_progress.py
```

This creates:
- `flashcards_with_ids.json`: Original data with IDs
- `flashcard_progress.json`: Initial progress data

### 2. Basic Usage

```typescript
import { AnkiAlgorithm, ReviewQuality } from './app/ankii-algo/ankii';
import { loadFlashcards, saveFlashcards } from './app/ankii-algo/data_manager';

// Load flashcards with progress data
const flashcards = await loadFlashcards();

// Get cards due for review
const dueCards = AnkiAlgorithm.getDueCards(deck);

// Review a card
const updatedCard = AnkiAlgorithm.processReview(card, ReviewQuality.GOOD);

// Save progress
await saveFlashcards(flashcards);
```

### 3. Complete Study Session Example

```typescript
import { AnkiAlgorithm, ReviewQuality } from './ankii';
import { loadFlashcards, updateCardProgress } from './data_manager';

async function studySession() {
    const flashcards = await loadFlashcards();

    // Create deck
    const deck = {
        id: 1,
        name: "Japanese Study",
        flashcards,
        date_created: new Date()
    };

    // Get due cards
    const dueCards = AnkiAlgorithm.getDueCards(deck);

    for (const card of dueCards) {
        console.log(`Review: ${card.word_hiragana} (${card.english})`);

        // Simulate user selecting GOOD
        const quality = ReviewQuality.GOOD;
        const updatedCard = AnkiAlgorithm.processReview(card, quality);

        // Save progress for this card
        await updateCardProgress(updatedCard);

        console.log(`Next review in ${updatedCard.interval} days`);
    }
}
```

## API Reference

### AnkiAlgorithm Class

#### Static Methods

- `initializeCard(baseCard)`: Create new flashcard with SR values
- `processReview(card, quality)`: Process review response and update card
- `getNextReviewDate(card)`: Calculate next review date
- `isDue(card)`: Check if card needs review
- `getDueCards(deck)`: Get all due cards
- `getNewCards(deck)`: Get never-studied cards
- `getDeckStats(deck)`: Get deck statistics

#### ReviewQuality Enum

- `AGAIN = 0`
- `HARD = 1`
- `GOOD = 2`
- `EASY = 3`

### DataManager Class

#### Methods

- `loadCompleteFlashcards()`: Load cards with progress
- `saveFlashcards(cards)`: Save progress data
- `updateAndSaveCard(card)`: Update single card progress

## Data Separation

The system maintains separation between:

1. **Static Data** (`flashcards_with_ids.json`):
   - Word information (hiragana, kanji, english, etc.)
   - IDs for referencing
   - Never changes during study

2. **Dynamic Data** (`flashcard_progress.json`):
   - Study statistics
   - Ease factors
   - Intervals
   - Review history
   - Updated after each review

This separation allows:
- Easy backup of progress
- Independent updates to flashcard content
- Clean data management

## Algorithm Accuracy

The implementation follows the official Anki SM-2 algorithm:
- Correct initial values (EF=2.5, interval=1)
- Proper ease factor bounds (minimum 1.3)
- Accurate interval calculations
- Correct handling of learning phase (6-day graduation)

## Future Enhancements

Potential improvements:
- Fuzzy matching for due dates (within hours)
- Card suspension/failure handling
- Review statistics and graphs
- Custom scheduling options
- Integration with Anki's card templates
