
import os
import re
import base64
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ==================================================
# 1. CONFIGURATION
# ==================================================

load_dotenv()

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o").strip()

st.set_page_config(
    page_title="VisionCraft AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# 2. AZURE AI CLIENT
# ==================================================

client = None

if ENDPOINT and API_KEY:
    try:
        BASE_URL = ENDPOINT.split("/responses")[0].rstrip("/") + "/"

        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY
        )
    except Exception as e:
        st.error(f"Azure client configuration error: {e}")

# ==================================================
# 3. PROFESSIONAL UI AND TEXT VISIBILITY
# ==================================================

st.markdown("""
<style>

/* Main application background */
.stApp {
    background: linear-gradient(135deg, #0b1020, #111b35);
    color: #f1f5f9;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Hero section */
.hero {
    padding: 28px;
    border: 1px solid #293b60;
    border-radius: 20px;
    background: linear-gradient(120deg, #172554, #172033);
    margin-bottom: 25px;
}

.hero h1 {
    color: #ffffff !important;
    font-size: 38px;
    margin-bottom: 8px;
}

.hero p {
    color: #cbd5e1 !important;
    font-size: 16px;
}

/* Chat message cards */
div[data-testid="stChatMessage"] {
    background-color: #172033;
    border: 1px solid #293b60;
    border-radius: 14px;
    padding: 12px;
}

/* Chat text */
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] h1,
div[data-testid="stChatMessage"] h2,
div[data-testid="stChatMessage"] h3 {
    color: #f1f5f9 !important;
}

/* Chat input container */
div[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border: 2px solid #60a5fa !important;
    border-radius: 14px !important;
}

/* User prompt text */
div[data-testid="stChatInput"] textarea {
    background-color: #ffffff !important;
    color: #111827 !important;
    caret-color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    opacity: 1 !important;
}

/* Chat placeholder */
div[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}

/* Image question and illustration prompt boxes */
.stTextArea textarea,
.stTextInput input {
    background-color: #ffffff !important;
    color: #111827 !important;
    caret-color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    opacity: 1 !important;
}

.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}

/* Labels */
.stTextArea label,
.stTextInput label,
.stFileUploader label {
    color: #e2e8f0 !important;
}

/* All regular buttons: visible without hover */
.stButton > button,
.stFormSubmitButton > button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    border: 1px solid #60a5fa !important;
    border-radius: 10px !important;
    min-height: 42px;
    opacity: 1 !important;
}

/* Button text */
.stButton > button *,
.stFormSubmitButton > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

/* Button hover */
.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #1d4ed8 !important;
    color: #ffffff !important;
    border-color: #93c5fd !important;
}

/* Download button */
.stDownloadButton > button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    border: 1px solid #60a5fa !important;
    border-radius: 10px !important;
}

.stDownloadButton > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #e2e8f0;
}

/* Radio buttons */
div[role="radiogroup"] label {
    color: #e2e8f0 !important;
}

/* General headings */
h1, h2, h3 {
    color: #f8fafc;
}

/* Info and warning messages */
div[data-testid="stAlert"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# 4. IMAGE CONVERSION
# ==================================================

def image_to_data_url(uploaded_file):
    image_bytes = uploaded_file.getvalue()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    extension = uploaded_file.name.rsplit(".", 1)[-1].lower()

    mime_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp"
    }

    mime_type = mime_types.get(extension, "image/png")

    return f"data:{mime_type};base64,{encoded_image}"


# ==================================================
# 5. SVG ILLUSTRATION GENERATION
# ==================================================

def generate_svg(prompt):
    instructions = """
    You are a professional SVG illustration generator.

    Create a complete, valid, visually attractive SVG
    illustration based on the user's prompt.

    Requirements:
    - Return ONLY raw SVG code.
    - Start with <svg and end with </svg>.
    - Use viewBox="0 0 800 600".
    - Include appropriate shapes, colors and details.
    - Use gradients, paths, circles and text where useful.
    - Do not use Markdown code fences.
    - Do not include explanations outside the SVG.
    - Produce a complete standalone SVG document.
    """

    try:
        response = client.responses.create(
            model=DEPLOYMENT,
            instructions=instructions,
            input=f"Create an SVG illustration of: {prompt}"
        )

        output = response.output_text or ""

        # Remove Markdown code fences if present
        output = re.sub(
            r"```(?:svg|xml|html)?",
            "",
            output,
            flags=re.IGNORECASE
        ).replace("```", "").strip()

        # Extract the SVG document
        match = re.search(
            r"<svg\b[\s\S]*?</svg\s*>",
            output,
            re.IGNORECASE
        )

        if match:
            return match.group(0)

        st.error("The AI did not return SVG code.")

        with st.expander("View AI response for debugging"):
            st.code(output or "Empty response")

        return None

    except Exception as e:
        st.error(f"Illustration generation failed: {e}")
        return None


# ==================================================
# 6. DISPLAY AND DOWNLOAD SVG
# ==================================================

def show_svg(svg_code):
    if not svg_code:
        return

    encoded_svg = base64.b64encode(
        svg_code.encode("utf-8")
    ).decode("utf-8")

    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            padding:18px;
            border-radius:16px;
            text-align:center;
        ">
            <img
                src="data:image/svg+xml;base64,{encoded_svg}"
                style="width:100%;max-width:800px;height:auto;"
                alt="Generated illustration"
            />
        </div>
        """,
        unsafe_allow_html=True
    )

    st.download_button(
        label="Download Illustration (SVG)",
        data=svg_code,
        file_name="visioncraft_illustration.svg",
        mime="image/svg+xml",
        use_container_width=True
    )


# ==================================================
# 7. IMAGE ANALYSIS
# ==================================================

def ask_about_image(prompt, uploaded_file):
    data_url = image_to_data_url(uploaded_file)

    response = client.responses.create(
        model=DEPLOYMENT,
        instructions="""
        You are VisionCraft AI, a professional visual assistant.

        Analyze the uploaded image carefully.
        Answer the user's question clearly and accurately.
        Describe visible objects, colors, composition,
        background and readable text when relevant.
        Do not invent details that cannot be seen.
        Reply in the language used by the user.
        """,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": data_url
                    }
                ]
            }
        ]
    )

    return response.output_text or "I could not generate a response."


# ==================================================
# 8. GENERAL AI CHAT
# ==================================================

def chat_with_ai(prompt, uploaded_file=None, history=None):
    input_messages = []

    # Include previous conversation for follow-up questions
    for message in (history or []):
        input_messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    # Current user message
    content = [
        {
            "type": "input_text",
            "text": prompt
        }
    ]

    if uploaded_file is not None:
        content.append({
            "type": "input_image",
            "image_url": image_to_data_url(uploaded_file)
        })

    input_messages.append({
        "role": "user",
        "content": content
    })

    response = client.responses.create(
        model=DEPLOYMENT,
        instructions="""
        You are VisionCraft AI, a helpful professional AI assistant.

        Understand the user's complete prompt and conversation.
        Answer questions, explain concepts, help with coding,
        brainstorm ideas, and analyze attached images.
        Use earlier conversation messages when answering follow-ups.
        Reply in the language used by the user.
        Be clear, accurate and helpful.
        """,
        input=input_messages
    )

    return response.output_text or "I could not generate a response."


# ==================================================
# 9. SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "generated_svg" not in st.session_state:
    st.session_state.generated_svg = None


# ==================================================
# 10. SIDEBAR
# ==================================================

with st.sidebar:
    st.title("🎨 VisionCraft AI")
    st.caption("Your visual AI assistant")

    mode = st.radio(
        "Choose a mode",
        [
            "AI Chat",
            "Describe an Image",
            "Generate Illustration"
        ]
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg", "webp"],
        help="Upload an image to ask questions about it."
    )

    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption=uploaded_file.name,
            use_container_width=True
        )

    st.divider()

    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.generated_svg = None
        st.rerun()

    st.caption("Powered by Azure AI")


# ==================================================
# 11. MAIN HEADER
# ==================================================

st.markdown("""
<div class="hero">
    <h1>VisionCraft AI ✨</h1>
    <p>
        Ask questions, understand images, and create
        custom vector illustrations with AI.
    </p>
</div>
""", unsafe_allow_html=True)

if client is None:
    st.error(
        "Azure AI is not configured. Check your .env file "
        "for AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY."
    )
    st.stop()


# ==================================================
# 12. GENERATE ILLUSTRATION MODE
# ==================================================

if mode == "Generate Illustration":
    st.subheader("Create an Illustration")

    st.write(
        "Describe what you want to create. "
        "Example: A cute robot in a colorful garden."
    )

    with st.form("illustration_form"):
        illustration_prompt = st.text_area(
            "Describe your illustration",
            placeholder=(
                "A futuristic electric car driving through "
                "a modern city at night..."
            ),
            height=120
        )

        generate_button = st.form_submit_button(
            "Generate Illustration",
            use_container_width=True
        )

    if generate_button:
        if not illustration_prompt.strip():
            st.warning("Please enter an illustration description.")
        else:
            with st.spinner("Creating your illustration..."):
                svg = generate_svg(illustration_prompt)

            if svg:
                st.session_state.generated_svg = svg

    if st.session_state.generated_svg:
        st.subheader("Your Illustration")
        show_svg(st.session_state.generated_svg)


# ==================================================
# 13. DESCRIBE IMAGE MODE
# ==================================================

elif mode == "Describe an Image":
    st.subheader("Understand Your Image")

    if uploaded_file is None:
        st.info("Upload an image from the sidebar to get started.")
    else:
        image_question = st.text_area(
            "What would you like to know about this image?",
            placeholder=(
                "Describe this image in detail, identify objects, "
                "or explain what is happening."
            ),
            height=100
        )

        if st.button("Analyze Image", use_container_width=True):
            question = image_question.strip()

            if not question:
                question = "Describe this image in detail."

            try:
                with st.spinner("Analyzing your image..."):
                    answer = ask_about_image(question, uploaded_file)

                st.subheader("AI Analysis")
                st.markdown(answer)

            except Exception as e:
                st.error(f"Image analysis failed: {e}")


# ==================================================
# 14. AI CHAT MODE
# ==================================================

elif mode == "AI Chat":
    st.subheader("Chat with VisionCraft")

    if uploaded_file is not None:
        st.caption(
            f"Attached image: {uploaded_file.name}. "
            "Ask a question about it below."
        )

    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask a question or describe what you need..."
    )

    if prompt:
        # Save current user prompt
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Do not send the current message twice
            history = st.session_state.messages[:-1]

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = chat_with_ai(
                        prompt,
                        uploaded_file,
                        history
                    )

                st.markdown(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:
            st.error(f"Chat failed: {e}")
