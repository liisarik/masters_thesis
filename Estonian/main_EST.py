import os
import re
import json
import pandas as pd

def load_keywords(json_directory):
    keywords_dict = {}
    for filename in os.listdir(json_directory):
        if filename.endswith('.json'):
            file_path = os.path.join(json_directory, filename)
            category_name = os.path.splitext(filename)[0]
            with open(file_path, 'r') as file:
                data = json.load(file)
                keywords_dict[category_name] = data.get('keywords', [])
    return keywords_dict

def delete_substrings(text, substrings):
    for substring in substrings:
        text = text.replace(substring, '')
    return text

def combine_rows_with_ellipsis(df):
    combined_texts = []
    movie_names = []
    skip_next = False

    for i in range(len(df)):
        if skip_next:
            skip_next = False
            continue

        text = df.at[i, 'text']
        movie = df.at[i, 'movie']

        if text.endswith('...'):
            combined_text = text
            combined_movies = {movie}

            j = i + 1
            while j < len(df) and df.at[j, 'text'].endswith('...'):
                combined_text += ' ' + df.at[j, 'text']
                combined_movies.add(df.at[j, 'movie'])
                j += 1

            if j < len(df):
                combined_text += ' ' + df.at[j, 'text']
                combined_movies.add(df.at[j, 'movie'])
                skip_next = True

            combined_texts.append(combined_text)
            movie_names.append(', '.join(combined_movies))
        else:
            combined_texts.append(text)
            movie_names.append(movie)

    return pd.DataFrame({'text': combined_texts, 'movie': movie_names})

def find_matching_keywords(text, keywords_dict):
    matching_keywords = []
    categories = []
    for category, keywords in keywords_dict.items():
        for keyword in keywords:
            pattern = rf'(?<!\w){re.escape(keyword)}\w*' # for estonian, this will match any characters after the keyword - it allows it to capture words that start with the keyword, but prevents the keyword from being matched in the middle of a word
            if re.search(pattern, text, re.IGNORECASE):
                matching_keywords.append(keyword)
                if category not in categories:
                    categories.append(category)
    return matching_keywords, categories

def combine_text(df, index):
    texts = []
    for i in range(max(0, index - 1), min(len(df), index + 2)):
        texts.append(df.loc[i, 'text'])
    return ' '.join(texts)

def process_keywords(csv_file, output_file, keywords_dict):
    df = pd.read_csv(csv_file)
    df['text'] = df['text'].fillna('')

    substrings_to_delete = ['<i>', '</i>']
    df['text'] = df['text'].apply(lambda x: delete_substrings(x, substrings_to_delete))

    combined_df = combine_rows_with_ellipsis(df)

    new_rows = []
    for index, row in combined_df.iterrows():
        matching_keywords, categories = find_matching_keywords(row['text'], keywords_dict)
        if matching_keywords:
            combined_text = combine_text(combined_df, index)
            new_row = {
                'combined_text': combined_text,
                'movie': row['movie'],
                'matching_keywords': ', '.join(matching_keywords),
                'category': ', '.join(categories)
            }
            new_rows.append(new_row)

    filtered_df = pd.DataFrame(new_rows)
    filtered_df.to_csv(output_file, index=False)
    print(f"Filtered keywords saved to {output_file}")

def parse_srt(srt_lines, movie_name):
    subs = []
    sub = {'index': None, 'start_time': None, 'end_time': None, 'text': "", 'movie': movie_name}

    for line in srt_lines:
        line = line.strip()
        if line.isdigit():
            if sub['index'] is not None:
                subs.append(sub)
            sub = {'index': int(line), 'start_time': None, 'end_time': None, 'text': "", 'movie': movie_name}
        elif re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line):
            times = line.split(' --> ')
            sub['start_time'] = times[0]
            sub['end_time'] = times[1]
        elif line:
            sub['text'] += (line + ' ')

    if sub['index'] is not None:
        subs.append(sub)

    return subs

def process_srt_files(srt_directory, output_directory):
    for filename in os.listdir(srt_directory):
        if filename.endswith('.srt'):
            movie_name = os.path.splitext(filename)[0]
            file_path = os.path.join(srt_directory, filename)
            output_csv_path = os.path.join(output_directory, f"{movie_name}.csv")

            with open(file_path, 'r', encoding='latin-1') as file:
                srt_content = file.readlines()

            subs = parse_srt(srt_content, movie_name)
            df = pd.DataFrame(subs)
            df = df[df['text'].str.strip() != '']  # Remove empty rows
            df.to_csv(output_csv_path, index=False)
            print(f"Subtitles for {movie_name} saved to {output_csv_path}")

# Main script
srt_directory = r"C:\Users\elzbe\DATA\ESTONIAN\SRT"
output_directory = r"C:\Users\elzbe\DATA\ESTONIAN\CSV"
filtered_output_directory = r"C:\Users\elzbe\DATA\ESTONIAN\Filtered_CSV"
keywords_directory = r"C:\Users\elzbe\DATA\ESTONIAN\est_JSON"

os.makedirs(output_directory, exist_ok=True)
os.makedirs(filtered_output_directory, exist_ok=True)

process_srt_files(srt_directory, output_directory)

keywords_dict = load_keywords(keywords_directory)
for category, keywords in keywords_dict.items():
    print(f"Loaded {len(keywords)} keywords for category: {category}")

for csv_file in os.listdir(output_directory):
    if csv_file.endswith('.csv'):
        input_csv_path = os.path.join(output_directory, csv_file)
        output_csv_path = os.path.join(filtered_output_directory, csv_file.replace('.csv', '_filtered_sentences.csv'))
        process_keywords(input_csv_path, output_csv_path, keywords_dict)

print("Processing complete.")