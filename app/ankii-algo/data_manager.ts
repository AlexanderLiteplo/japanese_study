// Data management utilities for flashcards and progress tracking
import { Flashcard, AnkiAlgorithm } from './ankii';
import fs from 'fs';
import path from 'path';

export interface FlashcardProgress {
    id: number;
    date_last_studied: string | null; // ISO string when loaded from JSON
    num_times_studied: number;
    ease_factor: number;
    interval: number;
    repetitions: number;
    total_correct: number;
    total_incorrect: number;
    total_studied: number;
    total_correct_streak: number;
    total_incorrect_streak: number;
}

export interface BaseFlashcard {
    id: number;
    word_hiragana: string;
    word_katakana: string;
    word_kanji: string;
    word_romaji: string;
    english: string;
    part_of_speech: string;
    example_sentence: string;
    example_translation: string;
}

export class FlashcardDataManager {
    private flashcardsPath: string;
    private progressPath: string;

    constructor(
        flashcardsPath: string = './flashcard_generation/flashcard_generation/flashcards_with_ids.json',
        progressPath: string = './flashcard_generation/flashcard_generation/flashcard_progress.json'
    ) {
        this.flashcardsPath = flashcardsPath;
        this.progressPath = progressPath;
    }

    /**
     * Load base flashcard data from JSON file
     */
    async loadBaseFlashcards(): Promise<BaseFlashcard[]> {
        try {
            const data = await fs.promises.readFile(this.flashcardsPath, 'utf-8');
            return JSON.parse(data);
        } catch (error) {
            console.error('Error loading base flashcards:', error);
            throw error;
        }
    }

    /**
     * Load progress data from JSON file
     */
    async loadProgressData(): Promise<FlashcardProgress[]> {
        try {
            const data = await fs.promises.readFile(this.progressPath, 'utf-8');
            return JSON.parse(data);
        } catch (error) {
            console.error('Error loading progress data:', error);
            throw error;
        }
    }

    /**
     * Save progress data to JSON file
     */
    async saveProgressData(progressData: FlashcardProgress[]): Promise<void> {
        try {
            const data = JSON.stringify(progressData, null, 2);
            await fs.promises.writeFile(this.progressPath, data, 'utf-8');
        } catch (error) {
            console.error('Error saving progress data:', error);
            throw error;
        }
    }

    /**
     * Merge base flashcard data with progress data to create complete Flashcard objects
     */
    mergeFlashcardData(
        baseCards: BaseFlashcard[],
        progressData: FlashcardProgress[]
    ): Flashcard[] {
        const progressMap = new Map(progressData.map(p => [p.id, p]));

        return baseCards.map(baseCard => {
            const progress = progressMap.get(baseCard.id);

            if (!progress) {
                console.warn(`No progress data found for card ID ${baseCard.id}`);
                return AnkiAlgorithm.initializeCard(baseCard);
            }

            // Convert date string back to Date object if it exists
            const dateLastStudied = progress.date_last_studied
                ? new Date(progress.date_last_studied)
                : null;

            return {
                ...baseCard,
                date_last_studied: dateLastStudied,
                num_times_studied: progress.num_times_studied,
                ease_factor: progress.ease_factor,
                interval: progress.interval,
                repetitions: progress.repetitions,
                total_correct: progress.total_correct,
                total_incorrect: progress.total_incorrect,
                total_studied: progress.total_studied,
                total_correct_streak: progress.total_correct_streak,
                total_incorrect_streak: progress.total_incorrect_streak
            };
        });
    }

    /**
     * Extract progress data from Flashcard objects for saving
     */
    extractProgressData(flashcards: Flashcard[]): FlashcardProgress[] {
        return flashcards.map(card => ({
            id: card.id,
            date_last_studied: card.date_last_studied ? card.date_last_studied.toISOString() : null,
            num_times_studied: card.num_times_studied,
            ease_factor: card.ease_factor,
            interval: card.interval,
            repetitions: card.repetitions,
            total_correct: card.total_correct,
            total_incorrect: card.total_incorrect,
            total_studied: card.total_studied,
            total_correct_streak: card.total_correct_streak,
            total_incorrect_streak: card.total_incorrect_streak
        }));
    }

    /**
     * Load complete flashcards with progress data
     */
    async loadCompleteFlashcards(): Promise<Flashcard[]> {
        const [baseCards, progressData] = await Promise.all([
            this.loadBaseFlashcards(),
            this.loadProgressData()
        ]);

        return this.mergeFlashcardData(baseCards, progressData);
    }

    /**
     * Save updated flashcards (extracts and saves only progress data)
     */
    async saveFlashcards(flashcards: Flashcard[]): Promise<void> {
        const progressData = this.extractProgressData(flashcards);
        await this.saveProgressData(progressData);
    }

    /**
     * Update a single flashcard's progress and save
     */
    async updateAndSaveCard(card: Flashcard): Promise<void> {
        const allProgress = await this.loadProgressData();
        const progressIndex = allProgress.findIndex(p => p.id === card.id);

        if (progressIndex === -1) {
            throw new Error(`Progress data not found for card ID ${card.id}`);
        }

        // Update the progress data
        allProgress[progressIndex] = {
            id: card.id,
            date_last_studied: card.date_last_studied ? card.date_last_studied.toISOString() : null,
            num_times_studied: card.num_times_studied,
            ease_factor: card.ease_factor,
            interval: card.interval,
            repetitions: card.repetitions,
            total_correct: card.total_correct,
            total_incorrect: card.total_incorrect,
            total_studied: card.total_studied,
            total_correct_streak: card.total_correct_streak,
            total_incorrect_streak: card.total_incorrect_streak
        };

        await this.saveProgressData(allProgress);
    }
}

// Convenience functions for common operations
export async function loadFlashcards(): Promise<Flashcard[]> {
    const manager = new FlashcardDataManager();
    return manager.loadCompleteFlashcards();
}

export async function saveFlashcards(flashcards: Flashcard[]): Promise<void> {
    const manager = new FlashcardDataManager();
    return manager.saveFlashcards(flashcards);
}

export async function updateCardProgress(card: Flashcard): Promise<void> {
    const manager = new FlashcardDataManager();
    return manager.updateAndSaveCard(card);
}
