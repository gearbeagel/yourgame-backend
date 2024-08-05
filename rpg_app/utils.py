from transformers import pipeline

generator = pipeline('text-generation', model='distilgpt2')  # Change to a specific model if needed


def generate_initial_prompt(title, plot, characters, setting):
    prompt = (
        f"Create an engaging and intriguing opening for a story. The story should fit the following context:\n"
        f"- Title: {title}\n"
        f"- Plot Summary: {plot}\n"
        f"- Main Characters: {characters}\n"
        f"- Setting: {setting}\n\n"
        f"Here is the opening of the story:"
    )

    response = generator(prompt, max_length=200, num_return_sequences=1, truncation=True)

    generated_text = response[0]['generated_text']

    start_index = generated_text.find("Here is the opening of the story:")
    if start_index != -1:
        generated_text = generated_text[start_index + len("Here is the opening of the story:"):].strip()

    return generated_text.strip()