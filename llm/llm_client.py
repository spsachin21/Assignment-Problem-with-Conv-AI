from ollama import chat
import json
import streamlit as st


def ask_llm(prompt: str, expect_json: bool = True):
    """
    Sends a prompt to the LLM.

    Parameters
    ----------
    prompt : str
        Prompt to send.

    expect_json : bool
        True  -> Parse response as JSON.
        False -> Return plain text.

    Returns
    -------
    dict | str
    """

    response = chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    text = response["message"]["content"].strip()

    if expect_json:

        st.subheader("Raw LLM Response")
        st.code(text, language="json")

        try:
            return json.loads(text)  #converts json into python dictionary

        except json.JSONDecodeError:

            raise ValueError(
                "The LLM did not return valid JSON.\n\n"
                f"Raw response:\n{text}"
            )

    else:

        return text