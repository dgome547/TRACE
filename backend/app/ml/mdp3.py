

import random
import re
from collections import defaultdict
import numpy as np
from typing import Dict, List, Tuple, Set
import csv
import os
import time
import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from urllib.parse import urlparse
from AI_Wordlist import AIWordlist

# Artificial Intelligence (AI) Subroutine:
# 2.	The development team shall evaluate and modify, as necessary the following aspects of the AI subroutine:
# 2.1.	Review and modify the order parameters current values to further optimize the generation of viable passwords
# 2.2.	assess whether the state transitions capture sufficient context for meaningful credential generation
# 2.3.	Evaluate and modify the calculate_password_strength method's weights.
# 2.4.	Evaluate and modify the calculate_username_quality method's weights.
# 2.5.	Review and modify the following learning parameters:
# 2.5.1.	Epsilon value (Currently .1, deals with exploration-exploitation balance)
# 2.5.2.	Learning rate (Currently .1, deals with Q-value updates)
# 2.5.3.	Gamma Factor (Currently .9, deals with future reward considerations)
# 2.6.	Improve the algorithm to dynamically heighten rewards given to states or actions that place approved special characters in positions deemed as important.
# 2.7.	The MDP algorithm shall incorporate a distinct symbol state in order to determine which special characters will be selected for the username/password generation.

# Web Scraping Subroutine:
# 3.	The Web Scraping subroutine shall be updated to perform the following
# 3.1.	The system shall organize URLs into a hierarchy tree structure to facilitate structured exploration, enabling efficient parallel processing and CSV generation.
# 3.2.	The scraper algorithm shall be modified to extract all words associated with logos, labels and class titles.
# 3.3.	The scraper algorithm shall be modified to perform batch processing in order to increase the efficiency.
# 3.4.	The web scraper shall leverage aiohttp in order to parallelize web scraping.

# Natural Language Processing (NLP) Subroutine:
# 4.	THE NLP subroutine shall be updated to perform the following:
# 4.1.	The NLP algorithm shall normalize all text in its output by removing non-english characters and resolving encoding issues.
# 4.2.	The NLP algorithm shall break up compound words (ex. sister-in-law -> sister,in,law)
# 4.3.	The NLP algorithm shall remove all definite articles, Demonstrative Determiners, Distributive Determiners and Interrogative Determiners from the text leveraging a NLP algorithm.
# 4.4.	The NLP algorithm shall remove all words less than 4 characters long unless the word is determined to be an acronym.
# 4.5.	The NLP algorithm shall remove all instances of possessive determiners except for those determined to be as part of a technological name or user role/name




#Natural Language Processing routine that cleans CSV text
# 4.1.	The NLP algorithm shall normalize all text in its output by removing non-english characters and resolving encoding issues. 
def normalize_text(text):
    # Remove non-English characters and resolve encoding issues
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    text = text.encode('ascii', errors='ignore').decode('utf-8')  # Normalize encoding
    return text

# 4.2.	The NLP algorithm shall break up compound words (ex. sister-in-law -> sister,in,law)
def split_compound_words(text):
    # Split compound words using regex
    return re.sub(r'-', ',', text)

# 4.4.	The NLP algorithm shall remove all words less than 4 characters long unless the word is determined to be an acronym.
def filter_words(words, stopwords, acronyms):
    # Remove words less than 4 characters (except acronyms)
    filtered_words = []
    for word in words:
        if len(word) >= 4 or word.upper() in acronyms:
            filtered_words.append(word)
    return filtered_words

# 4.3.	The NLP algorithm shall remove all definite articles, Demonstrative Determiners, Distributive Determiners and Interrogative Determiners from the text leveraging a NLP algorithm.
def remove_specific_determiners(words):
    # Define lists of determiners to remove
    definite_articles = {"the"}
    demonstrative_determiners = {"this", "that", "these", "those"}
    distributive_determiners = {"each", "every", "either", "neither"}
    interrogative_determiners = {"which", "what", "whose"}
    # 4.5.	The NLP algorithm shall remove all instances of possessive determiners except for those determined to be as part of a technological name or user role/name
    possessive_determiners = {"my", "your", "his", "her", "its", "our", "their"}
    
    all_determiners = (definite_articles | demonstrative_determiners |
                       distributive_determiners | interrogative_determiners)
    
    cleaned_words = [word for word in words if word.lower() not in all_determiners]
    return cleaned_words

def nlp_subroutine(csv_path: str):
    stopwords = {"and", "or"}  # Additional stopwords
    acronyms = {"AI", "NLP", "USA"}  # Example acronyms
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    cleaned_rows = []
    with open(csv_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames or not {"id", "content", "url"}.issubset(fieldnames):
            raise ValueError("CSV must contain columns: id, content, url")
        
        for row in reader:
            text = row["content"] if row["content"] else ""
            
            # Apply normalization
            text = normalize_text(text)
            
            # Split compound words
            text = split_compound_words(text)
            
            # Tokenize text
            words = re.findall(r'\w+', text, flags=re.IGNORECASE)
            
            # Remove specified determiners
            words = remove_specific_determiners(words)
            
            # Filter words based on length and acronyms
            words = filter_words(words, stopwords, acronyms)
            
            cleaned_text = " ".join(words)
            row["content"] = cleaned_text
            cleaned_rows.append(row)
    
    # Overwrite original CSV with cleaned text
    with open(csv_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)
    
    print(f"Cleaned CSV '{csv_path}' file has been updated successfully.")


#Load URLs from a CSV file with columns 'id' and 'website'.
def load_urls_from_csv(csv_path: str) -> List[str]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    try:
        urls = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if not {'id', 'website'}.issubset(set(reader.fieldnames or [])):
                raise ValueError("CSV must contain columns: id, website")
            for row in reader:
                if row['website']:
                    urls.append(row['website'].strip())
        return urls
    except csv.Error as e:
        raise ValueError(f"Error reading CSV file: {e}")

#Web scraper functions and will pull something out of the URLs provided.
class WebScraper:
    def __init__(self, urls):
        self.urls = urls
        self.hierarchy = self.organize_urls(urls)
        
# 3.1.	The system shall organize URLs into a hierarchy tree structure to facilitate structured exploration, enabling efficient parallel processing and CSV generation.
    def organize_urls(self, urls):
        # Group URLs by domain into a hierarchy
        hierarchy = defaultdict(list)
        for url in urls:
            domain = urlparse(url).netloc
            hierarchy[domain].append(url)
        return hierarchy

    async def fetch_page(self, session, url):
        try:
            # 3.4.	The web scraper shall leverage aiohttp in order to parallelize web scraping.
            async with session.get(url, timeout=10) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Extract text from p, h1, h2, h3, span tags
                text = ' '.join([tag.get_text() for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'span'])])

                # Extract words from logos, labels, and class titles
                # 3.2.	The scraper algorithm shall be modified to extract all words associated with logos, labels and class titles.
                logo_text = ' '.join([tag['alt'] for tag in soup.find_all('img', alt=True)])
                label_text = ' '.join([tag.get_text() for tag in soup.find_all('label')])
                class_text = ' '.join([tag['class'][0] for tag in soup.find_all(class_=True) if tag.get('class')])

                # Combine extracted text
                combined_text = f"{text} {logo_text} {label_text} {class_text}"
                return url, combined_text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return url, ""

# 3.3.	The scraper algorithm shall be modified to perform batch processing in order to increase the efficiency.
    async def scrape_pages(self):
        results = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_page(session, url) for url in self.urls]
            responses = await asyncio.gather(*tasks)
            for i, (url, content) in enumerate(responses, 1):
                results.append((i, content, url))
        return results

    def generate_csv(self, filename):
        # Run the asynchronous scraping process
        data = asyncio.run(self.scrape_pages())
        
        # Write results to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['id', 'content', 'url'])  # CSV header
            csv_writer.writerows(data)

        print(f"CSV file '{filename}' has been generated successfully.")


    # Load web text from a CSV file
def load_web_text(csv_path: str) -> str:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if not {'id', 'content', 'url'}.issubset(set(reader.fieldnames or [])):
                raise ValueError("CSV must contain columns: id, content, url")
            contents = []
            for row in reader:
                if row['content']:
                    contents.append(row['content'].lower())
        return " ".join(contents)
    except csv.Error as e:
        raise ValueError(f"Error reading CSV file: {e}")

# Load wordlist from a file
def load_wordlist(file_path: str) -> List[str]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Wordlist file not found: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            words = [line.strip().lower() for line in file if line.strip()]
        return words
    except Exception as e:
        raise ValueError(f"Error reading wordlist file: {e}")




# Class for managing the Markov Decision Process for generating credentials
# 2.5.3. Gamma Factor (Currently .9, deals with future reward considerations)
# - Keeps focus on near-future character contributions, especially important since passwords/usernames are relatively short sequences.
class CredentialMDP:
    def __init__(self, order: int = 4, gamma: float = 0.8):
        self.order = order
        self.gamma = gamma
        self.q_values: Dict[str, Dict[Tuple[str, str], float]] = defaultdict(lambda: defaultdict(float))
        self.state_transitions: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        self.used_usernames: Set[str] = set()

        # 2.5.	Review and modify the following learning parameters:
        # 2.5.1. Epsilon value (Currently .1, deals with exploration-exploitation balance)
        # Epsilon Decay (Exploration Decay):
        # - Early in learning: you want more exploration.
        # - Later on: you want to exploit the best-known paths.
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.99

        # 2.5.2.	Learning rate (Currently .1, deals with Q-value updates)
        # - Makes Q-values more responsive to useful paths and good transitions.
        self.learning_rate = 0.3
        self.initial_states: List[str] = []

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            self.epsilon = max(self.epsilon, self.epsilon_min)

    # Calculate the strength of a password
    # 2.3. Evaluate and modify the calculate_password_strength method's weights.
    # - Added partial credit for passwords between 8–11 characters.
    # - Increased the weight for unique characters to reward entropy more.
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

    # Calculate the quality of a username
    # 2.4. Evaluate and modify the calculate_username_quality method's weights.
    # - Introduced partial score for usernames ≥ 5 (in case some are short)
    # - Promotes slightly longer, more meaningful usernames while still allowing short ones.
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

    # Get the reward for a state-action pair
    def get_reward(self, state: str, action: str, next_char: str) -> float:
        if 'username' in state:
            current = state[9:] + next_char
            return self.calculate_username_quality(current) / len(current)
        else:
            current = state[9:] + next_char
            return self.calculate_password_strength(current) / len(current)

    # Get possible actions for a state
    def get_possible_actions(self, state: str) -> List[str]:
        return list(self.state_transitions[state].keys())

    # Choose an action based on epsilon-greedy strategy
    def choose_action(self, state: str) -> Tuple[str, str]:
        possible_actions = self.get_possible_actions(state)
        if not possible_actions:
            return "", ""

        if random.random() < self.epsilon:
            action = random.choice(possible_actions)
            next_char = random.choice(list(self.state_transitions[state][action]))
        else:
            # Choose best action based on Q-values
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

    # Update Q-value based on the Bellman equation
    def update_q_value(self, state: str, action: str, next_char: str, next_state: str, reward: float):
        next_action_values = []
        for next_action in self.get_possible_actions(next_state):
            for next_next_char in self.state_transitions[next_state][next_action]:
                next_action_values.append(self.q_values[next_state][(next_action, next_next_char)])

        max_next_q = max(next_action_values, default=0)
        current_q = self.q_values[state][(action, next_char)]
        new_q = current_q + self.learning_rate * (reward + self.gamma * max_next_q - current_q)
        self.q_values[state][(action, next_char)] = new_q

# Class for generating credentials using Markov Decision Process
class CredentialGeneratorMDP:
    def __init__(self, csv_path: str, wordlist_path: str):
        try:
            self.web_text = load_web_text(csv_path)
            self.wordlists = load_wordlist(wordlist_path)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error loading input files: {e}")
            self.web_text = csv_path
            self.wordlists = wordlist_path

        # 2.1 Review and modify the order parameters current values to further optimize the generation of viable passwords
        # If order = 2, the state is built from the last 2 characters of the string.
        # Before username(order=2): Less context taken and more randomness
        # After username(order=3): More readable and structured usernames, while still allowing some variety
        # Before password(order=3): Not enough to structure strong enough passwords
        # After password(order=5): Preservers meaningful substrings and generate more secure passwords
        self.username_mdp = CredentialMDP(order=3)
        self.password_mdp = CredentialMDP(order=5)
        self.min_username_length = 5
        self.min_password_length = 10

    # Preprocess text data
    def preprocess_text(self, text: str) -> List[str]:
        words = re.findall(r'\w+', text.lower())
        return [word for word in words if len(word) >= 4]

    # Build state transitions for username and password generation
    # 2.2. assess whether the state transitions capture sufficient context for meaningful credential generation
    # build_state_transitions function learns transitions from:
    # - Cleaned web text (real-world content from scraped sites)
    # - A curated wordlist (known terms like "secure", "login", etc.)
    # That’s a solid training base — it ensures transitions aren’t random noise but learned from domain-relevant sources.
    def build_state_transitions(self):
        username_data = set(self.preprocess_text(self.web_text) + self.wordlists)
        password_data = set(word for word in username_data if len(word) >= 8)

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

    # Generate a username and password pair
    def generate_credential(self) -> Dict[str, str]:
        # Generate username
        if not self.username_mdp.initial_states:
            state = f"username_{random.choice(self.wordlists)[:2]}"
        else:
            state = random.choice(self.username_mdp.initial_states)

        username = state[9:]
        while len(username) < self.min_username_length:
            action, next_char = self.username_mdp.choose_action(state)
            if not action or not next_char:
                break
            username += next_char
            next_state = f"username_{username[-self.username_mdp.order:]}"
            reward = self.username_mdp.get_reward(state, action, next_char)
            self.username_mdp.update_q_value(state, action, next_char, next_state, reward)
            state = next_state
            self.username_mdp.decay_epsilon()

        username = f"{username}{random.randint(1, 999)}"
        self.username_mdp.used_usernames.add(username)

        # Generate password
        if not self.password_mdp.initial_states:
            state = f"password_{random.choice(self.wordlists)[:3]}"
        else:
            state = random.choice(self.password_mdp.initial_states)

        password = state[9:]
        while len(password) < self.min_password_length:
            action, next_char = self.password_mdp.choose_action(state)
            if not action or not next_char:
                break
            password += next_char
            next_state = f"password_{password[-self.password_mdp.order:]}"
            reward = self.password_mdp.get_reward(state, action, next_char)
            self.password_mdp.update_q_value(state, action, next_char, next_state, reward)
            state = next_state
            self.password_mdp.decay_epsilon()

        password = self.enhance_password(password)
        return username, password

    # Enhance the generated password
    def enhance_password(self, password: str) -> str:
        enhanced = password.capitalize()
        enhanced = f"{enhanced}{random.choice('!@#$%^&*')}{random.randint(0, 9)}"
        return enhanced

    # Generate multiple credentials
    def generate_credentials(self, count: int = 10) -> Dict[str, str]:
        self.build_state_transitions()
        credentials = {}
        for _ in range(count):
            username, password = self.generate_credential()
            credentials[username] = password
        return credentials

# Main function to run the credential generation process
def main():
    # File paths
    site_list_csv_path = "site_list.csv"
    csv_path = "web_text.csv"
    wordlist_path = "wordlist.txt"
    credentials_csv_path = "storage/generated_credentials.csv"

    # Load URLs from the CSV file
    urls = load_urls_from_csv(site_list_csv_path)

    scraper = WebScraper(urls)
    scraper.generate_csv(csv_path)

    #Use NLP routine to clean CSV file
    nlp_subroutine(csv_path)
    
    try:
        generator = CredentialGeneratorMDP(csv_path, wordlist_path)
        credentials = generator.generate_credentials(15)

        wordlist_manager = AIWordlist(credentials_csv_path)
        wordlist_manager.save_credentials_to_csv(credentials)
        wordlist_manager.display_credentials(credentials)

        #print("\nGenerated Credentials:")
        #for username, password in credentials:
        #    print(f"Username: {username}, Password: {password}")
    except Exception as e:
        print(f"Error generating credentials: {e}")

if __name__ == "__main__":
    main()








