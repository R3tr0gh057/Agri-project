from openai import OpenAI
client = OpenAI()

def response_gen(content):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": content
                }
            ]
        )

        return(completion.choices[0].message)
    
    except Exception as e:
        print("Error generating response:", str(e))
        return None

if __name__ == "__main__":
    while True:
        user_input = input("Query: ")
        response = response_gen(user_input)
        print("Assistant:", response)