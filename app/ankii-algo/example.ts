// Example usage of the Anki Algorithm implementation
import { AnkiAlgorithm, ReviewQuality, Flashcard, Deck } from './ankii';

// Example: Loading flashcards from JSON and initializing them
async function loadFlashcards(): Promise<Flashcard[]> {
    // In a real app, you'd load from your flashcards_with_ids.json
    const response = await fetch('/flashcard_generation/flashcard_generation/flashcards_with_ids.json');
    const rawCards = await response.json();

    // Initialize each card with spaced repetition data
    return rawCards.map(card => AnkiAlgorithm.initializeCard(card));
}

// Example: Simulating a study session
async function studySession() {
    const flashcards = await loadFlashcards();

    // Create a deck
    const deck: Deck = {
        id: 1,
        name: "Japanese Vocabulary",
        description: "Basic Japanese words and particles",
        flashcards: flashcards,
        date_created: new Date()
    };

    console.log("Deck Statistics:", AnkiAlgorithm.getDeckStats(deck));

    // Get due cards for today's review
    const dueCards = AnkiAlgorithm.getDueCards(deck);
    console.log(`Found ${dueCards.length} cards due for review`);

    // Simulate reviewing the first card
    if (dueCards.length > 0) {
        const card = dueCards[0];
        console.log(`\nReviewing: ${card.word_hiragana} (${card.english})`);

        // User selects "GOOD" quality
        const quality = ReviewQuality.GOOD;
        const updatedCard = AnkiAlgorithm.processReview(card, quality);

        console.log(`Card reviewed with quality: ${ReviewQuality[quality]}`);
        console.log(`New interval: ${updatedCard.interval} days`);
        console.log(`New ease factor: ${updatedCard.ease_factor}`);
        console.log(`Next review date: ${AnkiAlgorithm.getNextReviewDate(updatedCard)?.toDateString()}`);

        // Update the card in the deck
        const cardIndex = deck.flashcards.findIndex(c => c.id === card.id);
        if (cardIndex !== -1) {
            deck.flashcards[cardIndex] = updatedCard;
        }
    }

    // Show updated statistics
    console.log("\nUpdated Deck Statistics:", AnkiAlgorithm.getDeckStats(deck));
}

// Example: Getting cards for different review scenarios
function demonstrateCardFiltering() {
    // This would be called with a real deck
    console.log("Example of card filtering functions:");
    console.log("- AnkiAlgorithm.getDueCards(deck): Get cards ready for review");
    console.log("- AnkiAlgorithm.getNewCards(deck): Get cards never studied");
    console.log("- AnkiAlgorithm.isDue(card): Check if individual card is due");
    console.log("- AnkiAlgorithm.getNextReviewDate(card): Get next review date");
}

// Example: Review quality options
function showReviewOptions() {
    console.log("\nReview Quality Options:");
    console.log(`${ReviewQuality.AGAIN} - AGAIN: Card was difficult, review immediately`);
    console.log(`${ReviewQuality.HARD} - HARD: Card was somewhat difficult`);
    console.log(`${ReviewQuality.GOOD} - GOOD: Card was remembered with some effort`);
    console.log(`${ReviewQuality.EASY} - EASY: Card was remembered easily`);

    console.log("\nAlgorithm Behavior:");
    console.log("- AGAIN: Interval = 0, ease factor decreases");
    console.log("- HARD: Interval increases slightly, ease factor decreases slightly");
    console.log("- GOOD: Interval = current * ease_factor");
    console.log("- EASY: Interval = current * ease_factor * 1.3, ease factor increases");
}

// Run examples
console.log("=== Anki Algorithm Example ===");
showReviewOptions();
demonstrateCardFiltering();

// Uncomment to run actual study session (requires fetch to work)
// studySession().catch(console.error);

export { studySession, demonstrateCardFiltering, showReviewOptions };
