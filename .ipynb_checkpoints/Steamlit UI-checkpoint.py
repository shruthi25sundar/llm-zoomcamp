{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "18c0daf0-ebd4-4112-99d3-f931f7207c32",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2024-07-07 15:02:20.869 \n",
      "  \u001b[33m\u001b[1mWarning:\u001b[0m to view this Streamlit app on a browser, run it with the following\n",
      "  command:\n",
      "\n",
      "    streamlit run /home/codespace/.local/share/virtualenvs/llm-zoomcamp-B9pnCD16/lib/python3.10/site-packages/ipykernel_launcher.py [ARGUMENTS]\n",
      "2024-07-07 15:02:20.870 Session state does not function when running a script without `streamlit run`\n"
     ]
    }
   ],
   "source": [
    "import streamlit as st\n",
    "import time\n",
    "\n",
    "from elasticsearch import Elasticsearch\n",
    "from openai import OpenAI\n",
    "\n",
    "client = OpenAI(\n",
    "    base_url='http://localhost:11434/v1/',\n",
    "    api_key='ollama',\n",
    ")\n",
    "\n",
    "es_client = Elasticsearch('http://localhost:9200') \n",
    "\n",
    "\n",
    "def elastic_search(query, index_name = \"course-questions\"):\n",
    "    search_query = {\n",
    "        \"size\": 5,\n",
    "        \"query\": {\n",
    "            \"bool\": {\n",
    "                \"must\": {\n",
    "                    \"multi_match\": {\n",
    "                        \"query\": query,\n",
    "                        \"fields\": [\"question^3\", \"text\", \"section\"],\n",
    "                        \"type\": \"best_fields\"\n",
    "                    }\n",
    "                },\n",
    "                \"filter\": {\n",
    "                    \"term\": {\n",
    "                        \"course\": \"data-engineering-zoomcamp\"\n",
    "                    }\n",
    "                }\n",
    "            }\n",
    "        }\n",
    "    }\n",
    "\n",
    "    response = es_client.search(index=index_name, body=search_query)\n",
    "    \n",
    "    result_docs = []\n",
    "    \n",
    "    for hit in response['hits']['hits']:\n",
    "        result_docs.append(hit['_source'])\n",
    "    \n",
    "    return result_docs\n",
    "\n",
    "\n",
    "def build_prompt(query, search_results):\n",
    "    prompt_template = \"\"\"\n",
    "You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.\n",
    "Use only the facts from the CONTEXT when answering the QUESTION.\n",
    "\n",
    "QUESTION: {question}\n",
    "\n",
    "CONTEXT: \n",
    "{context}\n",
    "\"\"\".strip()\n",
    "\n",
    "    context = \"\"\n",
    "    \n",
    "    for doc in search_results:\n",
    "        context = context + f\"section: {doc['section']}\\nquestion: {doc['question']}\\nanswer: {doc['text']}\\n\\n\"\n",
    "    \n",
    "    prompt = prompt_template.format(question=query, context=context).strip()\n",
    "    return prompt\n",
    "\n",
    "def llm(prompt):\n",
    "    response = client.chat.completions.create(\n",
    "        model='phi3',\n",
    "        messages=[{\"role\": \"user\", \"content\": prompt}]\n",
    "    )\n",
    "    \n",
    "    return response.choices[0].message.content\n",
    "\n",
    "\n",
    "def rag(query):\n",
    "    search_results = elastic_search(query)\n",
    "    prompt = build_prompt(query, search_results)\n",
    "    answer = llm(prompt)\n",
    "    return answer\n",
    "\n",
    "\n",
    "def main():\n",
    "    st.title(\"RAG Function Invocation\")\n",
    "\n",
    "    user_input = st.text_input(\"Enter your input:\")\n",
    "\n",
    "    if st.button(\"Ask\"):\n",
    "        with st.spinner('Processing...'):\n",
    "            output = rag(user_input)\n",
    "            st.success(\"Completed!\")\n",
    "            st.write(output)\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    main()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.13"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
