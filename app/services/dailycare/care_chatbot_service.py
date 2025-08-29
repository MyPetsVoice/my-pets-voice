from openai import OpenAI
from dotenv import load_dotenv
from app.services.dailycare import healthcare_service, medicalcare_service
load_dotenv()

client = OpenAI()

def get_gpt_response(user_input: str):
    response = client.chat.completions.create(
        model="gpt-4o",   
        messages=[
            {"role": "system", "content": "너는 반려동물 건강 상담 챗봇이야."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content


def main():
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        answer = get_gpt_response(user_input)
        print("Bot:", answer)

if __name__ == "__main__":
    main()
