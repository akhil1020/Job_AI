from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama

from gmail_tool import send_email_tool


llm = ChatOllama(
    model="gemma4",
    base_url="http://127.0.0.1:11434",
    temperature=0,
)

tools = [send_email_tool]

SYSTEM_PROMPT = """
You are an AI Job Application Assistant.

Your job:
- Help the user analyze a job description and prepare a tailored application
- Write professional job application emails
- Reuse the job description shared earlier in the conversation when the user says "this JD" or "the job description"
- Always use resume file path: resume.pdf
- Never ask the user for the resume file path
- Always assume attachment is resume.pdf

When the user requests sending an email:
- Determine the correct recipient email
- Generate a professional subject line
- Write a concise, tailored body
- Use send_email_tool

When the user shares a job description:
- Understand the role, company, required skills, and tone
- Keep that context for the rest of the chat session

Be concise, helpful, and action-oriented.
"""

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)


def run_agent(messages: list) -> dict:
    return agent.invoke({"messages": messages})


def extract_assistant_text(messages: list) -> str:
    ai_text_parts = []
    tool_updates = []

    for message in messages:
        if isinstance(message, AIMessage):
            content = message.content
            if isinstance(content, str):
                text = content.strip()
                if text:
                    ai_text_parts.append(text)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "").strip()
                        if text:
                            ai_text_parts.append(text)
        elif isinstance(message, ToolMessage):
            text = str(message.content).strip()
            if text:
                tool_updates.append(text)

    combined_parts = ai_text_parts + tool_updates
    return "\n".join(combined_parts).strip()


def read_multiline_input(prompt: str) -> str:
    print(prompt)
    print("Finish with a single line containing END")

    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    return "\n".join(lines).strip()


def chat_cli() -> None:
    print("Job Application Assistant CLI")
    print("Commands: /jd to paste a job description, /quit to exit")
    print("Example: Take this JD and send a job application to recruiter@company.com")

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() in {"/quit", "quit", "exit"}:
            print("Session closed.")
            break

        if user_input.lower() == "/jd":
            jd_text = read_multiline_input("Paste the job description below.")
            if not jd_text:
                print("Assistant: No job description was captured.")
                continue

            user_input = (
                "Here is the job description. Save it for this session and use it "
                "when I later ask you to draft or send a job application:\n\n"
                f"{jd_text}"
            )

        messages.append(HumanMessage(content=user_input))
        response = run_agent(messages)
        messages = response["messages"]

        assistant_text = extract_assistant_text(messages)
        if assistant_text:
            print(f"Assistant: {assistant_text}")
        else:
            print("Assistant: I processed that, but I do not have a text response to show.")


if __name__ == "__main__":
    chat_cli()
