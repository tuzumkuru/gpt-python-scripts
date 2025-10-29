import sys
import os
from dotenv import load_dotenv
from ollama import Client
import re
import shutil
from datetime import datetime

OLLAMA_HOST = 'http://192.168.1.77:11434'

def convert_to_sentence_case(text, client:Client):
    # # Convert text to sentence case using ChatGPT
    # response = client.completions.create(
    #     model="gpt-3.5-turbo-instruct",
    #     prompt=text + "\nConvert the title above to APA version 7 style.",
    #     max_tokens=50,
    #     n=1,
    #     stop=None,
    #     temperature=0,
    #     top_p=1,
    #     frequency_penalty=0,
    #     presence_penalty=0
    # )        
    # # Extract the generated sentence case from the API response
    # sentence_case = response.choices[0].text.strip()
    # return sentence_case
    # response = client.chat(model='llama2', messages=[
    # {
    #     'role': 'system',
    #     'content': 'You are a journal editor. Providing no additional text than the result change the given title of an article into APA edition 7 style sentenced text:\n' + text, 
    # },
    # ])

    response = client.generate(model='gemma', 
                               prompt='Convert the title to APA edition 7 style. It should be in sentence case:\n' + text + "\n Type me the correct result only.",
                               system="You are an editor of a journal. Answer without providing any comments, explanations, greetings or any additional text then the asked question"
                               )
    
    # return response['message']['content']
    return response["response"]


def generate_copy_filename(original_file):
    # Split the original file name and extension
    file_name, file_extension = os.path.splitext(original_file)
    # Generate copy file name with current date and time and extension at the end
    current_time = datetime.now().strftime("%Y%m%d%H%M")
    return f'{file_name}_output_{current_time}{file_extension}'

def copy_original_file(original_file, copy_file):
    # Copy the original file
    shutil.copyfile(original_file, copy_file)

def process_file(original_file, copy_file, client):
    # Get total number of lines
    total_lines = sum(1 for line in open(copy_file))

    # Open the copy file
    with open(copy_file, 'r') as file:
        lines = file.readlines()
    
    # Open the copy file again in write mode to update it
    with open(copy_file, 'w') as file:
        # Iterate through the lines
        for idx, line in enumerate(lines):
            # Check if the line contains <dc:title>
            if '<dc:title>' in line:
                # Extract the title text using regex
                title_text = re.search(r'<dc:title>(.*?)</dc:title>', line).group(1)
                # Convert the title text to sentence case
                sentence_case = convert_to_sentence_case(title_text, client)
                # Write the converted line to the file
                file.write(line.replace(title_text, sentence_case))
                # Print progress
                progress = (idx + 1) / total_lines * 100
                print(f'Processing line {idx + 1}/{total_lines} - {progress:.2f}% complete')
                print(f'Original Title: {title_text}')
                print(f'Converted Title: {sentence_case}\n')
            else:                
                # file.write(line)  # Write the unchanged line to the file
                pass

def main():
    # Get OpenAI API key
    # api_key = get_openai_api_key()
    # Initialize OpenAI client
    # client = OpenAI(api_key=api_key)
    client = Client(host=OLLAMA_HOST)

    # Original file name
    if len(sys.argv) == 2:
        original_file = sys.argv[1]
    else:
        original_file = input("Please enter the filename: ")

    # Check if the provided file exists
    if not os.path.exists(original_file):
        print(f"Error: File '{original_file}' not found.")
        return

    # Generate copy file name
    copy_file_name = generate_copy_filename(original_file)

    # Copy the original file
    copy_original_file(original_file, copy_file_name)

    try:
        process_file(original_file, copy_file_name, client)
    except KeyboardInterrupt:
        print(f"\nExiting!")
        pass

    

if __name__ == "__main__":
    main()
