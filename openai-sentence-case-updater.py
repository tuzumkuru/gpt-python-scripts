import sys
import os
from dotenv import load_dotenv
from openai import OpenAI
import re
import shutil
from datetime import datetime


def get_openai_api_key():
    # Load environment variables from .env file
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")

def convert_to_sentence_case(text, client):
    # Convert text to sentence case using ChatGPT
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt= "I want you to act as a journal editor.  \
                I will provide you with full title of an article and you will reply with how it should be according to APA edition 7. \
                    I want you to only reply with the corrected title inside one unique code block, and nothing else. do not write explanations. \
                        do not type commands unless I instruct you to do so. \
                            Basic Rules for Most Sources \
                                APA edition 7 uses sentenced case for showing title. \
                                    Titles and subtitles are seperated by a semi colon \
                                        When referring to the titles of books, chapters, articles, reports, webpages, or other sources, \
                                            capitalize only the first letter of the first word of the title and subtitle, \
                                                the first word after a colon or a dash in the title, and proper nouns. \
                                                    Let's start. First title is=" + text,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )        
    # Extract the generated sentence case from the API response
    sentence_case = response.choices[0].text.strip()
    return sentence_case

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
    api_key = get_openai_api_key()
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

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