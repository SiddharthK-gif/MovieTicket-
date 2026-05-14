import os
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

def get_weather_from_gemini(city: str) -> str:
    """Ask Gemini for the current weather in the requested city."""
    if not city.strip():
        return "No city provided."

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "GOOGLE_API_KEY is not set. Please set the environment variable before running."

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=api_key)
    prompt = (
        f"Tell me the current weather in {city.strip()}. "
        "Answer in one short sentence describing the weather only."
    )

    try:
        response = model.invoke(prompt)
    except Exception as exc:
        return f"Weather service error: {exc}"

    if hasattr(response, "content") and response.content is not None:
        return response.content.strip()

    if hasattr(response, "content_blocks") and response.content_blocks:
        first = response.content_blocks[0]
        if isinstance(first, dict) and "text" in first:
            return first["text"].strip()

    return str(response)


def is_good_weather(weather_text: str) -> bool:
    text = weather_text.lower()
    bad_keywords = [
        "rain",
        "storm",
        "snow",
        "sleet",
        "hail",
        "windy",
        "thunder",
        "tornado",
        "blizzard",
        "freezing",
        "cold",
        "overcast",
    ]
    good_keywords = [
        "sunny",
        "clear",
        "warm",
        "pleasant",
        "nice",
        "bright",
        "mild",
    ]

    if any(keyword in text for keyword in bad_keywords):
        return False
    if any(keyword in text for keyword in good_keywords):
        return True
    return "cloud" not in text


def main() -> None:
    city = input("What city are you in? ").strip()
    if not city:
        print("Please enter a city name.")
        return

    weather_report = get_weather_from_gemini(city)
    print(weather_report)

    if is_good_weather(weather_report):
        print("It's a good day to go out and have a nice day.")
    else:
        print("Stay cozy inside because the weather is bad.")


if __name__ == "__main__":
    main()