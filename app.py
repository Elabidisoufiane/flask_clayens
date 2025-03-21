from langchain.schema import Document  # Ensure Document is imported
import os
from flask import Flask, request, jsonify
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain, LLMChain
from langchain import hub
from flask_cors import CORS  # Import CORS
import os
from twilio.rest import Client
# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for your app

# Set API key for Google Gemini
GOOGLE_API_KEY = "AIzaSyA188Jgn6lZTMBikEJ7LCUPHBpfvsV2nNI"  # Replace with your actual API key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Initialize Gemini LLM and embedding model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
embed_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key=GOOGLE_API_KEY)

# Load existing vector store
persist_directory = "persisted_db"
vector_store = Chroma(persist_directory=persist_directory, embedding_function=embed_model)

# Configure retriever
retriever = vector_store.as_retriever()

# Pull chat prompt template
retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

# Use `retrieval_qa_chat_prompt` directly (no need to convert it)
combine_docs_chain = LLMChain(llm=llm, prompt=retrieval_qa_chat_prompt)

# Create retrieval chain
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

@app.route('/get_defect_analysis', methods=['POST'])
def get_defect_analysis():
    try:
        data = request.json
        defect = data.get("defect")
        print("defect :",defect)
        if not defect:
            return jsonify({"error": "Missing 'defect' parameter"}), 400

        # Query the retrieval chain
        response = retrieval_chain.invoke(
            {"input": f"Provide probable causes and corresponding solution for each cause , this is the defect '{defect}' . Return only a JSON script in French and include just the causes that have relation with tempirature withe a variable indice : 11 , vitesse de vise indice : 17 , matiere indice 18 or mold indice 7. like this : cause , solution , indice. "}
        )

        # Log the entire response to check its structure
        response1=response['answer']
        response1text=response1['text']
        if '```json' in response1text:
            response1text = response1text.replace('```json', '').replace('```', '').strip()
            print("done hhhh")
            return response1text
        
        print(f"Response from retrieval chain: {response1['text']}")


        # Check if the response has a 'text' key and extract it
        if 'text' in response1:
            return response1['text']
        else:
            return jsonify({"error": "No 'text' found in response"}), 400

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/call', methods=['GET'])
def call():
        # Download the helper library from https://www.twilio.com/docs/python/install
    

    # Set environment variables for your credentials
    # Read more at http://twil.io/secure

    account_sid = "ACa8aca5271e0cdccf3b906f65c48e0ad8"
    auth_token = "eb375fe322c72a2090aa64e2d5807ea0"
    client = Client(account_sid, auth_token)

    call = client.calls.create(
    url="http://demo.twilio.com/docs/voice.xml",
    to="+212684992113",
    from_="+19564767521"
    )

    print(call.sid)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
