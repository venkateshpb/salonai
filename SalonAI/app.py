from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('helpdesk.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    conn = get_db()
    pending = conn.execute('''
        SELECT MIN(id) as id, question, COUNT(*) as count, 
               MAX(timestamp) as last_asked
        FROM help_requests 
        WHERE status='pending'
        GROUP BY question
        ORDER BY last_asked DESC
    ''').fetchall()
    
    recent = conn.execute('''
        SELECT question, answer 
        FROM knowledge_base 
        ORDER BY timestamp DESC 
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    return render_template('supervisor.html', 
                         pending_questions=pending,
                         recent_answers=recent)

@app.route('/resolve', methods=['POST'])
def resolve():
    conn = get_db()
    try:
        question = conn.execute(
            'SELECT question FROM help_requests WHERE id = ?', 
            (request.form['id'],)
        ).fetchone()['question']
        
        conn.execute('''
            INSERT OR REPLACE INTO knowledge_base (question, answer)
            VALUES (?, ?)
        ''', (question, request.form['answer']))
        
        conn.execute('''
            UPDATE help_requests 
            SET status='resolved' 
            WHERE question = ? AND status='pending'
        ''', (question,))
        
        conn.commit()
        return jsonify(success=True)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)