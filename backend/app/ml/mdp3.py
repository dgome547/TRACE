import random
import re
from collections import defaultdict
import numpy as np
from typing import Dict, List, Tuple, Set
import csv
import os
import aiohttp
import asyncio
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .AI_Wordlist import AIWordlist

# =====================
# Natural Language Processing (NLP) Subroutines
# =====================

def normalize_text(text):
    text = re.sub(r'[\u201c\u201d\u2018\u2019\u2013\u2014]', '', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = text.encode('ascii', errors='ignore').decode('utf-8')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_compound_words(text):
    return re.sub(r'-', ' ', text)

def filter_words(words, stopwords, acronyms):
    filtered = []
    for word in words:
        if len(word) >= 4 or word.upper() in acronyms:
            filtered.append(word)
    return filtered

def remove_specific_determiners(words):
    definite_articles = {"the"}
    demonstrative = {"this", "that", "these", "those"}
    distributive = {"each", "every", "either", "neither"}
    interrogative = {"which", "what", "whose"}
    possessive = {"my", "your", "his", "her", "its", "our", "their"}
    allowed_possessives = {"myaccount", "myprofile", "youradmin", "yourportal", "theirserver", "ourapp"}
    
    remove = definite_articles | demonstrative | distributive | interrogative
    cleaned = [
        word for word in words if (
            word.lower() not in remove and
            (word.lower() not in possessive or word.lower() in allowed_possessives)
        )
    ]
    return cleaned

def nlp_subroutine(csv_path: str):
    stopwords = {"and", "or"}
    acronyms = {"AI", "NLP", "USA"}
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    cleaned_rows = []
    with open(csv_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames or not {"id", "content", "url"}.issubset(fieldnames):
            raise ValueError("CSV must have columns: id, content, url")

        for row in reader:
            text = row["content"] if row["content"] else ""
            text = normalize_text(text)
            text = split_compound_words(text)
            words = re.findall(r'\w+', text, flags=re.IGNORECASE)
            words = remove_specific_determiners(words)
            words = filter_words(words, stopwords, acronyms)
            cleaned_text = " ".join(words)
            row["content"] = cleaned_text
            cleaned_rows.append(row)

    with open(csv_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print(f"[NLP] Cleaned CSV: {csv_path}")


# =====================
# CSV Loading Helpers
# =====================

def load_urls_from_csv(csv_path: str) -> List[str]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    urls = []
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if not {"id", "website"}.issubset(set(reader.fieldnames or [])):
            raise ValueError("CSV must have columns: id, website")
        for row in reader:
            if row["website"]:
                urls.append(row["website"].strip())
    return urls

def load_web_text(csv_path: str) -> str:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if not {"id", "content", "url"}.issubset(set(reader.fieldnames or [])):
            raise ValueError("CSV must have columns: id, content, url")
        contents = [row["content"].lower() for row in reader if row["content"]]
    return " ".join(contents)

def load_wordlist(file_path: str) -> List[str]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Wordlist not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        words = [line.strip().lower() for line in file if line.strip()]
    return words

# =====================
# WebScraper Class
# =====================

class WebScraper:
    def __init__(self, urls):
        self.urls = urls
        self.hierarchy = self.organize_urls(urls)

    def organize_urls(self, urls):
        hierarchy = defaultdict(list)
        for url in urls:
            domain = urlparse(url).netloc
            hierarchy[domain].append(url)
        return hierarchy

    async def fetch_page(self, session, url):
        try:
            async with session.get(url, timeout=10) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                text = " ".join([tag.get_text() for tag in soup.find_all(["p", "h1", "h2", "h3", "span"])])
                logo_text = " ".join([tag["alt"] for tag in soup.find_all("img", alt=True)])
                label_text = " ".join([tag.get_text() for tag in soup.find_all("label")])
                class_text = " ".join([" ".join(tag["class"]) for tag in soup.find_all(class_=True) if tag.get("class")])
                combined = f"{text} {logo_text} {label_text} {class_text}"
                return url, combined
        except Exception as e:
            print(f"[Scraper] Error fetching {url}: {e}")
            return url, ""

    async def scrape_pages(self, batch_size=10):
        results = []
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(self.urls), batch_size):
                batch = self.urls[i:i+batch_size]
                tasks = [self.fetch_page(session, url) for url in batch]
                responses = await asyncio.gather(*tasks)
                results.extend(responses)
                await asyncio.sleep(0.5)
        return results

    def generate_csv(self, filename):
        data = asyncio.run(self.scrape_pages())
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "content", "url"])
            writer.writerows(data)
        print(f"[Scraper] CSV generated: {filename}")

# =====================
# CredentialMDP Class (handles the Markov chain learning)
# =====================

class CredentialMDP:
    def __init__(self, order: int = 4, gamma: float = 0.8):
        self.order = order
        self.gamma = gamma
        self.q_values: Dict[str, Dict[Tuple[str, str], float]] = defaultdict(lambda: defaultdict(float))
        self.state_transitions: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        self.used_usernames: Set[str] = set()

        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.95
        self.learning_rate = 0.3
        self.num_credentials_generated = 0

        self.initial_states: List[str] = []

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            self.epsilon = max(self.epsilon, self.epsilon_min)

    def calculate_password_strength(self, password: str) -> float:
        score = 0.0
        if len(password) >= 12:
            score += 0.25
        elif len(password) >= 8:
            score += 0.15
        if re.search(r'[A-Z]', password):
            score += 0.2
        if re.search(r'[0-9]', password):
            score += 0.2
        if re.search(r'[!@#$%^&*]', password):
            score += 0.2
        if len(set(password)) >= 8:
            score += 0.1
        return score

    def calculate_username_quality(self, username: str) -> float:
        score = 0.0
        if len(username) >= 8:
            score += 0.3
        elif len(username) >= 5:
            score += 0.2
        if username not in self.used_usernames:
            score += 0.4
        if re.match(r'^[a-z]', username):
            score += 0.2
        if not re.search(r'\s', username):
            score += 0.1
        return score

    def get_reward(self, state: str, action: str, next_char: str) -> float:
        current = state[9:] + next_char
        if 'password' in state:
            return self.calculate_password_strength(current) / len(current)
        else:
            return self.calculate_username_quality(current) / len(current)

    def update_learning_rate(self):
        self.learning_rate = max(0.05, 0.03 * (0.99 ** self.num_credentials_generated))

    def register_credential_generation(self):
        self.num_credentials_generated += 1
        self.update_learning_rate()

    def get_possible_actions(self, state: str) -> List[str]:
        return list(self.state_transitions[state].keys())

    def choose_action(self, state: str) -> Tuple[str, str]:
        possible_actions = self.get_possible_actions(state)
        if not possible_actions:
            return "", ""

        if random.random() < self.epsilon:
            action = random.choice(possible_actions)
            next_char = random.choice(list(self.state_transitions[state][action]))
        else:
            action_values = {}
            for act in possible_actions:
                if self.state_transitions[state][act]:
                    value = max([self.q_values[state][(act, nxt_ch)] for nxt_ch in self.state_transitions[state][act]])
                    action_values[act] = value

            if action_values:
                action = max(action_values.items(), key=lambda x: x[1])[0]
                next_char = random.choice(list(self.state_transitions[state][action]))
            else:
                action = random.choice(possible_actions)
                next_char = random.choice(list(self.state_transitions[state][action]))

        return action, next_char

    def update_q_value(self, state: str, action: str, next_char: str, next_state: str, reward: float):
        next_action_values = []
        for next_action in self.get_possible_actions(next_state):
            for next_next_char in self.state_transitions[next_state][next_action]:
                next_action_values.append(self.q_values[next_state][(next_action, next_next_char)])
        max_next_q = max(next_action_values, default=0)
        current_q = self.q_values[state][(action, next_char)]
        new_q = current_q + self.learning_rate * (reward + self.gamma * max_next_q - current_q)
        self.q_values[state][(action, next_char)] = new_q

# ============================
# CredentialGeneratorMDP Class
# ============================

class CredentialGeneratorMDP:
    def __init__(
        self,
        csv_path: str,
        wordlist_path: str,
        username_length: int = 8,
        password_length: int = 12,
        use_username_chars: bool = True,
        use_username_nums: bool = True,
        use_username_symbols: bool = True,
        use_password_chars: bool = True,
        use_password_nums: bool = True,
        use_password_symbols: bool = True,
    ):
        try:
            self.web_text = load_web_text(csv_path)
            self.wordlists = load_wordlist(wordlist_path)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error loading input files: {e}")
            self.web_text = ""
            self.wordlists = []

        self.username_mdp = CredentialMDP(order=3)
        self.password_mdp = CredentialMDP(order=5)

        # Store user preferences
        self.username_length = username_length
        self.password_length = password_length
        self.use_username_chars = use_username_chars
        self.use_username_nums = use_username_nums
        self.use_username_symbols = use_username_symbols
        self.use_password_chars = use_password_chars
        self.use_password_nums = use_password_nums
        self.use_password_symbols = use_password_symbols

    def preprocess_text(self, text: str) -> List[str]:
        words = re.findall(r'[a-zA-Z0-9!@#$%^&*]+', text.lower())
        return [word for word in words if len(word) >= 4]

    def build_state_transitions(self):
        username_data = set(self.preprocess_text(self.web_text) + self.wordlists)
        password_data = set(word for word in username_data if len(word) >= 8)
        symbols = "!@#$%^&*"

        password_data |= {sym + word for word in password_data for sym in symbols}
        password_data |= {word + sym for word in password_data for sym in symbols}
        password_data |= {word[:i] + sym + word[i:] for word in password_data for i in range(1, len(word)) for sym in symbols}

        for word in username_data:
            for i in range(len(word) - self.username_mdp.order):
                state = f"username_{word[i:i+self.username_mdp.order]}"
                action = word[i+self.username_mdp.order]
                next_char = word[i+self.username_mdp.order]
                self.username_mdp.state_transitions[state][action].add(next_char)
                if i == 0:
                    self.username_mdp.initial_states.append(state)

        for word in password_data:
            for i in range(len(word) - self.password_mdp.order):
                state = f"password_{word[i:i+self.password_mdp.order]}"
                action = word[i+self.password_mdp.order]
                next_char = word[i+self.password_mdp.order]
                self.password_mdp.state_transitions[state][action].add(next_char)
                if i == 0:
                    self.password_mdp.initial_states.append(state)

    def generate_username(self) -> str:
        if not self.username_mdp.initial_states:
            state = f"username_{random.choice(self.wordlists)[:2]}"
        else:
            state = random.choice(self.username_mdp.initial_states)

        username = state[9:]
        allowed = ""
        if self.use_username_chars:
            allowed += "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if self.use_username_nums:
            allowed += "0123456789"
        if self.use_username_symbols:
            allowed += "!@#$%^&*"

        if not allowed:
            allowed = "user123"

        while len(username) < self.username_length:
            username += random.choice(allowed)

        return username

    def generate_password(self) -> str:
        if not self.password_mdp.initial_states:
            if self.wordlists:
                state = f"password_{random.choice(self.wordlists)[:3]}"
            else:
                state = "password_pa"
        else:
            state = random.choice(self.password_mdp.initial_states)

        password = state[9:]
        allowed = ""
        if self.use_password_chars:
            allowed += "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if self.use_password_nums:
            allowed += "0123456789"
        if self.use_password_symbols:
            allowed += "!@#$%^&*"

        if not allowed:
            allowed = "pass1234"

        while len(password) < self.password_length:
            password += random.choice(allowed)

        password = self.enhance_password(password)
        return password

    def enhance_password(self, password: str) -> str:
        symbols = "!@#$%^&*"
        words = re.findall(r'\b[a-zA-Z]{4,}\b', password)

        if self.use_password_symbols and not any(c in symbols for c in password):
            insert_pos = len(password) // 2
            password = password[:insert_pos] + random.choice(symbols) + password[insert_pos:]

        if self.use_password_nums and not any(c.isdigit() for c in password):
            insert_pos = len(password) - 1
            password = password[:insert_pos] + str(random.randint(0, 9)) + password[insert_pos:]

        if password and not password[0].isupper():
            password = password[0].upper() + password[1:]
        return password

    def generate_credentials(self, count: int = 10):
        self.build_state_transitions()
        credentials = {}
        for _ in range(count):
            username = self.generate_username() if self.wordlists else "user"
            password = self.generate_password()
            credentials[username] = password
        return credentials



