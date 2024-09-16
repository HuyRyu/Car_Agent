import openai
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb
from llama_index.core import PromptTemplate
from llama_index.core.tools import QueryEngineTool, ToolMetadata, RetrieverTool


class VnExpressTool:
    def __init__(self, tool_name, description: str="", storage_path: str='./chroma_db', collection_name: str="vnexpress_car_info", llm_model: str="gpt-4o-mini", topk: int=5) -> None:
        self.__llm = OpenAI(model=llm_model)
        self.__tool_name = tool_name
        self.__description = description
        self.__topk = topk
        self.tool = self._create_vector_tool(storage_path, collection_name)

    def _create_vector_index(self, storage_path: str, collection_name: str):
        # initialize client, setting path to save data
        db = chromadb.PersistentClient(path=storage_path)
        # create collection
        chroma_collection = db.get_or_create_collection(collection_name)

        # assign chroma as the vector_store to the context
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
    
    def _create_vector_tool(self, storage_path: str, collection_name: str):
        vector_index = self._create_vector_index(storage_path, collection_name)
        text_qa_template_str = (
                                "Bạn là một chuyên gia về xe hơi và bạn được yêu cầu trả lời một số câu hỏi bằng tiếng Việt dựa trên thông tin dưới đây:"
                                "\n---------------------\n{context_str}\n---------------------\n"
                                " Dựa trên thông tin trên và kiến thức của bạn, hãy trả lời câu hỏi: {query_str}\n"
                                " Nếu thông tin trên không đủ, bạn cũng có thể tự trả lời câu hỏi. Câu trả lời phải là tiếng Việt (Vietnamese)\n"
                            )
        text_qa_template = PromptTemplate(text_qa_template_str)
        retriever = vector_index.as_retriever(text_qa_template=text_qa_template, llm=self.__llm, topk=self.__topk)
        return RetrieverTool(
                                retriever=retriever,
                                metadata=ToolMetadata(
                                    name=self.__tool_name,
                                    description=(
                                        self.__description
                                    ),
                                ),
                            )