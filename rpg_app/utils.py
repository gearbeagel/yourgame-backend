from transformers import pipeline

generator = pipeline('text-generation', model='gpt2')  # Change to a specific model if needed


def generate_initial_prompt(title, plot, characters, setting):
    # Structure the prompt to guide the model
    prompt = (
        f"Title: {title}\n"
        f"Plot Summary: {plot}\n"
        f"Main Characters: {characters}\n"
        f"Setting: {setting}\n\n"
        f"Generate an engaging and comedic adventure story that fits the following context:\n"
        f"In the heart of a bustling modern city, you, a seemingly ordinary person, stumble upon an ancient bookshop "
        f"tucked away in an alley. The shop's eccentric owner insists that you’re destined to find a book that will "
        f"unravel the funniest and most unexpected adventure of your life. As you open the dusty tome, "
        f"you’re transported into a whirlwind of hilarious situations, from talking animals to bizarre gadgets, "
        f"all while navigating your everyday life. Can you unravel the book’s secrets and find your way back to "
        f"reality, or will you be forever trapped in this comedic whirlwind?\n\n"
        f"Here is the adventure:"
    )

    # Generate the prompt using the Hugging Face model
    response = generator(prompt, max_length=500, num_return_sequences=1)

    # Extract and return the generated text
    generated_text = response[0]['generated_text']

    # Optionally, trim or process the text if needed
    return generated_text.strip()