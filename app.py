# ============================ #
# 🔧 Import Required Libraries #
# ============================ #
import openai                        # For interacting with OpenAI's GPT models
import os                            # To access environment variables
import praw                          # Python Reddit API Wrapper for Reddit data
import panel as pn                   # Panel for building interactive web apps
from dotenv import load_dotenv, find_dotenv  # For loading environment variables from .env file
 
# ======================================= #
# 🔐 Load Environment Variables & API Key #
# ======================================= #
_ = load_dotenv(find_dotenv())                    # Load variables from .env file
openai.api_key = os.getenv('OPENAI_API_KEY')      # Set OpenAI API key
 
# =========================================== #
# 🌐 Initialize Panel App with Material Theme #
# =========================================== #
pn.extension(sizing_mode="stretch_width", template="material", title="TrendSage")
 
# ======================================== #
# 🧠 System Prompt: Define Chatbot Context #
# ======================================== #
context = [
    {'role': 'system', 'content': """
    You are Byte Me - TrendSage 🎛️, a witty, current, and insightful chatbot designed to keep users updated
    on digital trends, internet slang, meme culture, and digital etiquette.
 
    Your personality is friendly, chill, and vibey — but always informative. You help users:
    - Understand new digital trends, TikTok/IG crazes, and viral movements
    - Explain Gen Z or internet slang in plain terms
    - Decode memes and share their backstories
    - Offer guidance on how to behave online (DMs, ghosting, soft-launching, etc.)
    - Share advice on building digital presence and cleaning up digital footprints
 
    Avoid giving outdated or offline advice unless asked. Always aim to keep it light, clear, and up-to-date.
 
    You can use emojis for fun, but stay readable. Respond like the user’s cool, clued-in friend.
    If you are asked about anything outside the scope of TrendSage, gently say:
    "Oops, that's not really my vibe! I’m all about the latest trends, memes, and digital culture. Let’s stick to that!"
    DO NOT answer any questions that are unrelated to digital trends, internet slang, meme culture, and digital etiquette.
    """}
]
 
# ======================================== #
# 🎨 Define Custom CSS for UI Styling     #
# ======================================== #
css_style = """
<style>
body {
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    background: linear-gradient(to right, #FF80AB, #FF4081);
    margin: 0;
    padding: 0;
}
.bm-header {
    font-size: 28px;
    font-weight: bold;
    color: #6A1B9A;
    margin-bottom: 8px;
}
.bm-subheader {
    font-size: 16px;
    color: #555;
    margin-bottom: 16px;
}
.bm-button {
    background-color: #FF80AB;
    color: white;
    border-radius: 8px;
}
.bm-button:hover {
    background-color: #FF4081;
}
.bm-user {
    font-weight: bold;
    color: #1A237E;
}
.bm-bot {
    font-weight: bold;
    color: #388E3C;
}
.chat-box {
    background-color: #fafafa;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0px 0px 5px #ddd;
    margin-bottom: 10px;
}
.loading {
    font-size: 18px;
    color: #FF4081;
}
</style>
"""
 
# =========================== #
# 🔎 Set Up Reddit API Access #
# =========================== #
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)
 
# ======================================== #
# 🔥 Fetch Trending Posts from Reddit API #
# ======================================== #
def fetch_reddit_trends(subreddit_name="trending", limit=5):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        hot_posts = subreddit.hot(limit=limit)
        # Skip stickied posts (e.g., announcements) and format results
        trends = [f"- {post.title}" for post in hot_posts if not post.stickied]
        return "\n".join(trends) if trends else "No hot trends found right now."
    except Exception as e:
        return f"Oops! Couldn’t fetch Reddit trends: {str(e)}"
 
# =============================== #
# 🧾 Render Custom Header Layout #
# =============================== #
header = pn.pane.HTML(f"""
{css_style}
<div class='bm-header'>📲 Byte Me – TrendSage</div>
<div class='bm-subheader'>Your go-to digital bestie for the freshest trends, memes, slang, and social savvy 💬</div>
""", sizing_mode="stretch_width")
 
# ======================= #
# 💬 Chat UI Components   #
# ======================= #
conversation_pane = pn.Column()  # Main chat display area
 
# Conversation history panel (initially hidden)
history_pane = pn.Column(pn.pane.Markdown("### Conversation History 📜", styles={'font-size': '18px'}))
history_pane.visible = False
 
# ============================================= #
# 🧠 Function to Get Response from GPT Model     #
# ============================================= #
def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0.5):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]
 
# ============================================= #
# 💬 Handle User Input and Generate Chat Reply  #
# ============================================= #
def collect_messages(_):
    prompt = inp.value.strip()
    if not prompt:
        return
    inp.value = ''  # Clear input field
 
    # Show "thinking" status
    conversation_pane.append(pn.pane.Markdown("<div class='loading'>🤖 TrendSage is thinking...</div>", width=600))
 
    # Check if input mentions Reddit and fetch trends
    if "reddit" in prompt.lower():
        reddit_response = fetch_reddit_trends("popular")
        response = f"Here’s what's hot on Reddit right now:\n\n{reddit_response}"
        context.append({'role': 'user', 'content': prompt})
        context.append({'role': 'assistant', 'content': response})
    else:
        context.append({'role': 'user', 'content': prompt})
        response = get_completion_from_messages(context)
        context.append({'role': 'assistant', 'content': response})
 
    # Update chat display with the new conversation
    conversation_pane.clear()
    conversation_pane.append(pn.pane.Markdown(f"<div class='chat-box'><span class='bm-user'>🧍 You:</span> {prompt}</div>", width=600))
    conversation_pane.append(pn.pane.Markdown(f"<div class='chat-box'><span class='bm-bot'>🤖 TrendSage:</span> {response}</div>", width=600))
 
    # Update conversation history
    history_pane.clear()
    history_pane.append(pn.pane.Markdown("### Conversation History 📜", styles={'font-size': '18px'}))
    for msg in context[1:]:
        role = "🧍 You" if msg['role'] == 'user' else "🤖 TrendSage"
        history_pane.append(pn.pane.Markdown(f"<div class='chat-box'><b>{role}:</b> {msg['content']}</div>", width=600))
 
# ======================== #
# 🧩 Chat Controls & Layout #
# ======================== #
inp = pn.widgets.TextInput(value="", placeholder="Ask about trends, memes, or etiquette...", width=600)
 
button_convo = pn.widgets.Button(name="Ask TrendSage", button_type="primary", css_classes=["bm-button"], width=130, height=40)
button_history = pn.widgets.Button(name="Conversation History", button_type="light", css_classes=["bm-button"], width=170, height=40)
 
# 🔴 End Session Button
button_done = pn.widgets.Button(name="End Session", button_type="danger", width=100, height=40)
def close_chatbot(event):
    main_dashboard.clear()
    main_dashboard.append(pn.pane.Markdown("## 🙋 TrendSage signing off! Stay trendy and see you soon."))
    print("Chatbot closed.")  # Debug log
button_done.on_click(close_chatbot)
 
# Link button clicks to functions
button_convo.on_click(collect_messages)
 
# Toggle history visibility
def toggle_history(event):
    history_pane.visible = not history_pane.visible
    button_history.name = "Hide History" if history_pane.visible else "Conversation History"
button_history.on_click(toggle_history)
 
# ======================== #
# 🧱 Assemble Final Layout #
# ======================== #
chat_controls = pn.Row(
    inp,
    button_convo,
    button_history,
    button_done,
    align="center"
)
 
chat_area = pn.Column(
    conversation_pane,
    styles={'background-color': '#fff', 'padding': '20px', 'border-radius': '10px'}
)
 
main_dashboard = pn.Column(
    header,
    pn.Card(chat_controls, title="💬 Start Chatting", margin=(10, 5)),
    pn.Card(chat_area, title="📲 Conversation", styles={'background-color': '#FFFDE7'}),
    pn.Card(history_pane, title="🗂️ Chat History", styles={'background-color': '#E3F2FD'})
)
 
# =========================== #
# 🚀 Launch the Panel App     #
# =========================== #
pn.serve(main_dashboard, title="Byte Me - TrendSage 📲", port=5007, show=True)