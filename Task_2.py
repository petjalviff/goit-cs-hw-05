import string
import requests
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import matplotlib.pyplot as plt

def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Помилка з'єднання: {e}")
    return None

def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))

def map_function(word):
    return word, 1

def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)

def extract_book_info(text):
    lines = text.splitlines()
    title = None
    author = None
    for line in lines:
        if line.startswith("Title:"):
            title = line.split(":", 1)[1].strip()
        elif line.startswith("Author:"):
            author = line.split(":", 1)[1].strip()
        if title and author:
            break
    return title, author

def visualize_top_words(word_counts, title=None, author=None, top_n=10):
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*top_words)
    y_pos = range(len(words)-1, -1, -1)
    plt.figure(figsize=(12, 6))
    plt.barh(y_pos, counts, align="center")
    plt.yticks(y_pos, words, fontsize=10)
    plt.xlabel("Частота", fontsize=12)
    plt.ylabel("Слова", fontsize=12)
    title_str = f"Топ {top_n} найчастіше вживаних слів"
    if title and author:
        title_str += f" у книзі '{title}' автора {author}"
    plt.title(title_str, fontsize=14)
    plt.tight_layout()
    plt.show()

def map_reduce(text):
    if text is None:
        return None
    try:
        text = remove_punctuation(text.lower())
        words = text.split()
        with ThreadPoolExecutor() as executor:
            mapped_values = list(executor.map(map_function, words))
        shuffled_values = shuffle_function(mapped_values)
        with ThreadPoolExecutor() as executor:
            reduced_values = list(executor.map(reduce_function, shuffled_values))
        return dict(reduced_values)
    except Exception as e:
        print(f"Помилка при обробці тексту: {e}")
        return None

if __name__ == "__main__":
    url = "https://gutenberg.net.au/ebooks/m00014.txt"
    text = get_text(url)
    if text:
        title, author = extract_book_info(text)
        word_counts = map_reduce(text)
        if word_counts:
            visualize_top_words(word_counts, title, author)
        else:
            print("Не вдалося аналізувати текст.")
    else:
        print("Не вдалося завантажити текст.")