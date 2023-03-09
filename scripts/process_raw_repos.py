import concurrent
import json
import logging
import os
import re

import tiktoken

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


def clean_text(text):
    # Remove comments
    text = re.sub(r'//.*?\n|/\*.*?\*/', '', text, flags=re.DOTALL)

    # Remove preprocessor directives
    text = re.sub(r'#.*?\n', '', text)

    # Replace newlines with semicolons
    text = text.replace('\n', ';')

    # Remove non-alphanumeric characters
    text = re.sub(r'[^a-z0-9 ;]', '', text)

    return text


def process_file(input_file, output_dir, remaining_files):
    try:
        # Get the file content
        with open(input_file, 'r') as f:
            content = f.read()

        # Get the word count
        word_count = len(content.split())

        # Get the token count
        tokens = encoding.encode(content)
        token_count = len(tokens)

        # Construct the JSON object
        filename, extension = os.path.splitext(os.path.basename(input_file))
        output_obj = {
            'filename': filename,
            'filepath': os.path.relpath(input_file, start=input_dir),
            'content': content,
            'word_count': word_count,
            'tokens': tokens,
            'token_count': token_count
        }

        # Write the JSON object to a file
        output_file = os.path.join(
            output_dir, f"{filename}_{extension[1:]}.json")
        with open(output_file, 'w') as f:
            json.dump(output_obj, f, indent=2)

        # Update the remaining files count
        remaining_files[0] -= 1

    except UnicodeDecodeError as e:
        logging.warning(f"Could not process file: {input_file} ({e})")


def process_directory(input_dir, output_parent_dir, files):
    # Recursively process files in the input directory
    remaining_files = [
        len([file for file in files if not file.startswith('.')])]

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.startswith('.'):
                continue
            input_file = os.path.join(root, file)
            logging.info(f"Processing file: {input_file}")
            output_dir = os.path.join(
                output_parent_dir, os.path.relpath(root, start=input_dir))
            process_file(input_file, output_dir, remaining_files)

        # Recreate the directory structure in the output directory
        for dir in dirs:
            input_subdir = os.path.join(root, dir)
            if not input_subdir.startswith(input_dir):
                continue
            output_subdir = os.path.join(
                output_parent_dir, os.path.relpath(input_subdir, start=input_dir))
            if not os.path.exists(output_subdir):
                os.mkdir(output_subdir)

    # Log completion
    logging.info(f"Finished processing directory: {input_dir}")

    # Log completion
    logging.info(f"Finished processing directory: {input_dir}")


input_parent_dir = '../raw_repos'
output_parent_dir = '../processed_repos'

# Create the output directory if it doesn't exist
if not os.path.exists(output_parent_dir):
    os.makedirs(output_parent_dir)

# Recursively get a list of all the directories to process
dirs = [os.path.join(dp, d)
        for dp, dn, fn in os.walk(input_parent_dir) for d in dn]

# Create a thread pool and submit each directory to be processed
max_workers = os.cpu_count() or 1
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = []
    for input_dir in dirs:
        output_dir = os.path.join(output_parent_dir, os.path.relpath(
            input_dir, start=input_parent_dir))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        files = os.listdir(input_dir)
        future = future = executor.submit(
            process_directory, input_dir, output_dir, files)

        futures.append(future)

    # Wait for all futures to complete
    while futures:
        for future in concurrent.futures.as_completed(futures):
            futures.remove(future)
            try:
                future.result()
            except Exception as e:
                logging.exception(e)
