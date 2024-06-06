import streamlit as st
from openai import OpenAI
import os
from PIL import Image
import base64
from io import BytesIO

# Set up OpenAI API key
openai_api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=openai_api_key)

# --- Page Config ---
st.set_page_config(
    page_title = "Construction Analyzer",
    page_icon = "🔎",
    menu_items = None
)

# Function to convert image file to base64
def get_image_base64(image_raw):
    buffered = BytesIO()
    image_raw.save(buffered, format=image_raw.format)
    img_byte = buffered.getvalue()

    return base64.b64encode(img_byte).decode('utf-8')

# Define a function to generate image description using GPT-4
# The dialog decorator creates a modal/popup for the function
@st.experimental_dialog("Image Analysis",width="large")
def generate_image_description(image_path, image):
    with st.spinner('Analyzing...'):
        # insert image
        st.image(image)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_path }
                    },
                    {
                        "type": "text",
                        "text": "Describe this image. Identify any areas of concern regarding workplace safety, specifying the description, location, priority, and applicable OSHA reference with a recommendation."
                    }
                ]
                }
            ],
            stream=True,
            temperature=0.5,
            max_tokens=4096
        )
        # Stream response from LLM
        st.write_stream(response)

# Define the Streamlit app
def main():
    st.title("OSHA Workplace Safety Analysis")

    with st.expander("See explanation"):
        st.write(
            "The Construction Analyzer app leverages the power of Streamlit and advanced machine learning to enhance workplace safety at construction sites. Users can upload images of construction sites, and the app employs a large language model (LLM) to analyze and compare these images against OSHA (Occupational Safety and Health Administration) guidelines. The app highlights potential safety concerns, providing an invaluable tool for construction managers and safety officers."
        )

    # Display the images
    images = [
        "https://raw.githubusercontent.com/ninja-skunk/streamlit/main/images/construction-stairs.jpeg",
        "https://raw.githubusercontent.com/ninja-skunk/streamlit/main/images/construction-electrical.jpeg",
        "https://raw.githubusercontent.com/ninja-skunk/streamlit/main/images/construction-piping.jpeg"
    ]

    cols = st.columns(len(images))
    for i, image_url in enumerate(images):
        select_image = ""
        select = 0
        with cols[i]:
            st.image(image_url, width=200)
            if st.button(f"Analyze Image {i+1}"):
                # image_path = image_url
                select = 1
        if select==1:
            description = generate_image_description(image_url, image_url)
   
    st.divider()
    #Allow user to upload their image
    uploaded_file = st.file_uploader("Choose an Image")
    if uploaded_file is not None:
        img_type = uploaded_file.type
        raw_img = Image.open(uploaded_file)
        img = get_image_base64(raw_img)

        img_url = f"data:{img_type};base64,{img}"
        generate_image_description(img_url, raw_img)

if __name__ == "__main__":
    main()
