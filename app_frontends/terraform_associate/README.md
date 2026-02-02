# HashiCorp Certified: Terraform Associate Exam Prep - Streamlit App

An interactive web application to help you study for the HashiCorp Certified: Terraform Associate exam.

## Features

- 📚 **All JSON files loaded automatically** - Parses all exam questions from the Hashicorp folder
- 🔍 **Search functionality** - Search questions by text or keywords
- ✅ **Show/Hide answers** - Practice mode with toggleable answers
- 💬 **Community explanations** - View top-rated explanations from ExamTopics discussions
- 🎲 **Random question** - Study random questions for better practice
- 📊 **Navigation** - Easy navigation between questions
- 📋 **Question metadata** - View question IDs, topics, and links to discussions
- 📖 **Bookmark feature** - Automatically saves your progress and resumes where you left off

## Setup

1. Install dependencies:
```bash
pip install streamlit
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## Usage

- **Select a question** from the sidebar dropdown
- **Search** for specific topics or keywords
- **Toggle answers** to practice without seeing solutions
- **View explanations** from the community (sorted by upvotes)
- **Navigate** using Previous/Next buttons or jump to a random question
- **Bookmark** - Your position is automatically saved as you navigate. When you return, the app will resume from your last question. Use the "Go to Bookmark" button in the sidebar to jump back to your saved position.

## File Structure

```
terraform_associate/
├── app.py              # Main Streamlit application
├── README.md           # This file
└── bookmark.json       # Auto-generated bookmark file (saves your progress)
```

The app reads JSON files from the `../Hashicorp/` directory relative to this folder. The `bookmark.json` file is automatically created to save your last position.
