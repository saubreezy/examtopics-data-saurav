import streamlit as st
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import random

# Page configuration
st.set_page_config(
    page_title="Terraform Associate Exam Prep",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bookmark file path
BOOKMARK_FILE = Path(__file__).parent / "bookmark.json"

def save_bookmark(question_id: int) -> None:
    """Save the current question ID to bookmark file."""
    try:
        with open(BOOKMARK_FILE, 'w') as f:
            json.dump({"last_question_id": question_id}, f)
    except Exception:
        pass  # Silently fail if can't save

def load_bookmark() -> Optional[int]:
    """Load the last question ID from bookmark file."""
    try:
        if BOOKMARK_FILE.exists():
            with open(BOOKMARK_FILE, 'r') as f:
                data = json.load(f)
                return data.get("last_question_id")
    except Exception:
        pass
    return None

def find_question_index_by_id(questions: List[Dict[str, Any]], question_id: int) -> Optional[int]:
    """Find the index of a question by its question_id."""
    for idx, q in enumerate(questions):
        if q.get('question_id') == question_id:
            return idx
    return None

def load_all_questions() -> List[Dict[str, Any]]:
    """Load and parse all Terraform Associate JSON files."""
    base_path = Path(__file__).parent.parent / "Hashicorp"
    all_questions = []
    
    # Find all Terraform Associate files
    json_files = sorted(
        base_path.glob("Terraform-Associate_*.json"),
        key=lambda x: int(x.stem.split('_')[-1]) if x.stem.split('_')[-1].isdigit() else 0
    )
    
    if not json_files:
        return []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract questions from the nested structure
            questions = data.get('pageProps', {}).get('questions', [])
            
            for q in questions:
                # Add file source for reference
                q['source_file'] = json_file.name
                all_questions.append(q)
                
        except Exception as e:
            # Silently handle errors - will show in UI if needed
            pass
    
    return all_questions

@st.cache_data
def get_cached_questions() -> List[Dict[str, Any]]:
    """Cached version of load_all_questions."""
    return load_all_questions()

def format_question(question: Dict[str, Any], show_answer: bool = False) -> None:
    """Display a formatted question."""
    # Question header
    q_id = question.get('question_id', 'N/A')
    topic = question.get('topic', 'N/A')
    
    st.markdown(f"### Question #{q_id} (Topic: {topic})")
    
    # Question text
    question_text = question.get('question_text', '')
    st.markdown(f"**{question_text}**")
    
    st.markdown("---")
    
    # Choices
    choices = question.get('choices', {})
    if choices:
        st.markdown("#### Options:")
        for letter in sorted(choices.keys()):
            choice_text = choices[letter]
            # Highlight correct answer if showing
            if show_answer and letter == question.get('answer'):
                st.markdown(f"**{letter}.** {choice_text} ✅ **CORRECT**")
            else:
                st.markdown(f"**{letter}.** {choice_text}")
    
    # Answer section
    if show_answer:
        st.markdown("---")
        correct_answer = question.get('answer', 'N/A')
        answer_et = question.get('answer_ET', '')
        community_answers = question.get('answers_community', [])
        
        st.success(f"**Correct Answer: {correct_answer}**")
        
        if answer_et and answer_et != correct_answer:
            st.info(f"ExamTopics Answer: {answer_et}")
        
        if community_answers:
            st.markdown(f"**Community Consensus:** {', '.join(community_answers)}")
    
    # Discussion/Explanations
    discussion = question.get('discussion', [])
    if discussion and show_answer:
        st.markdown("---")
        st.markdown("#### 💬 Community Explanations")
        
        # Sort by upvotes (most helpful first)
        sorted_discussions = sorted(
            discussion,
            key=lambda x: int(x.get('upvote_count', 0)) if isinstance(x.get('upvote_count'), (int, str)) else 0,
            reverse=True
        )
        
        # Show top explanations
        top_explanations = sorted_discussions[:5]
        
        for idx, comment in enumerate(top_explanations, 1):
            content = comment.get('content', '')
            upvotes = comment.get('upvote_count', 0)
            poster = comment.get('poster', 'Anonymous')
            
            if content:
                with st.expander(f"💡 Explanation #{idx} ({upvotes} upvotes) by {poster}"):
                    st.markdown(content)
                    
                    # Show nested comments if any
                    nested = comment.get('comments', [])
                    if nested:
                        st.markdown("**Replies:**")
                        for reply in nested[:3]:  # Show top 3 replies
                            reply_content = reply.get('content', '')
                            reply_upvotes = reply.get('upvote_count', 0)
                            reply_poster = reply.get('poster', 'Anonymous')
                            if reply_content:
                                st.markdown(f"- **{reply_poster}** ({reply_upvotes} upvotes): {reply_content}")

def main():
    st.title("📚 HashiCorp Certified: Terraform Associate Exam Prep")
    st.markdown("---")
    
    # Initialize session state
    if 'questions' not in st.session_state:
        with st.spinner("Loading exam questions from JSON files..."):
            st.session_state.questions = get_cached_questions()
    
    questions = st.session_state.questions
    
    if not questions:
        st.error("No questions found! Please check the file path.")
        return
    
    # Initialize selected_idx - check for bookmark first
    if 'selected_idx' not in st.session_state:
        bookmark_id = load_bookmark()
        if bookmark_id:
            bookmark_idx = find_question_index_by_id(questions, bookmark_id)
            if bookmark_idx is not None:
                st.session_state.selected_idx = bookmark_idx
                st.info(f"📖 Resumed from Question #{bookmark_id}")
            else:
                st.session_state.selected_idx = 0
        else:
            st.session_state.selected_idx = 0
    
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    
    # Sidebar
    st.sidebar.title("Navigation")
    st.sidebar.info(f"**Total Questions:** {len(questions)}")
    
    # Bookmark section
    current_q_id = questions[st.session_state.selected_idx].get('question_id')
    bookmark_id = load_bookmark()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 Bookmark")
    
    if bookmark_id and bookmark_id == current_q_id:
        st.sidebar.success(f"📍 Bookmarked at Question #{bookmark_id}")
    elif bookmark_id:
        bookmark_idx = find_question_index_by_id(questions, bookmark_id)
        if bookmark_idx is not None:
            if st.sidebar.button(f"🔖 Go to Bookmark (Q#{bookmark_id})"):
                st.session_state.selected_idx = bookmark_idx
                st.session_state.show_answer = False
                st.rerun()
        else:
            st.sidebar.info("No bookmark saved")
    else:
        st.sidebar.info("No bookmark saved")
    
    # Question selection
    question_options = [f"Question {q.get('question_id', idx+1)}" for idx, q in enumerate(questions)]
    selected_display = st.sidebar.selectbox(
        "Select Question",
        range(len(questions)),
        index=st.session_state.selected_idx,
        format_func=lambda x: f"Question {questions[x].get('question_id', x+1)}"
    )
    
    # Update session state if selection changed and save bookmark
    if selected_display != st.session_state.selected_idx:
        st.session_state.selected_idx = selected_display
        st.session_state.show_answer = False
        # Save bookmark whenever position changes
        new_q_id = questions[selected_display].get('question_id')
        if new_q_id:
            save_bookmark(new_q_id)
    
    # Display options
    st.sidebar.markdown("---")
    show_answer = st.sidebar.checkbox("Show Answer", value=st.session_state.show_answer)
    if show_answer != st.session_state.show_answer:
        st.session_state.show_answer = show_answer
    
    # Search functionality
    st.sidebar.markdown("---")
    search_term = st.sidebar.text_input("🔍 Search Questions", "")
    
    # Filter questions if search term provided
    display_questions = questions
    if search_term:
        filtered = [
            q for q in questions
            if search_term.lower() in q.get('question_text', '').lower()
            or any(search_term.lower() in str(v).lower() for v in q.get('choices', {}).values())
        ]
        display_questions = filtered
        st.sidebar.info(f"Found {len(filtered)} matching questions")
        
        if filtered:
            filtered_idx = st.sidebar.selectbox(
                "Select from Results",
                range(len(filtered)),
                format_func=lambda x: f"Question {filtered[x].get('question_id', x+1)}"
            )
            current_question = filtered[filtered_idx]
        else:
            st.warning("No questions found matching your search.")
            return
    else:
        current_question = questions[st.session_state.selected_idx]
    
    # Save bookmark when navigating with buttons
    current_q_id = current_question.get('question_id')
    if current_q_id:
        save_bookmark(current_q_id)
    
    # Display current question
    format_question(
        current_question,
        show_answer=st.session_state.show_answer
    )
    
    # Navigation buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.selected_idx > 0:
            if st.button("◀ Previous"):
                st.session_state.selected_idx -= 1
                st.session_state.show_answer = False
                # Save bookmark
                new_q_id = questions[st.session_state.selected_idx].get('question_id')
                if new_q_id:
                    save_bookmark(new_q_id)
                st.rerun()
    
    with col2:
        if st.button("🔄 Toggle Answer"):
            st.session_state.show_answer = not st.session_state.show_answer
            st.rerun()
    
    with col3:
        if st.session_state.selected_idx < len(questions) - 1:
            if st.button("Next ▶"):
                st.session_state.selected_idx += 1
                st.session_state.show_answer = False
                # Save bookmark
                new_q_id = questions[st.session_state.selected_idx].get('question_id')
                if new_q_id:
                    save_bookmark(new_q_id)
                st.rerun()
    
    with col4:
        if st.button("🎲 Random Question"):
            st.session_state.selected_idx = random.randint(0, len(questions) - 1)
            st.session_state.show_answer = False
            # Save bookmark
            new_q_id = questions[st.session_state.selected_idx].get('question_id')
            if new_q_id:
                save_bookmark(new_q_id)
            st.rerun()
    
    # Question metadata
    with st.expander("📋 Question Metadata"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Question ID:** {current_question.get('question_id', 'N/A')}")
            st.markdown(f"**Topic:** {current_question.get('topic', 'N/A')}")
            st.markdown(f"**Source File:** {current_question.get('source_file', 'N/A')}")
        with col2:
            st.markdown(f"**Timestamp:** {current_question.get('timestamp', 'N/A')}")
            url = current_question.get('url', '')
            if url:
                st.markdown(f"**Discussion:** [View on ExamTopics]({url})")

if __name__ == "__main__":
    main()
