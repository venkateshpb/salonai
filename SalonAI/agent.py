import sqlite3
from difflib import get_close_matches
from datetime import datetime

class SalonAgent:
    def __init__(self):
        self.knowledge_base = {
            "hours": "We're open 9AM-5PM daily",
            "pricing": "Haircuts start at $30",
            "appointments": "Book online at salon.com"
        }
        self._init_db()
        self._setup_keywords()
        self.last_checked = datetime.now().isoformat()
    
    def _init_db(self):
        self.conn = sqlite3.connect('helpdesk.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS help_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                status TEXT DEFAULT 'pending',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                question TEXT PRIMARY KEY,
                answer TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self._load_knowledge_base()
        self.conn.commit()

    def _load_knowledge_base(self):
        self.cursor.execute("SELECT question, answer FROM knowledge_base")
        for q, a in self.cursor.fetchall():
            self.knowledge_base[q] = a

    def _setup_keywords(self):
        self.keywords = {
            'hour': 'hours', 'open': 'hours', 'close': 'hours',
            'price': 'pricing', 'cost': 'pricing', 'book': 'appointments'
        }

    def _clean_question(self, question):
        question = question.lower().strip(' ?')
        stop_words = ['what', 'are', 'your', 'how', 'for', 'the']
        return ' '.join(word for word in question.split() if word not in stop_words)

    def _fuzzy_match(self, question):
        if question in self.knowledge_base:
            return self.knowledge_base[question]
        
        for word in question.split():
            if word in self.keywords:
                return self.knowledge_base[self.keywords[word]]
        
        matches = get_close_matches(question, self.knowledge_base.keys(), n=1, cutoff=0.6)
        return self.knowledge_base[matches[0]] if matches else None

    def _escalate_to_supervisor(self, question):
        self.cursor.execute(
            "INSERT INTO help_requests (question) VALUES (?)",
            (question,)
        )
        self.conn.commit()
        print(f"\n[SUPERVISOR ALERT] Logged: '{question}'\n")

    def check_resolved_questions(self):
        self.cursor.execute('''
            SELECT k.question, k.answer 
            FROM knowledge_base k
            JOIN help_requests h ON k.question = h.question
            WHERE h.status = 'resolved'
            AND k.timestamp > ?
        ''', (self.last_checked,))
        
        for q, a in self.cursor.fetchall():
            if q not in self.knowledge_base:
                self.knowledge_base[q] = a
                print(f"\n[LEARNED] New response: {q} → {a}\n")
        
        self.last_checked = datetime.now().isoformat()

    def handle_call(self, question):
        if len(question.strip()) < 3:
            return "Could you please rephrase that?"
            
        clean_q = self._clean_question(question)
        response = self._fuzzy_match(clean_q)
        
        if response:
            return response
            
        self._escalate_to_supervisor(question)
        return "Let me check with my supervisor..."

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    agent = SalonAgent()
    print("Salon AI Agent (type 'quit' to exit)")
    
    try:
        while True:
            agent.check_resolved_questions()
            user_input = input("\nCustomer question: ").strip()
            
            if user_input.lower() == 'quit':
                break
                
            print("Agent:", agent.handle_call(user_input))
    finally:
        agent.close()