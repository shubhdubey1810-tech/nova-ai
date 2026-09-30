# NØVA AI 1.0
# Main application

from datetime import datetime


NOVA_NAME = "NØVA AI"
VERSION = "1.0.0"


def show_banner():
    print("=" * 50)
    print(f"        {NOVA_NAME}")
    print(f"        Version {VERSION}")
    print("        Your Intelligent Personal Assistant")
    print("=" * 50)
    print()


def get_response(user_input):
    command = user_input.lower().strip()

    if command in ["hello", "hi", "hey"]:
        return "Hello! I am NØVA. How can I help you?"

    if "your name" in command:
        return f"My name is {NOVA_NAME}."

    if "version" in command:
        return f"I am running NØVA AI version {VERSION}."

    if "time" in command:
        return f"The current time is {datetime.now().strftime('%I:%M:%S %p')}."

    if command in ["exit", "quit", "bye"]:
        return None

    return (
        "I received your request. My AI engine is not connected yet. "
        "We will connect it in the next step."
    )


def main():
    show_banner()

    print("NØVA is ready.")
    print("Type 'exit' to close NØVA.")
    print()

    while True:
        user_input = input("You: ")

        response = get_response(user_input)

        if response is None:
            print("NØVA: Goodbye!")
            break

        print(f"NØVA: {response}")
        print()


if __name__ == "__main__":
    main()