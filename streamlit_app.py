import streamlit as st
from openai import OpenAI
import os
from PIL import Image
import base64
from io import BytesIO

# Set up OpenAI API key from Streamlit's secrets management
openai_api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=openai_api_key)

# Configure the page's appearance and settings
st.set_page_config(
    page_title = "Construction Analyzer",
    page_icon = "🔎",
    menu_items = None
)

# Function to convert an image file to base64 format for inline display
def get_image_base64(image_raw):
    buffered = BytesIO()
    image_raw.save(buffered, format=image_raw.format)
    img_byte = buffered.getvalue()

    return base64.b64encode(img_byte).decode('utf-8')

# Function to generate a detailed description of an image using GPT-4
# This includes creating a modal dialog to display results
@st.experimental_dialog("Image Analysis",width="large")
def generate_image_description(image_path, image):
    with st.spinner('Analyzing...'):
        # Display the image in the modal
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
        # Stream the generated descriptions to the page
        st.write_stream(response)

# Main function defining the structure of the Streamlit app
def main():
    st.title("OSHA Workplace Safety Analysis")

    with st.expander("See explanation"):
        st.write(
            "Our new web application, which is powered by Streamlit, machine learning, and artificial intelligence is here to help keep construction sites safer. With the OSHA Workplace Safety Analysis, anyone from construction managers to safety officers to employees can upload photos of their sites. The web application uses a large language model (LLM) to check these photos against OSHA guidelines and highlights any safety red flags."
        )

    # Display predefined images with the option to analyze each
    images = [
        "https://raw.githubusercontent.com/Shaan-Duggal/streamlit_osha/main/images/construction-stairs.jpeg",
        "https://raw.githubusercontent.com/Shaan-Duggal/streamlit_osha/main/images/construction-electrical.jpeg",
        "https://raw.githubusercontent.com/Shaan-Duggal/streamlit_osha/main/images/construction-piping.jpeg"
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
    # Allow users to upload their own image for analysis
    uploaded_file = st.file_uploader("Choose an Image")
    if uploaded_file is not None:
        img_type = uploaded_file.type
        raw_img = Image.open(uploaded_file)
        img = get_image_base64(raw_img)

        img_url = f"data:{img_type};base64,{img}"
        generate_image_description(img_url, raw_img)

if __name__ == "__main__":
    main()

