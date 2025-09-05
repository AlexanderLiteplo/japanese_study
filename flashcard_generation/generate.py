import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from xai_sdk import Client
from xai_sdk.chat import user, system
from dotenv import load_dotenv

load_dotenv()

# Pydantic Models for Structured Flashcard Output
class PartOfSpeech(str, Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PRONOUN = "pronoun"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    PARTICLE = "particle"
    OTHER = "other"

class Flashcard(BaseModel):
    word_hiragana: str = Field(description="The Japanese word or phrase in hiragana")
    word_katakana: str = Field(description="The Japanese word or phrase in katakana")
    word_kanji: str = Field(description="The Japanese word or phrase in kanji")
    word_romaji: str = Field(description="The Japanese word or phrase in romaji")
    english: str = Field(description="English translation of the word")
    part_of_speech: PartOfSpeech = Field(description="Grammatical category of the word")
    example_sentence: str = Field(description="A simple example sentence using the word with hiragana")
    example_translation: str = Field(description="English translation of the example sentence")

def load_words_from_file(file_path: str) -> List[str]:
    """Load words from file synchronously"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return [word.strip() for word in file.readlines() if word.strip()]

def save_flashcards_to_file(flashcards: List[Dict[str, Any]], output_file: str):
    """Save flashcards to file synchronously, creating the file if it doesn't exist."""
    # 'w' mode will create the file if it does not exist, but ensure the directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flashcards, f, indent=2, ensure_ascii=False)

def prompt_gpt(system_prompt: str, user_prompt: str) -> str:
    # In your terminal, first run:
    # pip install xai-sdk

    client = Client(
        api_key=os.getenv("XAI_API_KEY"),
        timeout=3600,  # Override default timeout with longer timeout for reasoning models
    )

    chat = client.chat.create(model="grok-3-mini")
    chat.append(system(system_prompt))
    chat.append(user(user_prompt))

    response = chat.sample()
    return response.content

async def prompt_gpt_async(client: Client, system_prompt: str, user_prompt: str) -> Flashcard:
    """Async version of prompt_gpt for concurrent API calls with structured output

    Uses chat.aparse() to automatically parse the response into a Flashcard Pydantic model,
    eliminating the need for manual JSON parsing and providing type safety.

    Example usage:
        flashcard = await prompt_gpt_async(client, system_prompt, user_prompt)
        print(flashcard.word)  # Direct access to fields
        print(flashcard.english)
        print(flashcard.part_of_speech)
    """
    chat = client.chat.create(model="grok-3-mini")
    chat.append(system(system_prompt))
    chat.append(user(user_prompt))

    # Use parse method for structured output (run in thread pool since it's sync)
    response, flashcard = await asyncio.to_thread(chat.parse, Flashcard)
    return flashcard

async def generate_flashcard_batch(client: Client, words: List[str]) -> List[Dict[str, Any]]:
    """Generate flashcards for a batch of words concurrently"""
    system_prompt = """You are a Japanese language expert. For each Japanese word provided, create a comprehensive flashcard with accurate information. Be precise with readings, translations, and grammatical categories."""

    async def generate_single_flashcard(word: str) -> Dict[str, Any]:
        user_prompt = f"Create a flashcard for the Japanese word: {word}"
        try:
            # Use structured output - returns Flashcard object directly
            flashcard = await prompt_gpt_async(client, system_prompt, user_prompt)
            # Convert Pydantic model to dictionary for JSON serialization
            return flashcard.model_dump()
        except Exception as e:
            print(f"Error generating flashcard for '{word}': {e}")
            # Return a basic fallback as dictionary
            return {
                "word": word,
                "reading": word,  # fallback
                "english": "Translation not available",
                "part_of_speech": "other",
                "example_sentence": f"{word} example",
                "example_translation": "Example translation not available"
            }

    # Generate flashcards for all words in the batch concurrently
    tasks = [generate_single_flashcard(word) for word in words]
    flashcards = await asyncio.gather(*tasks)
    return flashcards

async def generate_flashcards():
    """Generate flashcards for all words in common.txt using concurrent API calls"""
    file_path = "./common.txt"

    # Load words from file (using thread pool for async compatibility)
    common_words = await asyncio.to_thread(load_words_from_file, file_path)

    print(f"Loaded {len(common_words)} words from {file_path}")

    # Create client once and reuse for all batches
    client = Client(
        api_key=os.getenv("XAI_API_KEY"),
        timeout=3600,
    )

    all_flashcards = []
    batch_size = 20

    # Process words in batches of 20
    for i in range(0, len(common_words), batch_size):
        batch_words = common_words[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(common_words) + batch_size - 1) // batch_size

        print(f"Processing batch {batch_num}/{total_batches} (words {i+1}-{min(i+batch_size, len(common_words))})")

        # Log each API call for this batch
        for word in batch_words:
            print(f"API call: Generating flashcard for '{word}'")

        # Generate flashcards for this batch concurrently
        batch_flashcards = await generate_flashcard_batch(client, batch_words)

        # Log the output for each API call
        for word, flashcard in zip(batch_words, batch_flashcards):
            print(f"API output for '{word}': {flashcard}")

        # Add to our collection
        all_flashcards.extend(batch_flashcards)

        # Save progress after each batch (using thread pool for async compatibility)
        output_file = "./flashcard_generation/flashcards.json"
        await asyncio.to_thread(save_flashcards_to_file, all_flashcards, output_file)

        print(f"Saved {len(all_flashcards)} flashcards so far...")

        # Small delay between batches to be respectful to the API
        if i + batch_size < len(common_words):
            await asyncio.sleep(1)

    print(f"Completed! Generated {len(all_flashcards)} flashcards")
    return all_flashcards




async def main():
    """
    Main function that runs when script is called directly
    """
    print("Starting flashcard generation...")
    await generate_flashcards()
    print("Flashcard generation completed!")

def run_main():
    """Wrapper to run async main function"""
    asyncio.run(main())

async def test_small_batch():
    """Test function to generate flashcards for just the first 5 words"""
    print("Testing with small batch...")

    # Load first 5 words
    file_path = "./common.txt"
    common_words = await asyncio.to_thread(load_words_from_file, file_path)
    common_words = common_words[:5]

    print(f"Testing with words: {common_words}")

    # Create client
    client = Client(
        api_key=os.getenv("XAI_API_KEY"),
        timeout=3600,
    )

    # Generate flashcards for these 5 words
    flashcards = await generate_flashcard_batch(client, common_words)

    # Save to test file
    await asyncio.to_thread(save_flashcards_to_file, flashcards, "./test_flashcards.json")

    print("Test completed! Check test_flashcards.json")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test_small_batch())
    else:
        run_main()
