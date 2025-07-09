


def get_llm_responses(
    prompt,
    client,
    model,
    system_message,
    print_debug=False,
    message_history=[],
    temperature=0.7,
    n_responses=1,
):
    if 'gemini' in model:
        new_message = message_history + [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                *new_message,
            ],
            temperature=temperature,
            max_tokens=MAX_NUM_TOKENS,
            n=n_responses,
            stop=None,
        )
        content = [r.message.content for r in response.choices]
        new_message_history = [
            new_message_history + [{"role": "assistant", "content": c}] for c in content
        ]
    return content, new_message_history