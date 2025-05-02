# Salon AI: Human-in-the-Loop System
An AI receptionist that intelligently escalates unknown questions to human supervisors and learns from their responses.

## ✨ Features
- **Smart AI Agent**: Handles common customer queries via console
- **Real-Time Supervisor Dashboard**: Web interface for answering questions
- **Self-Learning**: Automatically updates knowledge base
- **Activity Tracking**: Logs all interactions with timestamps

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git (optional)

```bash
# Clone the repository
git clone https://github.com/venkateshpb/salon-ai.git
cd salon-ai

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from agent import SalonAgent; SalonAgent()"
