// Anki SM-2 Algorithm Implementation
// Based on the SuperMemo SM-2 spaced repetition algorithm

export enum ReviewQuality {
    AGAIN = 0,
    HARD = 1,
    GOOD = 2,
    EASY = 3
}

export interface Flashcard {
    id: number;
    word_hiragana: string;
    word_katakana: string;
    word_kanji: string;
    word_romaji: string;
    english: string;
    part_of_speech: string;
    example_sentence: string;
    example_translation: string;
    // Spaced repetition fields
    date_last_studied: Date | null;
    num_times_studied: number;
    ease_factor: number; // Starts at 2.5, minimum 1.3
    interval: number; // Days until next review
    repetitions: number; // Number of successful reviews in a row
    total_correct: number;
    total_incorrect: number;
    total_studied: number;
    total_correct_streak: number;
    total_incorrect_streak: number;
}

export interface Deck {
    id: number;
    name: string;
    description: string;
    flashcards: Flashcard[];
    date_created: Date;
}

export class AnkiAlgorithm {
    private static readonly INITIAL_EASE_FACTOR = 2.5;
    private static readonly MINIMUM_EASE_FACTOR = 1.3;
    private static readonly INITIAL_INTERVAL = 1; // 1 day for new cards
    private static readonly GRADUATING_INTERVAL = 6; // 6 days after first correct review

    /**
     * Calculate the next review date for a flashcard
     * @param card The flashcard to calculate next review for
     * @returns Date when the card should be reviewed next, or null if never studied
     */
    static getNextReviewDate(card: Flashcard): Date | null {
        if (card.date_last_studied === null) {
            return null; // Never studied
        }

        const nextReview = new Date(card.date_last_studied);
        nextReview.setDate(nextReview.getDate() + card.interval);
        return nextReview;
    }

    /**
     * Check if a flashcard is due for review
     * @param card The flashcard to check
     * @returns true if the card should be reviewed now
     */
    static isDue(card: Flashcard): boolean {
        if (card.date_last_studied === null) {
            return true; // New cards are always due
        }

        const nextReview = this.getNextReviewDate(card);
        if (!nextReview) return true;

        return new Date() >= nextReview;
    }

    /**
     * Initialize a new flashcard with default spaced repetition values
     * @param baseCard The base flashcard data (without SR fields)
     * @returns Flashcard with initialized SR fields
     */
    static initializeCard(baseCard: Omit<Flashcard, 'date_last_studied' | 'num_times_studied' | 'ease_factor' | 'interval' | 'repetitions' | 'total_correct' | 'total_incorrect' | 'total_studied' | 'total_correct_streak' | 'total_incorrect_streak'>): Flashcard {
        return {
            ...baseCard,
            date_last_studied: null,
            num_times_studied: 0,
            ease_factor: this.INITIAL_EASE_FACTOR,
            interval: this.INITIAL_INTERVAL,
            repetitions: 0,
            total_correct: 0,
            total_incorrect: 0,
            total_studied: 0,
            total_correct_streak: 0,
            total_incorrect_streak: 0
        };
    }

    /**
     * Process a review response and update the flashcard's spaced repetition data
     * @param card The flashcard being reviewed
     * @param quality The quality of the review (AGAIN, HARD, GOOD, EASY)
     * @returns Updated flashcard with new SR values
     */
    static processReview(card: Flashcard, quality: ReviewQuality): Flashcard {
        const updatedCard = { ...card };
        const now = new Date();

        // Update study statistics
        updatedCard.num_times_studied++;
        updatedCard.total_studied++;
        updatedCard.date_last_studied = now;

        if (quality === ReviewQuality.AGAIN) {
            // Again: Reset repetitions, interval = 0 (review immediately)
            updatedCard.repetitions = 0;
            updatedCard.interval = 0;
            updatedCard.ease_factor = Math.max(this.MINIMUM_EASE_FACTOR, updatedCard.ease_factor - 0.2);
            updatedCard.total_incorrect++;
            updatedCard.total_incorrect_streak++;
            updatedCard.total_correct_streak = 0;
        } else {
            // Correct answer
            updatedCard.total_correct++;
            updatedCard.total_correct_streak++;
            updatedCard.total_incorrect_streak = 0;

            if (quality === ReviewQuality.HARD) {
                // Hard: Slight penalty to ease factor, small interval increase
                updatedCard.ease_factor = Math.max(this.MINIMUM_EASE_FACTOR, updatedCard.ease_factor - 0.15);
                updatedCard.interval = Math.min(6, updatedCard.interval * 1.2);
                updatedCard.repetitions = Math.max(0, updatedCard.repetitions - 1); // Slight penalty
            } else if (quality === ReviewQuality.GOOD) {
                // Good: Standard interval calculation
                if (updatedCard.repetitions === 0) {
                    // Graduating from learning phase
                    updatedCard.interval = this.GRADUATING_INTERVAL;
                } else {
                    updatedCard.interval = Math.round(updatedCard.interval * updatedCard.ease_factor);
                }
                updatedCard.repetitions++;
            } else if (quality === ReviewQuality.EASY) {
                // Easy: Bonus to ease factor and interval
                updatedCard.ease_factor += 0.15;
                if (updatedCard.repetitions === 0) {
                    // Graduating from learning phase
                    updatedCard.interval = Math.round(this.GRADUATING_INTERVAL * updatedCard.ease_factor * 1.3);
                } else {
                    updatedCard.interval = Math.round(updatedCard.interval * updatedCard.ease_factor * 1.3);
                }
                updatedCard.repetitions++;
            }
        }

        return updatedCard;
    }

    /**
     * Get cards that are due for review
     * @param deck The deck to check
     * @returns Array of flashcards that are due
     */
    static getDueCards(deck: Deck): Flashcard[] {
        return deck.flashcards.filter(card => this.isDue(card));
    }

    /**
     * Get new cards (never studied)
     * @param deck The deck to check
     * @returns Array of new flashcards
     */
    static getNewCards(deck: Deck): Flashcard[] {
        return deck.flashcards.filter(card => card.date_last_studied === null);
    }

    /**
     * Calculate review statistics for a deck
     * @param deck The deck to analyze
     * @returns Statistics object
     */
    static getDeckStats(deck: Deck) {
        const totalCards = deck.flashcards.length;
        const newCards = this.getNewCards(deck).length;
        const dueCards = this.getDueCards(deck).length;
        const studiedCards = totalCards - newCards;

        return {
            totalCards,
            newCards,
            dueCards,
            studiedCards,
            completionRate: studiedCards > 0 ? (studiedCards / totalCards) * 100 : 0
        };
    }
}