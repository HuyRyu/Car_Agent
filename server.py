import streamlit as st

from agent import CarAssistantAgent
from llama_index.llms.openai import OpenAI
from search_tool import BonBanhCarPrice
from query_tool import VnExpressTool
import openai
import os
st.title("Car Assistant")

openai.api_key = os.environ.get("OPENAI_API_KEY", "")
# Init chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    listed_price = VnExpressTool(tool_name="listed_price_car", 
                                  description="Cung cấp thông tin giá niêm yết của các mẫu xe hơi hiện tại ở Việt Nam",
                                  collection_name="vnexpress_car_listed_price")
    info_detail = VnExpressTool(tool_name="car_info_detail", 
                                    description="Cung cấp mô tả và đánh giá chi tiết của các mẫu xe hơi hiện tại ở Việt Nam",
                                    collection_name="vnexpress_car_info_detail")
    technical_detail = VnExpressTool(tool_name="car_technical_detail", 
                                        description="Cung cấp thông số kỹ thuật của các mẫu xe hơi hiện tại ở Việt Nam",
                                        collection_name="vnexpress_car_technical_detail")
    car_inventory_tool = VnExpressTool(tool_name="car_inventory",
                                      description="Cung cấp danh sách xe của một thương hiệu xe hơi hiện tại ở Việt Nam",
                                      collection_name="vnexpress_car_inventory")

    car_type_tool = VnExpressTool(tool_name="car_type",
                                      description="Cung cấp danh sách các loại xe hơi hiện cho một kiểu xe hơi cụ thể (SUV, Sedan, Hatchback, ...) ở Việt Nam",
                                      collection_name="vnexpress_car_type")      

    old_car_price = BonBanhCarPrice()


    llm_model = "gpt-4o-mini"
    llm = OpenAI(model=llm_model)

    st.session_state["agent"] = CarAssistantAgent([listed_price.tool, info_detail.tool, technical_detail.tool, old_car_price.tool, car_type_tool.tool, car_type_tool.tool], llm=llm, verbose=True)


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
prompt = st.chat_input("what is up?")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = st.session_state["agent"](prompt)
        message_placeholder.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
